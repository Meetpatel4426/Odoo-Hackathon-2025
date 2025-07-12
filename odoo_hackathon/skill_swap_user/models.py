# skill_swap_user/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    location = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    current_profession = models.CharField(max_length=100, blank=True)
    skills_offered = models.TextField(blank=True)
    skills_required = models.TextField(blank=True)
    availability = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.first_name} ({self.user.email})"
