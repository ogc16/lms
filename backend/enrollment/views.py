from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Count
from .models import Enrollment
from .serializers import EnrollmentSerializer
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
