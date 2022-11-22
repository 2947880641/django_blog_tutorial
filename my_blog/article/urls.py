from django.urls import path

from article import views

urlpatterns = [
    # 取出所有文章
    path('article-list/', views.article_list, name='article_list'),
    # 取出相对应文章
    path('article-detail/<int:id>/', views.article_detail, name='article_detail'),
    # 写文章
    path('article-create/', views.article_create, name='article_create'),
    # 删除
    path('article-delete/<int:id>/', views.article_delete, name='article_delete'),
    # 安全删除
    path('article-safe-delete/<int:id>/', views.article_safe_delete, name='article_safe_delete'),
    # 修改文章
    path('article-update/<int:id>/', views.article_update, name='article_update'),
    # 点赞 +1
    path(
        'increase-likes/<int:id>/',
        views.IncreaseLikesView.as_view(),
        name='increase_likes'
    ),

]
app_name = 'article'
