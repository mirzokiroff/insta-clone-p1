import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import CharField, PositiveIntegerField, TextField, ImageField, Model, EmailField, URLField, \
    ForeignKey, FileField, DateTimeField, CASCADE, ManyToManyField
from django.contrib.auth.models import AbstractUser


class CustomFileExtensionValidator(FileExtensionValidator):
    message = _(
        "File extension “{extension}(s)” is not allowed. "
        "Allowed extensions are: {allowed_extensions}s."
    )

    def __call__(self, value):
        extension = Path(value.name).suffix[1:].lower()  # value bu erda fayl obyekti
        if (
                self.allowed_extensions is not None
                and extension not in self.allowed_extensions
        ):
            raise ValidationError(
                self.message.format(**{
                    "extension": extension,
                    "allowed_extensions": ", ".join(self.allowed_extensions),
                    "value": value,
                }),
                code=self.code,
            )


file_ext_validator = CustomFileExtensionValidator(
    ('mp4', 'mkv', 'avi', 'webm', '3gp', 'jpg', 'jpeg', 'png', 'webp', 'mov'))


# Create your models here.
class UserProfile(AbstractUser):
    image = ImageField(upload_to="user_profile_pics", null=True, blank=True)
    # username = CharField(max_length=50, unique=True)
    # first_name = CharField(max_length=70, blank=True, null=True)
    # last_name = CharField(max_length=70, blank=True, null=True)
    # email = EmailField(unique=True)
    phone = CharField(max_length=70)
    followers = PositiveIntegerField(default=0)
    following = PositiveIntegerField(default=0)
    bio = CharField(max_length=777, blank=True, null=True)
    posts = PositiveIntegerField(default=0)
    password = CharField(max_length=128)
    # password2 = CharField(max_length=70)

    # def get_full_name():
    #     return f"{first_name} {last_name}"


class Post(Model):
    id = CharField(primary_key=True, max_length=36, unique=True, default=uuid.uuid4)
    user = ForeignKey('apps.UserProfile', CASCADE, related_name='post_user')
    tag = ForeignKey('apps.UserProfile', CASCADE, related_name="post_tags", blank=True, null=True)
    date = DateTimeField(auto_now_add=True)
    location = CharField(max_length=222, blank=True, null=True)
    media_post = FileField(upload_to='media_post/', validators=([file_ext_validator]))
    text = TextField(default="bu erda siz o'ylagan ibora bor", blank=True, null=True)
    alt_text = TextField(blank=True, null=True)
    image_description = TextField(blank=True, null=True)
    location_description = TextField(blank=True, null=True)
    audio_description = TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id} -- {self.user}"
