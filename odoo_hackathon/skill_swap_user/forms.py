# skill_swap_user/forms.py
from django import forms
from django.contrib.auth.models import User
import re

# Step 1: Basic Registration Form
class RegistrationFormStep1(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Enforce at least 8 characters, one uppercase, one lowercase, one number, one special char
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(pattern, password):
            raise forms.ValidationError(
                "Password must be at least 8 characters long and include at least one uppercase letter, "
                "one lowercase letter, one number, and one special character."
            )
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

# Step 2: Optional Details
class RegistrationFormStep2(forms.Form):
    location = forms.CharField(required=False, max_length=150)
    phone_number = forms.CharField(required=False, max_length=20)
    current_profession = forms.CharField(required=False, max_length=100)
    skills_offered = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))
    skills_required = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))
    availability = forms.CharField(required=False, help_text="e.g., Weekends, Evenings")

# Login Form (Optional but recommended for flexibility)
class LoginForm(forms.Form):
    username = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

# Profile update form (for future use)
class OptionalDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']
