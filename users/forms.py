from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class RegisterForm(forms.Form):
    """Registration form matching the existing register.html template fields."""

    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class LoginForm(forms.Form):
    """Login form matching the existing login.html template fields (email + password)."""

    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileEditForm(forms.Form):
    """Edit profile form."""

    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    bio = forms.CharField(max_length=300, required=False, widget=forms.Textarea(attrs={"rows": 3}))
    role = forms.ChoiceField(
        choices=[
            ("learner", "Learner"),
            ("educator", "Educator"),
            ("interpreter", "Interpreter"),
        ],
        required=True,
    )
