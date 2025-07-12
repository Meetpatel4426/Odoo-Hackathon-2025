# skill_swap_user/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser, UserDetails
from .forms import RegistrationFormStep1, RegistrationFormStep2, LoginForm
from django.contrib.auth.decorators import login_required

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
        if form.is_valid() or request.POST.get('skip'):
            try:
                user = CustomUser.objects.create(
                    name=session_data['name'],
                    email=session_data['email'],
                    password=make_password(session_data['password']),
                )
                if not request.POST.get('skip'):
                    UserDetails.objects.create(
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

    return render(request, 'skill_swap_user/register.html', {'form': form})


def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id  # Manual login via session
                return redirect('profile')
            else:
                error = "Invalid credentials"
        except CustomUser.DoesNotExist:
            error = "Invalid credentials"

    return render(request, 'skill_swap_user/login.html', {'error': error})


def forgot_password_view(request):
    return render(request, 'skill_swap_user/forgot_password.html')


def profile_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    try:
        user = CustomUser.objects.get(id=user_id)
        profile = getattr(user, 'details', None)
    except CustomUser.DoesNotExist:
        return redirect('login')

    return render(request, 'skill_swap_user/profile.html', {
        'user': user,
        'profile': profile
    })
