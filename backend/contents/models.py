from django.db import models

from helpers.models import BaseInfoModel


class Post(BaseInfoModel):
    images = models.ManyToManyField('PostImage')
    tags = models.ManyToManyField('Tag')


class PostImage(BaseInfoModel):
    image = models.ImageField()


class Tag(BaseInfoModel):
    name = models.CharField(max_length=50)


class Comment(BaseInfoModel):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    comment = models.TextField()

    tags = models.ManyToManyField(Tag)
