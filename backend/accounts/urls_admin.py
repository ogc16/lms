from django.urls import path
from . import views_admin

urlpatterns = [
    path("users/", views_admin.AdminUserListView.as_view(), name="admin-users"),
    path("instructors/<int:pk>/verify/", views_admin.AdminVerifyInstructorView.as_view(), name="admin-verify-instructor"),
]
