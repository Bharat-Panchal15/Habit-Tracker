from django.db import models

# Create your models here.

class StreakRecord(models.Model):
    habit = models.OneToOneField("habits.Habit", on_delete=models.CASCADE, related_name="streak_record")
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_completed_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Streak for {self.habit.title}: {self.current_streak} days"