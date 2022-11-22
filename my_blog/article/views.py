from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.serializers import python
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

import markdown

# Create your views here.
from django.views import View

from article.forms import ArticlePostForm
from article.models import ArticlePost, ArticleColum
from comment.forms import CommentForm
from comment.models import Comment


def article_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tags')
    # 初始化查询集
    article_list = ArticlePost.objects.all()
    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search)|Q(body__icontains=search)
        )
    else:
        search=''
    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)
    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])
    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by("-total_views")
    # 每页显示 1 篇文章
    paginator = Paginator(article_list,3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)

    context = {'articles': articles , 'order':order ,'search':search,
               'column':column,'tag':tag}

    return render(request, 'article/list.html', context)


def article_detail(request, id):
    # 取出相应的文章
    # article = ArticlePost.objects.get(id=id)
    article = get_object_or_404(ArticlePost,id=id)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(
                extensions=[
                # 包含 缩写、表格等常用扩展
                'markdown.extensions.extra',
                # 语法高亮扩展
                'markdown.extensions.codehilite',
                #目录拓展
                'markdown.extensions.toc',
                ]
            )
    article.body = md.convert(article.body)
    comment_form = CommentForm()
    # 需要传递给模板的对象
    context = {'article': article , 'toc': md.toc ,'comments':comments,'comment_form':comment_form,}
    return render(request, 'article/detail.html', context)

def article_create(request):
    if request.method =='POST':
        # 增加 request.FILES
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST,request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=request.user.id)

            if request.POST['column'] != 'none':
                new_article.column = ArticleColum.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()
            # 新增代码，保存 tags 的多对多关系
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        else:
            # 如果数据不合法，返回错误信息
            return HttpResponse("表单内容有误，请重新填写")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColum.objects.all()
        # 赋值上下文
        context = {'article_post_form': article_post_form,'columns':columns}
        # 返回模板
        return render(request,'article/create.html',context)

def article_delete(request,id):
    article = ArticlePost.objects.get(id=request.user.id)
    article.delete()
    return  redirect("article:article_delete")

@login_required(login_url='/userprofile/login/login/')
def article_safe_delete(request,id):

    if request.method == 'POST':
        #根据id获取需要删除的文章
        article = ArticlePost.objects.get(id=id)
        if request.user != article.author:
            return HttpResponse("你没有权限删除此用户")
        #调用.delete（）方法删除文章
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")

@login_required(login_url='/userprofile/login/login/')
def article_update(request,id):
    #获取需要修改的具体对象
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉年没有权限修改这篇文章")
    if request.method == 'POST':
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColum.objects.get(id=request.POST['column'])
            else:
                article.column = None
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

            article.tags.set(*request.POST.get('tags').split(','),clear=True)
            article.save()
            return redirect("article:article_detail",id=id)
        else:
            return HttpResponse("表单内容有误,请重新填写")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColum.objects.all()
        context = {'article':article,'article_post_form':article_post_form,'columns':columns,
                   'tags': ','.join([x for x in  article.tags.names()]),
                   }
        return render(request,'article/update.html',context)

# 点赞数 +1
class IncreaseLikesView(View):
    def post(self,request,*args,**kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')