from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


User = get_user_model()


class Activity(models.Model):
    user = models.ForeignKey(User,
                             null=True, blank=False,
                             db_index=True, on_delete=models.SET_NULL,
                             related_name='activities')
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    is_created = models.BooleanField(default=True)
    is_updated = models.BooleanField(default=False)

    activity_created_at = models.DateTimeField(auto_now_add=True,
                                               db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = ('user', 'content_type', 'object_id')
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ('-activity_created_at',)
