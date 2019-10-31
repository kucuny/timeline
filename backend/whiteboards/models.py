from django.contrib.auth import get_user_model
from django.db import models

from contents.models import Image, Tag
from helpers.models import BaseDateTimeModel


User = get_user_model()


class WhiteBoard(BaseDateTimeModel):
    content = models.TextField()

    tags = models.ManyToManyField(Tag,
                                  related_name='whiteboards')


class WhiteBoardComment(BaseDateTimeModel):
    whiteboard = models.ForeignKey(WhiteBoard,
                                   on_delete=models.CASCADE,
                                   related_name='whiteboards')
    parent = models.ForeignKey('self',
                               null=True, blank=True,
                               on_delete=models.CASCADE,
                               related_name='parent_whiteboard_comments')
    comment = models.TextField()
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(User,
                                   null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='whiteboard_comments')
    updated_by = models.ForeignKey(User,
                                   null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='updated_whiteboard_comments')

    tags = models.ManyToManyField(Tag,
                                  related_name='whiteboard_comments')

    def delete(self, using=None, keep_parents=False):
        keep_parents = True
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])
        super().delete(using, keep_parents)
