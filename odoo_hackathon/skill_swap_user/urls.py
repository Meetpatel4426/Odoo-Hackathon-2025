# odoo_hackathon/skill_swap_user/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset/<uidb64>/<token>/', views.reset_password_confirm, name='password_reset_confirm'),
    path('logout/', views.logout_view, name='logout'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Skill Search (public profiles only)
    path('search/', views.search_users, name='search_users'),

    # Swap Requests
    path('send-request/<int:user_id>/', views.send_swap_request, name='send_swap_request'),  # New: send to specific user
    path('requests/', views.manage_requests, name='manage_requests'),
    path('requests/<int:request_id>/<str:action>/', views.update_request_status, name='update_request_status'),

    # Feedback after swap
    path('feedback/<int:swap_id>/', views.leave_feedback, name='leave_feedback'),
    path('chat/<int:swap_id>/', views.chat_view, name='chat'),
    path('chat/<int:swap_id>/api/', views.chat_messages_api, name='chat_messages_api'),

]
