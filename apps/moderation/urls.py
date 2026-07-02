from django.urls import path
from .apis import ReportContentApi, ModerationQueueApi, ResolveReportApi

app_name = "moderation"

urlpatterns = [
    path("report/", ReportContentApi.as_view(), name="report"),
    path("queue/", ModerationQueueApi.as_view(), name="queue"),
    path("reports/<uuid:id>/resolve/", ResolveReportApi.as_view(), name="resolve-report"),
]
