from django.urls import path
from apps.views import UserProfileView, HomeView, ExploreView, ReelsView, MessageView, sign_up, sign_in, sign_out, \
    edit_profile, create_post

urlpatterns = [
    path("", HomeView, name="home"),
    path("profile/", UserProfileView, name="profile"),
    path("explore/", ExploreView, name="explore"),
    path("reels/", ReelsView, name="reels"),
    path("message/", MessageView, name="message"),
    path("sign-up/", sign_up, name="sign_up"),
    path("sign-in/", sign_in, name="sign_in"),
    path("sign-out/", sign_out, name="sign_out"),
    path("edit-profile/", edit_profile, name="edit_profile"),

    path('create-post/', create_post, name='create_post'),

]
