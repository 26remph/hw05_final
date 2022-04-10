from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q

SLICE_POST = 15

User = get_user_model()


class Group(models.Model):

    title = models.CharField(
        max_length=200,
        help_text='Title group'
    )
    slug = models.SlugField(unique=True)
    description = models.TextField()

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Post(models.Model):

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Опустоши свой разум, будь аморфным, бесформенным как вода.'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:SLICE_POST]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    created = models.DateTimeField(
        'Дата поста',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', 'author'], name='user_author'),
        ]
        constraints = [
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='user_not_author'),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
