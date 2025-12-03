from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class User(AbstractUser):
    email = models.EmailField(blank=True, null=True)
    is_guest = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    @property
    def is_guest_expired(self):
        if not self.is_guest:
            return False
        
        expiry_date = self.created_on + timedelta(days=7)
        return timezone.now().date() > expiry_date
    
    @property
    def guest_days_left(self):
        if not self.is_guest:
            return None
        
        expiry_date = self.created_on + timedelta(days=7)
        remaining = expiry_date - timezone.now().date()
        return max(remaining.days, 0)