import datetime
import json
import os

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
import zipfile
import io


from django.shortcuts import get_object_or_404

from reconprocess.filterset import ReconFilter
from reconprocess.models import FileData, ReconTask, ReconResult
from reconprocess.serializers import SourceTargetSerializer, ReconTaskSerializer, ReportSerializer, \
    ReconFilterSerializer

import pandas as pd

from reconprocess.utils import data_normalization, PerformRecon, ReportGenerator
from rest_framework.exceptions import ValidationError


class ReconViewSet(ViewSet):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=ReconFilterSerializer,
        responses={200: {

        }}
    )
    def list(self, request):
        """
        Handles the GET request for listing ReconResults, with filtering.
        """
        queryset = ReconTask.objects.all()  # Get the base queryset

        filterset = ReconFilter(request.GET, queryset=queryset)  # Apply the filter
        if filterset.is_valid():
            queryset = filterset.qs  # Get the filtered queryset

        serializer = ReconTaskSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)




    @extend_schema(
        request=SourceTargetSerializer,
        responses={201: {

        }},
    )
    def create(self, request):
        """
        Handle file uploads
        takes a source and target
        This api is limited to csv files

        both files should have the same name and number of columns
        Columns expected include;
        transaction Id
amount(debit and credit)
date
details for transactions

        """
        source_file = request.FILES.get('source_file')
        target_file = request.FILES.get('target_file')
        use_gemini = request.data.get("use_gemini", False)

        if not source_file or not target_file:
            return Response({'error': 'Source and target files are required.'}, status=status.HTTP_400_BAD_REQUEST)


        if not source_file.content_type == "text/csv"  or not target_file.content_type == "text/csv":
            return Response({'error': 'Invalid file type.'}, status=status.HTTP_400_BAD_REQUEST)


        try:
            # store files in disk  and generate a path for reference
            source_file_instance = FileData.objects.create(file=source_file)
            target_file_instance = FileData.objects.create(file=target_file)


            #  instantiate recon process
            recon_task = ReconTask.objects.create(
                source_file=source_file_instance,
                target_file=target_file_instance,
            )



            # use pandas to read files
            source_df = pd.read_csv(source_file_instance.file.path)
            target_df = pd.read_csv(target_file_instance.file.path)
            #
            # print(source_df)

            # normalize data
            normalize_source = data_normalization(source_df)
            normalize_target = data_normalization(target_df)

            # print(normalize_target)

            # instantiate the Recon class  and pass our normalized data
            recon = PerformRecon(normalize_source, normalize_target)

            if use_gemini:
                gemini_results= recon.detect_discrepancies_using_gemini()
                results = ReconResult.objects.create(
                    task=recon_task,
                    gemini_recon_result={
                        "records":gemini_results.to_json(orient="records")
                    },

                    gemini_generated=True
                )
            else:


                missing_data_in_source = recon.missing_in_target_and_in_source()
                missing_data_in_target = recon.missing_in_source_and_in_target()

                discrepancies = recon.discrepancies()

                #
                #
                # print(
                #     type(missing_data_in_source),
                #     "mds",
                #     type(missing_data_in_target),
                #     "mdt",
                #     type(discrepancies),
                #     "dc"
                # )

                # print(missing_data_in_target.to_json(orient="records"))


                #store my recon results
                results = ReconResult.objects.create(
                    task=recon_task,
                    missing_source={
                        "records":missing_data_in_source.to_json(orient="records")
                    },
                    missing_target=
                    {
                        "records": missing_data_in_target.to_json(orient="records")
                    },
                    discrepancies=
                    {
                        "records":discrepancies.to_json(orient="records"),

                    }
                )


            recon_task.status = 'completed'
            recon_task.end_time = datetime.datetime.now()
            recon_task.save()

            results.save()

            serializer = ReconTaskSerializer(recon_task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            recon_task.status = 'failed'
            recon_task.error={'error': str(e), status:status.HTTP_400_BAD_REQUEST}
            recon_task.save()
            return Response({'error': str(e), "message": "The process has been saved with a status -failed"}, status=status.HTTP_400_BAD_REQUEST)




    @extend_schema(
            request=ReportSerializer,
    responses = {200: {

    }}
    )
    def generate_report(self, request):
        """
        Generate reconciliation report based on the file type -
    This api is limited to 3 types csv, json, html

        """
        try:
            serializer = ReportSerializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                recon_task = get_object_or_404(ReconTask,
                                               id=serializer.validated_data["report_task_id"])
                if not recon_task:
                    raise ValidationError("Reconciliation task not found.")

                # retrieve recon result
                reports = ReconResult.objects.filter(task=recon_task).first()

                if not reports:
                    raise ValidationError("No reports available, the reconciliation might have failed")



                results = {
                    "missing_records_in_source": reports.missing_source,
                    "missing_records_in_target": reports.missing_target,
                    "discrepancies": reports.discrepancies
                }

                if reports.gemini_generated:
                    results={
                        "discrepancies":reports.gemini_recon_result
                    }



                report_generator = ReportGenerator(serializer.validated_data["report_type"],
                                                   results)  # Access validated data

                if serializer.validated_data["report_type"] == "CSV":  # Access validated data
                    report_data = report_generator.to_csv()  #
                    content_type = "text/csv"  #
                    filename = "reconciliation_report.csv"


                elif serializer.validated_data["report_type"] == "JSON":
                    report_data = report_generator.to_json()
                    content_type = "application/json"
                    filename = "reconciliation_report.json"


                elif serializer.validated_data["report_type"] == "HTML":
                    report_data = report_generator.to_html()
                    content_type = "text/html"
                    filename = "reconciliation_report.html"


                else:
                    return Response(
                        {"error": "Invalid report type"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                response = Response(report_data, content_type=content_type)
                response["Content-Disposition"] = f'attachment; filename="{filename}"'
                return response

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # More specific error code





