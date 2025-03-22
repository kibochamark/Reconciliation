import datetime
import json

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


from reconprocess.models import FileData, ReconTask, ReconResult
from reconprocess.serializers import SourceTargetSerializer, ReconTaskSerializer, ReportSerializer

import pandas as pd

from reconprocess.utils import data_normalization, PerformRecon, ReportGenerator


class ReconViewSet(ViewSet):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=SourceTargetSerializer,
        responses={201: {

        }},
    )
    def create(self, request):
        source_file = request.FILES.get('source_file')
        target_file = request.FILES.get('target_file')

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

            missing_data_in_source = recon.missing_in_source()
            missing_data_in_target = recon.missing_in_target()

            discrepancies = recon.discrepancies()



            print(
                type(missing_data_in_source),
                "mds",
                type(missing_data_in_target),
                "mdt",
                type(discrepancies),
                "dc"
            )

            print(missing_data_in_target.to_json(orient="records"))


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
            results.save()

            #
            # results_json = {
            #     'missing_source': missing_data_in_source,
            #     'missing_target': missing_data_in_target,
            #     'discrepancies': discrepancies,
            # }
            #
            #
            # recon_task.results_json = results_json
            recon_task.status = 'completed'
            recon_task.end_time = datetime.datetime.now()
            recon_task.save()
            #
            # # Generate CSV and HTML files
            # csv_content = pd.DataFrame(results_json['missing_source']).to_csv(index=False)
            # html_content = pd.DataFrame(results_json['missing_source']).to_html()
            #
            # csv_file_path = os.path.join(settings.MEDIA_ROOT, f'results_{recon_task.id}.csv')
            # html_file_path = os.path.join(settings.MEDIA_ROOT, f'results_{recon_task.id}.html')
            #
            # default_storage.save(csv_file_path, ContentFile(csv_content))
            # default_storage.save(html_file_path, ContentFile(html_content))
            #
            # recon_task.results_csv_path = csv_file_path
            # recon_task.results_html_path = html_file_path
            # recon_task.save()
            #
            serializer = ReconTaskSerializer(recon_task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            recon_task.status = 'failed'
            recon_task.error={'error': str(e), status:status.HTTP_400_BAD_REQUEST}
            recon_task.save()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




    @extend_schema(
            request=ReportSerializer,
    responses = {200: {

    }}
    )
    def generate_report(self, request):

        serializer_class = ReportSerializer(request.data)

        if serializer_class.is_valid(raise_exception=True):
            reports =get_object_or_404(ReconResult, id=request.data["report_id"])

        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

        # instantiate report generator
        
        
        reportGenertor= ReportGenerator()
