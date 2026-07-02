from django.urls import path
from .apis import GlobalSearchApi

app_name = "search"

urlpatterns = [
    path("", GlobalSearchApi.as_view(), name="global-search"),
]
