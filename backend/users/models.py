from django.contrib.auth.models import AbstractUser
from django.db import models

from helpers.models import BaseDateTimeModel


class User(AbstractUser):
    pass


class Profile(BaseDateTimeModel):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE, parent_link=True,
                                related_name='profile')
    nickname = models.CharField(max_length=30, null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True)
    comment = models.TextField()


class FavoritePost(BaseDateTimeModel):
    user = models.ForeignKey(User,
                             null=True, blank=True,
                             db_index=True, on_delete=models.SET_NULL,
                             related_name='favorite_posts')
    post = models.ForeignKey('contents.Post',
                             db_index=True, on_delete=models.CASCADE,
                             related_name='favorite_post_users')

    comments = models.TextField()

    class Meta:
        unique_together = ('user', 'post')


class LikePost(BaseDateTimeModel):
    user = models.ForeignKey(User,
                             null=True, blank=True,
                             db_index=True, on_delete=models.SET_NULL,
                             related_name='like_posts')
    post = models.ForeignKey('contents.Post',
                             db_index=True, on_delete=models.CASCADE,
                             related_name='like_post_users')

    class Meta:
        unique_together = ('user', 'post')
