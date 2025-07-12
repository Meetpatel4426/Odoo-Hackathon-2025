# skill_swap_user/models.py
from django.db import models

class CustomUser(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)  # Store hashed passwords later

    def __str__(self):
        return f"{self.name} ({self.email})"

class UserDetails(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='details')
    location = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    current_profession = models.CharField(max_length=100, blank=True)
    skills_offered = models.TextField(blank=True)
    skills_required = models.TextField(blank=True)
    availability = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Details of {self.user.email}"
