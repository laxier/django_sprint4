from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.utils import timezone
from .models import Post, Category

def index(request):
    template = 'blog/post_list.html'
    post_list = Post.get_published_posts(5)
    context = {'post_list': post_list}
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if (post.pub_date > timezone.now()
            or not post.is_published
            or not post.category.is_published):
        raise Http404("Публикация не найдена.")
    return render(request, 'blog/post_detail.html', {'post': post})


def category_posts(request, category_slug):
    template = 'blog/category_list.html'
    category = get_object_or_404(Category, slug=category_slug)
    if not category.is_published:
        raise Http404("Category is not published.")
    post_list = Post.get_published_posts(n=None).filter(category=category)
    context = {'category': category,
               'post_list': post_list}
    return render(request, template, context)
