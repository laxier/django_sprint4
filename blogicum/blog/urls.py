from django.urls import path
from . import views

# App namespace
app_name = "blog"

urlpatterns = [
    # Post routes
    path("", views.PostList.as_view(), name="index"),
    path("posts/<int:post_id>/", views.PostDetail.as_view(),
         name="post_detail"),

    # Comment-related routes
    path('posts/<int:post_id>/comment/', views.CommentCreate.as_view(),
         name="add_comment"),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdate.as_view(), name="edit_comment"),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDelete.as_view(), name="delete_comment"),

    # CRUD operations for Posts
    path("posts/create/", views.PostCreate.as_view(), name="create_post"),
    path("posts/<int:post_id>/delete/", views.PostDelete.as_view(),
         name="delete_post"),
    path("posts/<int:post_id>/edit/", views.PostUpdate.as_view(),
         name="edit_post"),

    # Category-specific posts
    path("category/<slug:category_slug>/", views.CategoryList.as_view(),
         name="category_posts"),

    # Profile-related routes
    path("profile/<str:username>/", views.ProfilePage.as_view(),
         name="profile"),
    path("profile/user/edit/", views.ProfileUpdate.as_view(),
         name="edit_profile"),
]
