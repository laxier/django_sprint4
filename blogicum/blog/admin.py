from django.contrib import admin
from .models import Post, Location, Category, Comment, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin.site.unregister(User)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'is_published')
    search_fields = ('title', 'text')
    list_filter = ('is_published', 'pub_date', 'category')
    ordering = ('-pub_date',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    search_fields = ('title', 'slug')
    list_filter = ('is_published',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created_at')
    search_fields = ('post__title', 'author__username', 'text')
    list_filter = ('created_at',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin panel configuration for the User model."""

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация',
         {'fields': ('first_name', 'last_name', 'email', 'is_staff', 'is_active', 'is_superuser')}),
        ('Разрешения', {'fields': ('groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'password1', 'password2')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_readonly_fields(self, request, obj=None):
        return ['last_login']
