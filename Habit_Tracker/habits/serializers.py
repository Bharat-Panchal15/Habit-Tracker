from rest_framework import serializers
from habits.models import Habit

class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ["id","title","description","created_on","end_date","reminder_enabled","reminder_time","is_active"]
        read_only_fields = ["id","created_on", "is_active"]