from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/admin/", include("accounts.urls_admin")),
    path("api/", include("learning.urls")),
    path("api/", include("enrollment.urls")),
]
