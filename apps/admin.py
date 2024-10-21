from django.contrib import admin
from .forms import UserProfileForm, PostForm
from .models import UserProfile, Post


class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm


class PostAdmin(admin.ModelAdmin):
    form = PostForm


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Post, PostAdmin)
