from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from .models import Post, Category, User, Comment
from .forms import PostCreateForm, CommentCreateForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView


class PaginatorMixin:
    paginate_by = 10


class PostMixin:
    model = Post


class PostFormMixin:
    form_class = PostCreateForm


class PostList(PaginatorMixin, PostMixin, ListView):
    template_name = 'blog/index.html'
    queryset = Post.get_published_posts()


class PostDetail(CreateView):
    form_class = CommentCreateForm
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        if (post.pub_date > timezone.now() or not post.is_published or not post.category.is_published):
            raise Http404("Публикация не найдена.")
        context['post'] = post
        context['comments'] = post.comments.all()
        return context


class CategoryList(PaginatorMixin, PostMixin, ListView):
    template_name = 'blog/index.html'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        if not self.category.is_published:
            raise Http404("Category is not published.")
        return Post.get_published_posts(n=None).filter(category=self.category)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostCreate(PostMixin, PostFormMixin, CreateView):
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdate(PostMixin, PostFormMixin, UpdateView):
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'


class PostDelete(PostMixin, DeleteView):
    pk_url_kwarg = 'post_id'


class UserByUsernameMixin:
    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        self.user = get_object_or_404(User, username=username)
        return self.user


class ProfilePage(UserByUsernameMixin, PaginatorMixin, DetailView):
    template_name = 'blog/profile.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        user_posts = self.object.posts.all()

        paginator = Paginator(user_posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ProfileUpdate(UpdateView):
    template_name = 'blog/user.html'
    model = User
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class CommentMixin:
    model = Comment


class CommentFormMixin:
    form_class = CommentCreateForm


class CommentIdMixin:
    pk_url_kwarg = 'comment_id'


class BackToPostMixin:
    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse_lazy('blog:post_detail', kwargs={'post_id': post_id})


class CommentCreate(CommentFormMixin, CreateView):
    context_object_name = 'comment'

    def form_valid(self, form):
        comment = form.save(commit=False)

        comment.author = self.request.user

        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        comment.post = post

        comment.save()
        return HttpResponseRedirect(reverse_lazy('blog:post_detail', kwargs={'post_id': post.id}))


class CommentUpdate(CommentIdMixin, CommentMixin, CommentFormMixin, BackToPostMixin, UpdateView):
    template_name = 'blog/comment.html'


class CommentDelete(CommentMixin, CommentIdMixin, BackToPostMixin, DeleteView):
    template_name = 'blog/comment.html'
