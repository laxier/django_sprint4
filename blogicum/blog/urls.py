from django.urls import path
from . import views
app_name = "blog"

urlpatterns = [
    path("", views.PostList.as_view(), name="index"),
    path("posts/<int:post_id>/", views.PostDetail.as_view(),
         name="post_detail"),
    path("category/<slug:category_slug>/", views.CategoryList.as_view(),
         name="category_posts")
]
