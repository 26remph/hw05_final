from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

SLICE_POSTS = 10


def index(request):
    """Главная страница"""
    template = 'posts/index.html'

    posts_list = Post.objects.order_by('-pub_date')
    paginator = Paginator(posts_list, SLICE_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'index': True
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Группировка по постам"""
    template = 'posts/group_list.html'

    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.order_by('-pub_date')

    paginator = Paginator(posts_list, SLICE_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Группировка постов по автору
    param: username - автор поста
    """
    user = get_object_or_404(User, username=username)
    posts_list = user.posts.order_by('-pub_date')

    paginator = Paginator(posts_list, SLICE_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    following = (request.user.is_authenticated and user.following.filter(
        author=user, user=request.user
    ).exists())
    context = {
        'author': user,
        'page_obj': page_obj,
        'posts_total': paginator.count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница поста"""
    post = get_object_or_404(Post, pk=post_id)
    posts_total = post.author.posts.count()

    comments = post.comments.order_by('-created')

    context = {
        'post': post,
        'posts_total': posts_total,
        'form': CommentForm(),
        'comments': comments,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """
    Создание поста блога

    param: is_edit = True - определяет, является ли страница редактируемой,
    используется в шаблоне posts/create_post.html для управления видимости
    заголовков кнопок и форм.
    """
    is_edit = False

    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            reverse('posts:profile', args=[request.user]))

    context = {
        'form': form,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Редактирование поста"""
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect(
            reverse('posts:post_detail', args=[post_id])
        )

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if form.is_valid():
        form.save()
        return redirect(
            reverse('posts:post_detail', args=[post_id]))

    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница всех подписок"""
    posts_list = Post.objects.select_related(
        'author'
    ).filter(
        author__following__user=request.user
    )

    paginator = Paginator(posts_list, SLICE_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'follow': True,
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора
    param: username - автор поста
    """
    author = get_object_or_404(User, username=username)
    entry = Follow.objects.filter(
        user=request.user,
        author=author)

    if author != request.user and not entry.exists():
        try:
            Follow.objects.create(user=request.user, author=author)
        except IntegrityError as e:
            messages.error(request,
                           f'Ошибка записи базу данных: {e.args}',
                           extra_tags="alert alert-danger"
                           )

        except BaseException as e:
            messages.error(request, e.args, extra_tags="alert alert-danger")

    return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    """Дизлайк, отписка
    param: username - автор поста
    """
    author = get_object_or_404(User, username=username)
    entry = Follow.objects.filter(user=request.user, author=author)
    if entry.exists():
        entry.delete()

    return redirect(reverse('posts:index'))
