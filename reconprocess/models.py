from django.db import models
import os

class FileData(models.Model):
    file = models.FileField(upload_to='recon_files/') # Store files in a directory

    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.filename()

class ReconTask(models.Model):
    source_file = models.ForeignKey(FileData, on_delete=models.CASCADE, related_name='source_tasks')
    target_file = models.ForeignKey(FileData, on_delete=models.CASCADE, related_name='target_tasks')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')


    errors= models.JSONField(null=True, blank=True)


    created_at=models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Recon Task {self.id} - {self.status}"

class ReconResult(models.Model):
    task = models.ForeignKey(ReconTask, on_delete=models.CASCADE, related_name='results')
    missing_source = models.JSONField(null=True, blank=True)
    missing_target = models.JSONField(null=True, blank=True)
    discrepancies = models.JSONField(null=True, blank=True)


    created_at=models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Results for Task {self.task.id}"

    def save_dataframe_to_jsonfield(df, jsonfield_instance, field_name):
        """
        Converts a Pandas DataFrame to a JSON string and saves it to a JSONField.

        Args:
            df (pd.DataFrame): The DataFrame to convert.
            jsonfield_instance: An instance of the model containing the JSONField
                               (e.g., an instance of ReconResult).
            field_name (str): The name of the JSONField in the model
                              (e.g., 'missing_source', 'discrepancies').
        """
        json_data = df.to_json(orient='records')
        setattr(jsonfield_instance, field_name, json.loads(json_data))
        jsonfield_instance.save()  # Save the model instance