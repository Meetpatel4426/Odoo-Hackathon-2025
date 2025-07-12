<<<<<<< HEAD
# odoo_hackathon/skill_swap_user/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset/<uidb64>/<token>/', views.reset_password_confirm, name='password_reset_confirm'),
    path('logout/', views.logout_view, name='logout'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Search public users by skill
    path('search/', views.search_users, name='search_users'),

    # Swap Requests
    path('send-request/<int:receiver_id>/', views.send_swap_request, name='send_swap_request'),
    path('requests/', views.manage_requests, name='manage_requests'),
    path('requests/<int:request_id>/<str:action>/', views.update_request_status, name='update_request_status'),

    # Feedback
    path('feedback/<int:swap_id>/', views.leave_feedback, name='leave_feedback'),
]
=======
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('profile/', views.profile_view, name='profile'),
]
>>>>>>> 50e51de (added media visiblity)
