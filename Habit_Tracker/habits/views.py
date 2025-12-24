from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from habits.serializers import HabitSerializer
from habits.models import Habit
# Create your views here.

class HabitViewSet(ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Habit.objects.filter(user=self.request.user)

        if self.action == "reactivate":
            return queryset
        return queryset.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        habit = self.get_object()

        if not habit.is_active:
            return Response({"detail": "Inactive habits cannot be modified"}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        habit = self.get_object()
        habit.is_active = False
        habit.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        habit = self.get_object()

        if habit.is_active:
            return Response({"detail": "Habit is already active"}, status=status.HTTP_400_BAD_REQUEST)
        
        habit.is_active = True
        habit.end_date = request.data.get('end_date')
        habit.save(update_fields=['is_active','end_date'])

        return Response(HabitSerializer(habit).data, status=status.HTTP_200_OK)