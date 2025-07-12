from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationFormStep1, RegistrationFormStep2, LoginForm, OptionalDetailsForm
from .models import UserProfile


# Step 1: Register view (multi-step)
def register_view(request):
    step = request.POST.get("step", "1")
    
    if request.method == 'POST' and step == "1":
        form = RegistrationFormStep1(request.POST)
        if form.is_valid():
            request.session['register_data'] = form.cleaned_data
            return render(request, 'skill_swap_user/register_step2.html', {
                'form': RegistrationFormStep2(),
            })
    elif request.method == 'POST' and step == "2":
        session_data = request.session.get('register_data')
        if not session_data:
            return redirect('register')

        form = RegistrationFormStep2(request.POST)
        if form.is_valid() or request.POST.get('skip'):  # Allow skip
            try:
                user = User.objects.create_user(
                    username=session_data['email'],
                    email=session_data['email'],
                    password=session_data['password'],
                    first_name=session_data['name'],
                )
                # Save optional data if not skipped
                if not request.POST.get('skip'):
                    profile = UserProfile.objects.create(
                        user=user,
                        location=form.cleaned_data.get('location', ''),
                        phone_number=form.cleaned_data.get('phone_number', ''),
                        current_profession=form.cleaned_data.get('current_profession', ''),
                        skills_offered=form.cleaned_data.get('skills_offered', ''),
                        skills_required=form.cleaned_data.get('skills_required', ''),
                        availability=form.cleaned_data.get('availability', ''),
                    )
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Error creating account: {e}")
                return redirect('register')
    else:
        form = RegistrationFormStep1()

    return render(request, 'skill_swap_user/register.html', {
        'form': form
    })


# Login View
def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('profile')
        else:
            error = "Invalid email or password"
    return render(request, 'skill_swap_user/login.html', {'error': error})


# Forgot Password View (Placeholder)
def forgot_password_view(request):
    return render(request, 'skill_swap_user/forgot_password.html')


# Profile View (Login required)
@login_required
def profile_view(request):
    profile = None
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        pass
    return render(request, 'skill_swap_user/profile.html', {
        'user': request.user,
        'profile': profile
    })
