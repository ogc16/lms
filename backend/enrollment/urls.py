from django.urls import path
from . import views

urlpatterns = [
    path("enrollments/", views.EnrollmentListView.as_view(), name="enrollment-list"),
    path("enrollments/create/", views.EnrollmentCreateView.as_view(), name="enrollment-create"),
    path("enrollments/<int:path_id>/progress/", views.EnrollmentProgressView.as_view(), name="enrollment-progress"),
]
