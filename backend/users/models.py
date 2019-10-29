from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Profile(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)
