from django.contrib import admin

# Register your models here.
from article.models import ArticlePost, ArticleColum

admin.site.register(ArticlePost)
admin.site.register(ArticleColum)