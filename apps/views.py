from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from apps.forms import PostForm
from apps.models import UserProfile, Post


@login_required(login_url="sign_in")
def UserProfileView(request):
    user_profile = request.user
    posts = Post.objects.filter(user=request.user)
    return render(request, "profile.html", {"users": user_profile, "posts": posts})


@login_required(login_url="sign_in")
def HomeView(request):
    # Foydalanuvchining obunachilarini olish
    user_profile = UserProfile.objects.get(id=request.user.id)
    following_users = user_profile.following.all()  # Agar following bilan bog'langan bo'lsa

    # Har bir obunachining postlarini olish
    posts = Post.objects.filter(user__in=following_users).select_related('user').order_by('-date')

    context = {
        'posts': posts,
        'current_user': user_profile,
        'suggested_users': UserProfile.objects.exclude(id=user_profile.id)[:5],
        # Tavsiya etilgan foydalanuvchilar uchun
    }
    return render(request, "home.html", context)


@login_required(login_url="sign_in")
def ExploreView(request):
    return render(request, "explore.html")


@login_required(login_url="sign_in")
def MessageView(request):
    return render(request, "messages.html")


@login_required(login_url="sign_in")
def ReelsView(request):
    return render(request, "reels.html")


def sign_up(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            if UserProfile.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
            elif UserProfile.objects.filter(email=email).exists():
                messages.error(request, "Email already in use")
            else:
                # Hash the password before saving
                hashed_password = make_password(password1)
                apps_userprofile = UserProfile.objects.create(
                    username=username,
                    email=email,
                    password=hashed_password,  # Save hashed password
                )
                apps_userprofile.save()

                messages.success(request, "Account created successfully")
                return redirect("sign_in")
        else:
            messages.error(request, "Passwords do not match")

    return render(request, "sign_up.html")


def sign_in(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = UserProfile.objects.get(username=username)
            # Check the hashed password
            if check_password(password, user.password):
                login(request, user)  # Log the user in
                messages.success(request, "Logged in successfully")
                return redirect("profile")  # Foydalanuvchini o'z profili sahifasiga yo'naltirish
            else:
                messages.error(request, "Invalid username or password")
        except UserProfile.DoesNotExist:
            messages.error(request, "Invalid username or password")

        return redirect("sign_in")

    return render(request, "login.html")


def sign_out(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect("sign_in")


@login_required(login_url="sign_in")
def edit_profile(request):
    user_profile = UserProfile.objects.get(username=request.user.username)

    if request.method == "POST":
        user_profile.username = request.POST.get("username")
        user_profile.first_name = request.POST.get("first_name")
        user_profile.last_name = request.POST.get("last_name")
        user_profile.bio = request.POST.get("bio")

        if UserProfile.objects.filter(
                username=user_profile.username).exists() and user_profile.username != request.user.username:
            messages.error(request, "Username already exists!")
            return render(request, 'edit_profile.html', {'user': request.user})
        else:

            if request.FILES.get("image"):
                user_profile.image = request.FILES.get("image")
            else:
                messages.error(request, "Please, upload an image")

            user_profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")

    return render(request, "edit_profile.html", {"user": user_profile})


@login_required(login_url='sign_in')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})
