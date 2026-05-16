from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count
from django.utils.crypto import get_random_string
from .models import Enrollment, Review, Certificate
from .serializers import EnrollmentSerializer, ReviewSerializer, CertificateSerializer
from learning.models import LearningPath


class EnrollmentListView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related("learning_path")


class EnrollmentCreateView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer

    def create(self, request, *args, **kwargs):
        path_id = request.data.get("learning_path")
        if not path_id:
            return Response({"error": "learning_path is required"}, status=status.HTTP_400_BAD_REQUEST)
        if Enrollment.objects.filter(user=request.user, learning_path_id=path_id).exists():
            return Response({"error": "Already enrolled"}, status=status.HTTP_400_BAD_REQUEST)
        path = LearningPath.objects.get(id=path_id)
        enrollment = Enrollment.objects.create(user=request.user, learning_path=path)
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EnrollmentProgressView(generics.RetrieveAPIView):
    serializer_class = EnrollmentSerializer

    def get_object(self):
        return Enrollment.objects.get(
            user=self.request.user,
            learning_path_id=self.kwargs["path_id"],
        )


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer

    def create(self, request, *args, **kwargs):
        path_id = kwargs.get("path_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment", "")
        if not rating:
            return Response({"error": "rating is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not path_id:
            return Response({"error": "path_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        review, created = Review.objects.get_or_create(
            user=request.user, learning_path_id=path_id,
            defaults={"rating": rating, "comment": comment},
        )
        if not created:
            review.rating = rating
            review.comment = comment
            review.save()
        serializer = self.get_serializer(review)
        return Response(serializer.data)


class ReviewDetailView(generics.RetrieveAPIView):
    serializer_class = ReviewSerializer

    def get_object(self):
        return Review.objects.get(
            user=self.request.user,
            learning_path_id=self.kwargs["path_id"],
        )


class CertificateDetailView(generics.RetrieveAPIView):
    serializer_class = CertificateSerializer

    def get_object(self):
        path_id = self.kwargs["path_id"]
        enrollment = Enrollment.objects.get(user=self.request.user, learning_path_id=path_id)
        if not enrollment.is_completed:
            raise permissions.exceptions.PermissionDenied("Path not completed yet")
        cert, _ = Certificate.objects.get_or_create(
            user=self.request.user, learning_path_id=path_id,
            defaults={"certificate_id": get_random_string(16).upper()},
        )
        if not cert.certificate_id:
            cert.certificate_id = get_random_string(16).upper()
            cert.save()
        return cert
