from django.forms import ModelForm

from apps.models import UserProfile, Post, Media


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'


#       fields ga nima qo'shsak oshani admin sahifada boshqara olamiz


class MediaForm(ModelForm):
    class Meta:
        model = Media
        fields = '__all__'


class PostForm(ModelForm):
    class Meta:
        model = Post
        exclude = ['id']
