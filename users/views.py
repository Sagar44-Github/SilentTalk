from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm, LoginForm, ProfileEditForm
from .models import UserProfile


def register_view(request):
    """Handle user registration with full validation."""
    # Redirect already-authenticated users
    if request.user.is_authenticated:
        return redirect("landing")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        # --- Validation ---
        errors = []

        if not first_name:
            errors.append("First name is required.")
        if not last_name:
            errors.append("Last name is required.")
        if not email:
            errors.append("Email is required.")
        if not password1 or len(password1) < 8:
            errors.append("Password must be at least 8 characters.")
        if password1 != password2:
            errors.append("Passwords do not match.")
        if email and User.objects.filter(email=email).exists():
            errors.append("An account with this email already exists.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "recognition/register.html", {
                "form_data": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                }
            })

        # --- Create User ---
        user = User.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )

        # Create profile
        UserProfile.objects.create(user=user)

        # Auto-login after registration
        login(request, user)
        messages.success(request, f"Welcome to SilentTalk, {user.first_name}! 🎉")
        return redirect("landing")

    # GET request — render empty form
    return render(request, "recognition/register.html")


def login_view(request):
    """Handle user login with email + password."""
    # Redirect already-authenticated users
    if request.user.is_authenticated:
        return redirect("landing")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Please enter both email and password.")
            return render(request, "recognition/login.html")

        # Look up user by email, then authenticate
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}! 👋")

            # Honour the ?next= parameter for @login_required redirects
            next_url = request.GET.get("next") or request.POST.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("landing")
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, "recognition/login.html", {
                "form_data": {"email": email}
            })

    # GET request — render empty form
    return render(request, "recognition/login.html")


def logout_view(request):
    """Log the user out and redirect to landing."""
    logout(request)
    messages.info(request, "You've been signed out.")
    return redirect("landing")


@login_required(login_url="login_page")
def profile_view(request):
    """User profile / dashboard page."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        bio = request.POST.get("bio", "").strip()
        role = request.POST.get("role", "learner")

        # Update User model fields
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.username = email  # Keep username in sync with email
        request.user.save()

        # Update Profile fields
        profile.bio = bio
        profile.role = role
        # Recalculate avatar initials
        first_initial = first_name[:1].upper() if first_name else ""
        last_initial = last_name[:1].upper() if last_name else ""
        profile.avatar_initial = f"{first_initial}{last_initial}" or email[:2].upper()
        profile.save()

        messages.success(request, "Profile updated successfully! ✅")
        return redirect("profile")

    # GET — pre-fill form with current data
    form_data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
        "bio": profile.bio,
        "role": profile.role,
    }

    return render(request, "users/profile.html", {
        "form_data": form_data,
        "profile": profile,
    })
