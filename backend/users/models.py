from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_family = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')
    nickname = models.CharField(max_length=30, null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True)
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FavoritePost(models.Model):
    user = models.ForeignKey(User,
                             null=True, blank=True,
                             db_index=True, on_delete=models.SET_NULL,
                             related_name='favorite_posts')
    post = models.ForeignKey('contents.Post',
                             db_index=True, on_delete=models.CASCADE,
                             related_name='favorite_post_users')
    comments = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'post')


class LikePost(models.Model):
    user = models.ForeignKey(User,
                             null=True, blank=True,
                             db_index=True, on_delete=models.SET_NULL,
                             related_name='like_posts')
    post = models.ForeignKey('contents.Post',
                             db_index=True, on_delete=models.CASCADE,
                             related_name='like_post_users')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'post')
