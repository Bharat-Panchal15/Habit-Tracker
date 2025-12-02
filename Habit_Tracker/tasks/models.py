from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('done','Done'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    habit = models.ForeignKey("habits.Habit",on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)
    description = models.TextField()
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.description} - {self.date}"