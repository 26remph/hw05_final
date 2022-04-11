import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.paginator_gif = SimpleUploadedFile(
            name='paginator.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.edit_gif = SimpleUploadedFile(
            name='edit.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.create_gif = SimpleUploadedFile(
            name='create.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )
        cls.edit_post = Post.objects.create(
            author=cls.user,
            text='Editable post for inserting image',
            group=cls.group,
        )
        cls.edit_post_id = cls.edit_post.pk

        cls.post_with_image = Post.objects.create(
            author=cls.user,
            text='Test post for check image in context',
            group=cls.group,
            image=cls.paginator_gif
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_post_with_image(self):
        """Валидная форма `post_create` создает запись с картинкой в Post."""
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Создан пост с картинкой.',
            'image': self.create_gif,
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.user])
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Создан пост с картинкой.',
                image='posts/create.gif'
            ).exists()
        )

    def test_edit_post_with_image(self):
        """Валидная форма из `post_edit` создает запись с картинкой в Post."""
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Отредактирован пост с картинкой.',
            'group': self.group.pk,
            'image': self.edit_gif,
        }
        url = reverse('posts:post_edit', args=[self.edit_post.pk])
        response = self.auth_client.post(
            url,
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[self.edit_post.pk])
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Отредактирован пост с картинкой.',
                group=self.group,
                image='posts/edit.gif'
            ).exists()
        )

    def test_paginator_context_page_post_with_image(self):
        """Картинка на страницах с paginator, передаётся в `context` шаблона"""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=['test-slug']),
            reverse('posts:profile', args=['auth']),
        ]

        for url in urls:
            response = self.auth_client.get(url)
            try:
                posts = list(response.context.get('page_obj').object_list)
            except Exception as e:
                self.assertFalse(
                    False,
                    f'Ошибка {e} при получении контекст страницы {url}, '
                    f'проверьте что предаете в контекст ключ `page_obj`'
                    f'или `post'
                )

            try:
                ind = posts.index(self.post_with_image)
            except ValueError:
                self.assertFalse(
                    False,
                    f'Post создан {self.post_with_image}, но не передается'
                    f'в `context` страницы {url}.')

            with self.subTest(url=url):
                self.assertEqual(
                    posts[ind].image,
                    self.post_with_image.image,
                    f'Картинка поста `{self.post_with_image.image}` и'
                    f'картинка в `context` {posts[ind].image} страницы '
                    f'отличаются .')

    def test_post_detail_page_with_image(self):
        """Картинка на posts/<int:post_id>/, передаётся в context шаблона"""
        url = reverse('posts:post_detail', args=[self.post_with_image.pk])
        response = self.auth_client.get(url)
        post = response.context['post']
        self.assertEqual(
            post.image,
            self.post_with_image.image,
            f'Картинка поста `{self.post_with_image.image}` и'
            f'картинка в `context` {post.image} страницы '
            f'отличаются .'
        )
