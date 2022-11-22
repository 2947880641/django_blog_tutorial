from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from article.models import ArticlePost


class Comment(MPTTModel):
    article = models.ForeignKey(
        ArticlePost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    # mptt树形结构
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    # 记录二级评论回复给谁, str
    reply_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replyers'
    )
    #body = models.TextField()
    body = RichTextField()
    created = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     ordering = ('created',)
    class MPTTMeta:
        order_inserton_by = ['creatrd']

    def __str__(self):
        return self.body[20]