# odoo_hackathon/skill_swap_user/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Step 1: Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

# Step 2: Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'                    # for login
    REQUIRED_FIELDS = ['name']                  # for createsuperuser

    def __str__(self):
        return self.email

# Step 3: Additional Profile Data
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
