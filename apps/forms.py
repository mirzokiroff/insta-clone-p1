from django.forms import ModelForm, Textarea, TextInput

from apps.models import UserProfile, Post


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'


#       fields ga nima qo'shsak oshani admin sahifada boshqara olamiz


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['media_post', 'text', 'tag', 'location']
        widgets = {
            'text': Textarea(attrs={'placeholder': "Write your thoughts here...", 'rows': 3}),
            'location': TextInput(attrs={'placeholder': "Add location"}),
        }
