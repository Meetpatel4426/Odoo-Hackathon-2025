from django.urls import path
from . import views

urlpatterns = [
    path('profile_page', views.profile_page, name='profile_page'),
]
