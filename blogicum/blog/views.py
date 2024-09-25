from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.utils import timezone
from .models import Post, Category
from django.views.generic import ListView
from django.views.generic import DetailView


class PostList(ListView):
    model = Post
    context_object_name = 'post_list'
    queryset = Post.get_published_posts(5)


class PostDetail(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'
    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if (post.pub_date > timezone.now()
                or not post.is_published
                or not post.category.is_published):
            raise Http404("Публикация не найдена.")
        return post

class CategoryList(ListView):
    model = Post
    template_name = 'blog/category_list.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        if not self.category.is_published:
            raise Http404("Category is not published.")
        return Post.get_published_posts(n=None).filter(category=self.category)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
