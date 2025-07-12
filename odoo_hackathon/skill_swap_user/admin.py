from django.contrib import admin
from .models import CustomUser, UserDetails

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email')
    search_fields = ('name', 'email')
    ordering = ('id',)

@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'location', 'current_profession')
    search_fields = ('user__email', 'location', 'current_profession')