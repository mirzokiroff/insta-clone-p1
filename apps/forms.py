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
        fields = ['media_post', 'text', 'tag', 'location', 'alt_text', 'image_description', 'location_description',
                  'audio_description']
        widgets = {
            'text': Textarea(attrs={'placeholder': "Write your thoughts here...", 'rows': 3}),
            'location': TextInput(attrs={'placeholder': "Add location"}),
            'alt_text': Textarea(attrs={'placeholder': "Add image description", 'rows': 2}),
        }
