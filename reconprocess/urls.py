from django.urls import path

from reconprocess.views import ReconViewSet

urlpatterns=[
        path("upload", ReconViewSet.as_view({
                'post':"create"
        })),
        path("generate_report", ReconViewSet.as_view({
                'post':"generate_report"
        })),
        path("ltasks", ReconViewSet.as_view({
                'get':"list"
        }))
]