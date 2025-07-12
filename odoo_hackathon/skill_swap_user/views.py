# skill_swap_user/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser, UserDetails
from .forms import RegistrationFormStep1, RegistrationFormStep2, LoginForm
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password

from .models import CustomUser
from .utils import password_reset_token

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

def reset_password_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and password_reset_token.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
            elif len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
            else:
                user.password = make_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset. You can now log in.")
                return redirect('login')

        return render(request, 'skill_swap_user/reset_password.html', {
            'uidb64': uidb64,
            'token': token
        })
    else:
        return render(request, 'skill_swap_user/password_reset_invalid.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token.make_token(user)

            subject = "Reset Your SkillSwap Password"
            from_email = None  # or settings.DEFAULT_FROM_EMAIL
            to_email = user.email

            html_content = render_to_string("skill_swap_user/password_reset_email.html", {
                'user': user,
                'uid': uid,
                'token': token,
                'domain': request.get_host(),
            })

            email_message = EmailMultiAlternatives(subject, "", from_email, [to_email])
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

            messages.success(request, "A password reset link has been sent to your email.")
        except CustomUser.DoesNotExist:
            messages.error(request, "This email is not registered. Please create an account.")
            return redirect('register')

    return render(request, 'skill_swap_user/forgot_password.html')


def profile_view(request):
    # Assuming you're storing user ID in session after login
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('login')

    # Try to get UserDetails if available
    try:
        profile = UserDetails.objects.get(user=user)
    except UserDetails.DoesNotExist:
        profile = None

    return render(request, 'skill_swap_user/profile.html', {
        'user': user,
        'profile': profile,
    })

def logout_view(request):
    request.session.flush()
    return redirect('login')