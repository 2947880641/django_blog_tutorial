from PIL import Image
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager



class ArticleColum(models.Model):
    # 栏目标题
    title = models.CharField(max_length=100,blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class ArticlePost(models.Model):
    # 新增点赞数统计
    likes = models.PositiveIntegerField(default=0)
    #文章作者  参数on_delete用于指定数据删除的方式
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    # 文章栏目的 “一对多” 外键
    column = models.ForeignKey(
        ArticleColum,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    # 文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d',blank=True)
    # 保存时处理图片
    def save(self,*args,**kwargs):
    # 调用原有的 save() 的功能
        article = super(ArticlePost,self).save(*args,**kwargs)
    # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x,y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x,new_y),Image.ANTIALIAS)
            resized_image.save(self.avatar.path)

        return article

    def was_created_recently(self):
        diff = timezone.now() - self.created

        # if diff.days <= 0 and diff.seconds < 60:
        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            return True
        else:
            return False
    #文章标题，CharField用于保存较短的字符串
    title = models.CharField(max_length=100)
    #文章正文。保存大量文本使用TextField
    body = models.TextField()
    #文章创建时间 参数指定在创建数据时默认写当前时间
    created = models.DateTimeField(default=timezone.now)
    #文章更新时间，更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)
    # 浏览量
    total_views = models.PositiveIntegerField(default=0)
    # 文章标签
    tags = TaggableManager(blank=True)

    # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail',args=[self.id])
    class Meta:
        #内部类class meta 用于给model定义元数据
        #ordering 指定模型返回的数据的排列顺序
        #-created 表明数据应该以倒序排列
        ordering = ('-created',)

        #定义当调用对象str（）方法时的返回内容
        def __str__(self):
            #将文章标题返回
            return self.title

