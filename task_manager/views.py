from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets, decorators, permissions, status
from rest_framework.response import Response

from .serializers import TaskSerializer
from .models import Task

USER_MODEL = get_user_model()


# Create your views here.
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return Task.objects.all().filter(Q(owner=self.request.user) | Q(access_list=self.request.user))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @decorators.detail_route(methods=['POST',])
    def share(self, request, pk):
        task = self.get_object()
        username = request.POST['username']

        try:
            access_user = USER_MODEL.objects.get(email=username)
        except USER_MODEL.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        task.access_list.add(access_user)
        task.save()
        return Response({'detail': 'user was added'})


