from django.db import models
from django.conf import settings

# Create your models here.

class Habit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    reminder_enabled = models.BooleanField(default=False)
    reminder_time = models.TimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"