# odoo_hackathon/skill_swap_user/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from datetime import timedelta

from .models import CustomUser, UserDetails, SwapRequest, Feedback
from .forms import (
    RegistrationFormStep1, RegistrationFormStep2,
    LoginForm, UpdateUserDetailsForm, SwapRequestForm, FeedbackForm
)
from .utils import password_reset_token

def index(request):
    return render(request, 'skill_swap_user/index.html')

# ---------------- Registration ----------------
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
                        **form.cleaned_data
                    )
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Error creating account: {e}")
                return redirect('register')
    else:
        form = RegistrationFormStep1()

    return render(request, 'skill_swap_user/register.html', {'form': form})


# ---------------- Login ----------------
def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['last_activity'] = timezone.now().isoformat()
                return redirect('profile')
            else:
                error = "Invalid credentials"
        except CustomUser.DoesNotExist:
            error = "Invalid credentials"

    return render(request, 'skill_swap_user/login.html', {'error': error})


# ---------------- Session Timeout Middleware ----------------
def check_session_timeout(request):
    last_activity = request.session.get('last_activity')
    if last_activity:
        last_activity_time = timezone.datetime.fromisoformat(last_activity)
        if timezone.now() - last_activity_time > timedelta(minutes=15):
            request.session.flush()
            return True
        else:
            request.session['last_activity'] = timezone.now().isoformat()
    return False


# ---------------- Profile ----------------
def profile_view(request):
    if check_session_timeout(request) or not request.session.get('user_id'):
        return redirect('login')

    user = get_object_or_404(CustomUser, id=request.session['user_id'])

    # Ensure profile exists or allow editing if skipped
    profile, created = UserDetails.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UpdateUserDetailsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UpdateUserDetailsForm(instance=profile)

    return render(request, 'skill_swap_user/profile.html', {
        'user': user,
        'profile': profile,
        'form': form,
    })


# ---------------- Logout ----------------
def logout_view(request):
    request.session.flush()
    return redirect('login')


# ---------------- Forgot Password ----------------
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token.make_token(user)

            html_content = render_to_string("skill_swap_user/password_reset_email.html", {
                'user': user,
                'uid': uid,
                'token': token,
                'domain': request.get_host(),
            })

            email_message = EmailMultiAlternatives(
                "Reset Your SkillSwap Password", "", None, [user.email]
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

            messages.success(request, "A password reset link has been sent to your email.")
        except CustomUser.DoesNotExist:
            messages.error(request, "This email is not registered.")
            return redirect('register')

    return render(request, 'skill_swap_user/forgot_password.html')


def reset_password_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except Exception:
        user = None

    if user and password_reset_token.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
            elif len(new_password) < 8:
                messages.error(request, "Password too short.")
            else:
                user.password = make_password(new_password)
                user.save()
                messages.success(request, "Password reset successful.")
                return redirect('login')

        return render(request, 'skill_swap_user/reset_password.html', {
            'uidb64': uidb64,
            'token': token
        })

    return render(request, 'skill_swap_user/password_reset_invalid.html')


# ---------------- Search Public Profiles ----------------
def search_users(request):
    if check_session_timeout(request) or not request.session.get('user_id'):
        return redirect('login')

    query = request.GET.get('q', '')
    users = UserDetails.objects.filter(
        profile_visibility='public',
        skills_offered__icontains=query
    ).select_related('user') if query else []

    return render(request, 'skill_swap_user/search_results.html', {
        'query': query,
        'results': users
    })


# ---------------- Send Swap Request ----------------
def send_swap_request(request, receiver_id):
    if check_session_timeout(request) or not request.session.get('user_id'):
        return redirect('login')

    sender = get_object_or_404(CustomUser, id=request.session['user_id'])
    receiver = get_object_or_404(CustomUser, id=receiver_id)

    if request.method == 'POST':
        form = SwapRequestForm(request.POST)
        if form.is_valid():
            swap = form.save(commit=False)
            swap.sender = sender
            swap.receiver = receiver
            swap.save()
            messages.success(request, "Swap request sent.")
            return redirect('profile')
    else:
        form = SwapRequestForm()

    return render(request, 'skill_swap_user/send_request.html', {'form': form})


# ---------------- Manage Swap Requests ----------------
def manage_requests(request):
    if check_session_timeout(request) or not request.session.get('user_id'):
        return redirect('login')

    user = get_object_or_404(CustomUser, id=request.session['user_id'])
    received = SwapRequest.objects.filter(receiver=user)
    sent = SwapRequest.objects.filter(sender=user)
    return render(request, 'skill_swap_user/manage_requests.html', {
        'received': received,
        'sent': sent
    })


def update_request_status(request, request_id, action):
    swap = get_object_or_404(SwapRequest, id=request_id)
    if action in ['accept', 'reject']:
        swap.status = 'accepted' if action == 'accept' else 'rejected'
        swap.save()
    elif action == 'delete' and swap.status == 'pending':
        swap.delete()
    return redirect('manage_requests')


# ---------------- Feedback ----------------
def leave_feedback(request, swap_id):
    if check_session_timeout(request) or not request.session.get('user_id'):
        return redirect('login')

    swap = get_object_or_404(SwapRequest, id=swap_id, status='accepted')

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.swap = swap
            feedback.save()
            messages.success(request, "Feedback submitted.")
            return redirect('manage_requests')
    else:
        form = FeedbackForm()

    return render(request, 'skill_swap_user/feedback.html', {'form': form})
