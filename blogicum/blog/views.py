from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .models import Post, Category, User, Comment
from .forms import PostCreateForm, CommentCreateForm
from django.db.models import Count


class PaginatorMixin:
    """Mixin for adding pagination to views."""

    paginate_by = 10


class PostMixin:
    """Mixin for Post model views."""

    model = Post


class PostFormMixin:
    """Mixin for Post form views."""

    form_class = PostCreateForm


class PostList(PaginatorMixin, PostMixin, ListView):
    """View for listing published posts."""

    template_name = 'blog/index.html'
    def get_queryset(self):
        return Post.get_published_posts(user=self.request.user)

class PostDetail(CreateView):
    """View for displaying post details and adding comments."""

    form_class = CommentCreateForm
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_post()
        context['post'] = post
        context['comments'] = post.comments.all()
        return context

    def get_post(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        # Check if the post should be visible to the current user
        if (
            (post.pub_date > timezone.now() or not post.is_published
             or not post.category.is_published)
            and post.author != self.request.user
        ):
            raise Http404("Публикация не найдена.")

        return post



class CategoryList(PaginatorMixin, PostMixin, ListView):
    """View for listing posts in a specific category."""

    template_name = 'blog/index.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug']
        )
        if not self.category.is_published:
            # Don't show posts from unpublished categories
            raise Http404("Category is not published.")
        return Post.get_published_posts(n=None, user=self.request.user, queryset=self.category.posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostCreate(LoginRequiredMixin, PostMixin, PostFormMixin, CreateView):
    """View for creating a new post."""

    template_name = 'blog/create.html'

    def form_valid(self, form):
        # Set the author of the post to the current user
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the user's profile page after creating a post
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class PostUpdate(LoginRequiredMixin, PostMixin, PostFormMixin, UpdateView):
    """View for updating an existing post."""

    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            # Redirect if the user is not the author of the post
            return HttpResponseRedirect(
                reverse_lazy(
                    'blog:post_detail',
                    kwargs={'post_id': post.id}
                )
            )
        return super().dispatch(request, *args, **kwargs)


class PostDelete(LoginRequiredMixin, PostMixin, DeleteView):
    """View for deleting a post."""

    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            # Prevent deletion if the user is not the author
            raise PermissionDenied(
                "You do not have permission to delete this post."
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # Redirect to the user's profile page after deleting a post
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class UserByUsernameMixin:
    """Mixin for retrieving user by username."""

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        self.user = get_object_or_404(User, username=username)
        return self.user


class ProfilePage(UserByUsernameMixin, PaginatorMixin, LoginRequiredMixin, DetailView):
    """View for displaying user profile page."""

    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs['username'])
        context['profile'] = user
        user_posts = Post.get_published_posts(user=self.request.user, queryset=user.posts)
        page_obj = self.paginate_user_posts(user_posts)
        context['page_obj'] = page_obj
        context['user'] = self.request.user
        return context

    def get_user_posts(self, user):
        """Retrieve and filter user posts based on publication status."""
        user_posts = user.posts.all()
        user_posts = user_posts.prefetch_related('comments').annotate(comment_count=Count('comments')).order_by(*Post._meta.ordering)
        if self.request.user != user:  # If the request user is not the profile owner
            user_posts = user_posts.filter(is_published=True)  # Show only published posts
        return user_posts

    def paginate_user_posts(self, user_posts):
        """Paginate the user's posts."""
        paginator = Paginator(user_posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        return paginator.get_page(page_number)


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    """View for updating user profile."""

    template_name = 'blog/user.html'
    model = User
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_object(self, queryset=None):
        return self.request.user

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Prevent unauthenticated users from accessing the view
            raise PermissionDenied(
                "You do not have permission to edit this profile."
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # Redirect to the user's profile page after updating
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class CommentMixin:
    """Mixin for Comment model views."""

    model = Comment


class CommentFormMixin:
    """Mixin for Comment form views."""

    form_class = CommentCreateForm


class CommentIdMixin:
    """Mixin for views using comment_id in URL."""

    pk_url_kwarg = 'comment_id'


class BackToPostMixin:
    """Mixin for redirecting back to post detail view."""

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse_lazy('blog:post_detail', kwargs={'post_id': post_id})


class CommentCreate(LoginRequiredMixin, CommentFormMixin, CreateView):
    """View for creating a new comment."""

    context_object_name = 'comment'

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        comment.post = post
        comment.save()
        # Redirect to the post detail page after creating a comment
        return HttpResponseRedirect(
            reverse_lazy('blog:post_detail', kwargs={'post_id': post.id})
        )


class CommentUpdate(
    LoginRequiredMixin, CommentIdMixin, CommentMixin,
    CommentFormMixin, BackToPostMixin, UpdateView
):
    """View for updating an existing comment."""

    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            # Prevent editing if the user is not the comment author
            raise PermissionDenied(
                "You do not have permission to edit this comment."
            )
        return super().dispatch(request, *args, **kwargs)


class CommentDelete(
    LoginRequiredMixin, CommentMixin, CommentIdMixin,
    BackToPostMixin, DeleteView
):
    """View for deleting a comment."""

    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            # Prevent deletion if the user is not the comment author
            raise PermissionDenied(
                "You do not have permission to delete this comment."
            )
        return super().dispatch(request, *args, **kwargs)
