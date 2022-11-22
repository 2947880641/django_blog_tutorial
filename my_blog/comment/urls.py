from django.urls import path

from comment import views

urlpatterns = [
  path('post-comment/<int:article_id>/', views.post_comment, name='post_comment'),
  path('post-comment/<int:article_id>/<int:parent_comment_id>',views.post_comment,name='comment_reply')
]
app_name ='comment'