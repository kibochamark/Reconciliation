from random import choices

from rest_framework import  serializers

from reconprocess.models import FileData, ReconResult, ReconTask


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model =FileData
        fields=["file"]




class FileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileData
        fields = '__all__'

class ReconResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconResult
        fields = '__all__'


class ReconTaskSerializer(serializers.ModelSerializer):
    source_file = FileDataSerializer(read_only=True)
    target_file = FileDataSerializer(read_only=True)

    class Meta:
        model = ReconTask
        fields = '__all__'




class SourceTargetSerializer(serializers.Serializer):
    source_file = FileDataSerializer(write_only=True)
    target_file = FileDataSerializer(write_only=True)
    use_gemini = serializers.BooleanField(write_only=True)


class ReportSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=[('CSV', 'csv'), ('HTML', 'html'), ('JSON', 'json')])
    report_task_id = serializers.IntegerField()


    required_fields=['report_type', 'report_task_id']



class ReconFilterSerializer(serializers.Serializer):
    created_at = serializers.DateField()
    status = serializers.ChoiceField(choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], required=False)


