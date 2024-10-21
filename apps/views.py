import uuid

from django.shortcuts import render, redirect

from apps.forms import PostForm, MediaForm
from apps.models import UserProfile, Post
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required


# @login_required(login_url="sign_in")
def UserProfileView(request):
    # users = UserProfile.objects.all()
    user = request.user
    posts = Post.objects.filter(user=user)
    return render(request, "profile.html", {"users": user, "posts": posts})


@login_required(login_url="sign_in")
def HomeView(request):
    return render(request, "home.html")


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
            if check_password(
                    password, user.password
            ):  # Correctly check the hashed password
                login(request, user)  # Log the user in
                messages.success(request, "Logged in successfully")
                return redirect("profile")
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
        post_form = PostForm(request.POST)
        media_form = MediaForm(request.POST, request.FILES)

        if post_form.is_valid() and media_form.is_valid():
            # Save media file
            media = media_form.save(commit=False)
            media.user = request.user
            media.save()

            # Save post
            post = post_form.save(commit=False)
            post.id = str(uuid.uuid4())  # Generate a unique ID for the post
            post.user = request.user
            post.save()

            # Add media to the post
            post.media.add(media)
            post.save()

            return redirect('home')  # Redirect to a relevant page, e.g., home

    else:
        post_form = PostForm()
        media_form = MediaForm()

    return render(request, 'create_post.html', {'post_form': post_form, 'media_form': media_form})
