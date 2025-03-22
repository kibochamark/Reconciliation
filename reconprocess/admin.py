from django.contrib import admin

from reconprocess.models import FileData, ReconTask, ReconResult

# Register your models here.
admin.site.register(FileData)
admin.site.register(ReconTask)
admin.site.register(ReconResult)
