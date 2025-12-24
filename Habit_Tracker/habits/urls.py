from django.urls import path, include
from rest_framework.routers import DefaultRouter
from habits.views import HabitViewSet


router = DefaultRouter()
router.register('habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]