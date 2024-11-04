from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from apps.forms import PostForm
from apps.models import UserProfile, Post, Reels


@login_required(login_url="sign_in")
def UserProfileView(request):
    user_profile = request.user  # Hozirgi foydalanuvchini olish
    posts = Post.objects.filter(user=user_profile)
    tagged_posts = Post.objects.filter(tag=user_profile)

    return render(request, "profile.html", {
        "users": user_profile,
        "posts": posts,
        "tagged_posts": tagged_posts,
    })


# def other_users_profile(request, username):
# print(f"Attempting to retrieve UserProfile with username: {username}")
# user_profile = get_object_or_404(UserProfile, username=username)  # Username bilan foydalanuvchini olish
# posts = Post.objects.filter(user=user_profile)  # Foydalanuvchining postlarini olish
# tagged_posts = Post.objects.filter(tag=user_profile)  # Foydalanuvchi tagida bo'lgan postlar
# return render(request, "other_users.html", {
# "user": user_profile,
# "posts": posts,
# "tagged_posts": tagged_posts
# })


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
    posts = Post.objects.all()
    reels = Reels.objects.all()
    users = UserProfile.objects.all()
    return render(request, "exploree.html", {"posts": posts, "reels": reels, "user": users})


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
            if check_password(password, user.password):
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
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})


@login_required(login_url="sign_in")
def follow_unfollow(request, username):
    user_to_follow = get_object_or_404(UserProfile, username=username)

    if request.user in user_to_follow.followers.all():
        # Unfollow
        user_to_follow.followers.remove(request.user)
        request.user.following.remove(user_to_follow)
    else:
        # Follow
        user_to_follow.followers.add(request.user)
        request.user.following.add(user_to_follow)

    return redirect('other_users', username=username)


def search_users(request):
    query = request.POST.get("query", "")
    results = UserProfile.objects.filter(username__icontains=query, is_public=True) if query else []
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX check
        results_data = [
            {
                "username": user.username,
                "full_name": user.get_full_name(),
                "image_url": user.image.url if user.image else "images/profile_img.jpg"
            }
            for user in results
        ]
        return JsonResponse({"results": results_data})
    return render(request, "base.html", {"query": query, "results": results})
