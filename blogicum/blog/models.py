from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# BaseModel contains common fields for other models to inherit
class BaseModel(models.Model):
    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликовано',
                                       help_text=('Снимите галочку, ',
                                                  'чтобы скрыть публикацию.'))
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        abstract = True


# Post model represents a blog post
class Post(BaseModel):
    title = models.CharField(max_length=256, verbose_name='Название')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            "Если установить дату и время в будущем — "
            "можно делать отложенные публикации."
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        'Category',
        # on_delete=models.PROTECT, обязтельный но может быть нуль? ладно
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField('Фото', upload_to='blog_images', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    # Method to get published posts, limit the number of posts returned
    @classmethod
    def get_published_posts(cls, user=None, queryset=None, n=None):
        """
        Returns published posts or all posts for the author.
        - If a user is provided and they are the author, unpublished posts will be included.
        - If no user is provided or the user is not the author, only published posts are returned.
        """
        if queryset is None:
            queryset = cls.objects.all()

        # If the user is provided, include the user's own posts (including unpublished)
        if user is not None:
            queryset = queryset.filter(
                models.Q(author=user) | (
                        models.Q(pub_date__lte=timezone.now()) &
                        models.Q(is_published=True) &
                        models.Q(category__is_published=True)
                )
            )
        else:

            queryset = queryset.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True
            )
        queryset = queryset.annotate(comment_count=models.Count('comments')).order_by(*cls._meta.ordering)
        return queryset if n is None else queryset[:n]

# Location model represents a place associated with posts
class Location(BaseModel):
    name = models.CharField(max_length=256,
                            verbose_name='Название места')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


# Category model represents a category for posts
class Category(BaseModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(unique=True, verbose_name='Идентификатор',
                            help_text=(
                                "Идентификатор страницы для URL; "
                                "разрешены символы латиницы, цифры, "
                                "дефис и подчёркивание."))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


# Comment model represents comments on posts
class Comment(models.Model):
    # Post associated with the comment
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    # the author
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    text = models.TextField(verbose_name='текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
