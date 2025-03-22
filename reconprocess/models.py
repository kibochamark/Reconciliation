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

