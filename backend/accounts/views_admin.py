from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer


class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminVerifyInstructorView(generics.UpdateAPIView):
    queryset = User.objects.filter(role=User.Role.INSTRUCTOR)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_verified = True
        user.save()
        return Response(UserSerializer(user).data)
