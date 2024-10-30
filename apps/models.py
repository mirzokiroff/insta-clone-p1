import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import CharField, PositiveIntegerField, TextField, ImageField, Model, EmailField, URLField, \
    ForeignKey, FileField, DateTimeField, CASCADE, ManyToManyField, BooleanField
from django.contrib.auth.models import AbstractUser

from conf import settings


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
    phone = CharField(max_length=70)
    followers = ManyToManyField("apps.UserProfile", related_name='my_followers', symmetrical=False, blank=True)
    following = ManyToManyField("apps.UserProfile", related_name='my_following', symmetrical=False, blank=True)
    likes = ManyToManyField("apps.UserProfile", related_name='my_likes', symmetrical=False, blank=True)
    is_public = BooleanField(default=True)
    user_posts = ManyToManyField('Post', related_name='users_posts', blank=True)
    user_reels = ManyToManyField('Reels', related_name='users_reels', blank=True)
    user_stories = ManyToManyField('Story', related_name='users_stories', blank=True)
    user_highlights = ManyToManyField('Highlight', related_name='users_highlights', blank=True)
    bio = CharField(max_length=777, blank=True, null=True)
    password = CharField(max_length=128)

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def following_count(self):
        return self.following.count()

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def posts_count(self):
        return self.user_posts.count()

    def __str__(self):
        return self.username + " " + self.first_name + " " + self.last_name


class Post(Model):
    id = CharField(primary_key=True, max_length=36, unique=True, default=uuid.uuid4)
    user = ForeignKey("apps.UserProfile", on_delete=CASCADE, related_name='post_user')
    tag = ForeignKey("apps.UserProfile", on_delete=CASCADE, related_name="post_tags", blank=True, null=True)
    date = DateTimeField(auto_now_add=True)
    location = CharField(max_length=222, blank=True, null=True)
    media_post = FileField(upload_to='media_post/', validators=([file_ext_validator]))
    text = TextField(default="bu erda siz o'ylagan ibora bor", blank=True, null=True)
    is_saved = BooleanField(default=False)

    @property
    def get_number_of_likes(self):
        return self.post_likes.count()

    @property
    def get_number_of_comments(self):
        return self.post_comments.count()

    def get_number_of_viewers(self):
        return self.post_view.count()

    def __str__(self):
        return f"{self.id} -- {self.user}"


class Reels(Model):
    id = CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='reels_user')
    caption = TextField(null=True, blank=True)
    media = FileField(upload_to='reels/', validators=[FileExtensionValidator(['mp4', 'avi', 'mkv', 'mov'])])

    @property
    def get_number_of_likes(self):
        return self.reels_likes.count()

    @property
    def get_number_of_comments(self):
        return self.reels_comments.count()


class Comment(Model):
    id = CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='comment_user')
    comment = TextField()
    date = DateTimeField(auto_now_add=True)
    post = ForeignKey('Post', CASCADE, related_name='post_comments', null=True, blank=True)
    reels = ForeignKey('Reels', CASCADE, related_name='reels_comments', null=True, blank=True)

    def __str__(self):
        return self.comment

    @property
    def get_number_of_likes(self):
        return self.comment_likes

    class Meta:
        unique_together = ('post', 'reels')


class Story(Model):
    id = CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='story_user')
    story = FileField(upload_to='story/', validators=[FileExtensionValidator(['mp4', 'jpg', 'png', 'mov'])])
    mention = ForeignKey("apps.UserProfile", CASCADE, related_name="mentioned_users", null=True, blank=True)
    viewer = ForeignKey("apps.UserProfile", CASCADE, related_name='story_viewers', null=True, blank=True)
    date = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.story

    def get_viewers_info(self):
        viewers_info = []
        for viewer_relation in self.story_view.all():
            viewer = viewer_relation
            viewer_info = {
                'username': viewer.user,
                'full_name': viewer.get_full_name(),
                'avatar': viewer.user if viewer.userprofile.avatar else None,
            }
            viewers_info.append(viewer_info)
        return viewers_info

    @property
    def get_number_of_likes(self):
        return self.story_likes.count()


class Highlight(Model):
    id = CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='highlight_user')
    name = CharField(max_length=77)
    date = DateTimeField(auto_now_add=True)
    highlight = ForeignKey('Story', CASCADE, related_name='highlight')

    def __str__(self):
        return self.user.username  # noqa

    @property
    def get_numbers_of_likes(self):
        return self.highlight_likes.count()


class Viewers(Model):
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='user_view')
    post = ForeignKey('Post', CASCADE, related_name='post_view')
    reel = ForeignKey('Reels', CASCADE, related_name='reel_view')
    story = ForeignKey('Story', CASCADE, related_name='story_view')


class PostLike(Model):
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='post_like_user', null=True, blank=True)
    post = ForeignKey('Post', CASCADE, related_name='post_likes')

    def __str__(self):
        return 'Like: ' + self.user.username  # noqa


class StoryLike(Model):
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='story_like_user')
    story = ForeignKey('Story', CASCADE, related_name='story_likes')

    def __str__(self):
        return 'Like: ' + self.user.username  # noqa


class CommentLike(Model):
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='comment_liked_user')
    comment = ForeignKey('Comment', CASCADE, related_name='comment_likes')

    def __str__(self):
        return 'Like: ' + self.user.username  # noqa


class ReelsLike(Model):
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='reels_like_user')
    reels = ForeignKey('Reels', CASCADE, related_name='reels_likes')

    def __str__(self):
        return 'Like: ' + self.user.username  # noqa


class HighlightLike(Model):
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='highlight_like_user')
    highlight = ForeignKey('Highlight', CASCADE, related_name='highlight_likes')

    def __str__(self):
        return 'Like: ' + self.user.username  # noqa
