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
