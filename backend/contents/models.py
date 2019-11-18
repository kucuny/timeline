from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.text import slugify

from helpers.models import BaseDateTimeModel


User = get_user_model()


class Image(BaseDateTimeModel):
    image = models.ImageField()

    created_by = models.ForeignKey(User,
                                   null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='images')
    updated_by = models.ForeignKey(User,
                                   null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='updated_images')


class Tag(BaseDateTimeModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, allow_unicode=True,
                            unique=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(force_insert, force_update, using, update_fields)


class Post(BaseDateTimeModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, allow_unicode=True,
                            unique=True)

    created_by = models.ForeignKey(User,
                                   null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='posts')
    updated_by = models.ForeignKey(User,
                                   null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='updated_posts')

    images = models.ManyToManyField(Image,
                                    related_name='posts')
    tags = models.ManyToManyField(Tag,
                                  related_name='posts')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(force_insert, force_update, using, update_fields)


class PostComment(BaseDateTimeModel):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='post_comments')
    parent = models.ForeignKey('self',
                               null=True, blank=True,
                               on_delete=models.CASCADE,
                               related_name='parent_post_comments')
    comment = models.TextField()
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(User,
                                   null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='post_comments')
    updated_by = models.ForeignKey(User,
                                   null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='updated_post_comments')

    tags = models.ManyToManyField(Tag,
                                  related_name='post_comments')

    def delete(self, using=None, keep_parents=False):
        keep_parents = True
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])
        super().delete(using, keep_parents)


class GooglePhotoAlbum(BaseDateTimeModel):
    id = models.CharField(primary_key=True, max_length=250)
    title = models.CharField(max_length=200, null=False, blank=False)
    product_url = models.URLField(max_length=2000, null=False, blank=False)
    cover_photo_url = models.URLField(max_length=2000)


class GooglePhotoItem(BaseDateTimeModel):
    id = models.CharField(primary_key=True, max_length=250)
    album = models.ForeignKey(GooglePhotoAlbum,
                              null=True, blank=True,
                              on_delete=models.SET_NULL,
                              related_name='google_photo_items')
    product_url = models.URLField(max_length=2000)
    base_url = models.URLField(max_length=2000)
    mine_type = models.CharField(max_length=100)
    media_type = models.CharField(max_length=20)
    default_weight = models.PositiveIntegerField()
    default_height = models.PositiveIntegerField()
    meta = JSONField(null=True, blank=True)

    imported = models.BooleanField(default=False)
    imported_at = models.DateTimeField()

    def get_photo_url(self, weight: int, height: int):
        return self.base_url + f'=w{weight}-h{height}'
