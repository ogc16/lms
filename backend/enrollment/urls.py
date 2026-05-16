from django.urls import path
from . import views

urlpatterns = [
    path("enrollments/", views.EnrollmentListView.as_view(), name="enrollment-list"),
    path("enrollments/create/", views.EnrollmentCreateView.as_view(), name="enrollment-create"),
    path("enrollments/<int:path_id>/progress/", views.EnrollmentProgressView.as_view(), name="enrollment-progress"),
    path("paths/<int:path_id>/review/", views.ReviewCreateView.as_view(), name="path-review"),
    path("paths/<int:path_id>/review/detail/", views.ReviewDetailView.as_view(), name="path-review-detail"),
    path("paths/<int:path_id>/certificate/", views.CertificateDetailView.as_view(), name="path-certificate"),
]
