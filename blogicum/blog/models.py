from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

help_text = 'Снимите галочку, чтобы скрыть публикацию.'


class BaseModel(models.Model):
    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликовано',
                                       help_text=help_text)
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        abstract = True


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

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    @classmethod
    def get_published_posts(cls, n=None):
        queryset = cls.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
        return queryset if n is None else queryset[:n]


class Location(BaseModel):
    name = models.CharField(max_length=256,
                            verbose_name='Название места')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


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


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    text = models.TextField(verbose_name='текст комментария')
