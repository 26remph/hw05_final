from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from ..models import Group, Post, User


class PostsViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post text',
            group=cls.group
        )
        cls.url_index = reverse('posts:index')
        cls.url_group_list = reverse('posts:group_list', args=[cls.group.slug])
        cls.url_profile = reverse('posts:profile', args=[cls.user.username])
        cls.url_post_detail = reverse('posts:post_detail', args=[cls.post.pk])
        cls.url_post_edit = reverse('posts:post_edit', args=[cls.post.pk])
        cls.url_post_create = reverse('posts:post_create')

        cls.template_pages_name = {
            'posts/index.html': [cls.url_index],
            'posts/group_list.html': [cls.url_group_list],
            'posts/profile.html': [cls.url_profile],
            'posts/post_detail.html': [cls.url_post_detail],
            'posts/create_post.html': [cls.url_post_edit, cls.url_post_create],
        }

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_url_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_keys in self.template_pages_name.items():
            for reverse_name in reverse_keys:
                with self.subTest(reverse_name=reverse_name):
                    response = self.auth_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)


class PaginatorViewTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )
        cls.group_without_post = Group.objects.create(
            title='Group without post',
            slug='group-without-post',
            description='This is an empty group, that does not contain posts'
        )
        cls.posts = mixer.cycle(13).blend(
            Post,
            author=cls.user,
            group=cls.group
        )

        cls.urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[cls.group.slug]),
            reverse('posts:profile', args=[cls.user.username]),
        ]
        cls.url_group_without_post = reverse(
            'posts:group_list', args=[cls.group_without_post.slug]
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.last_post_with_group = self.posts[12]

    def test_first_page_contains_ten_records(self):
        """Тестирование paginator первая страница"""
        response = self.auth_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Тестирование paginator вторая страница"""
        response = self.auth_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_posts_list_page_show_correct_context(self):
        """Пост попадает в указанную группу на главной странице,
        страницы выбранной группы постов, в профайл пользователя, """
        for url in self.urls:
            response = self.auth_client.get(url)
            try:
                posts = response.context.get('page_obj').object_list
            except Exception as e:
                self.assertFalse(
                    False,
                    f'Ошибка {e} при получении контекст страницы {url}, '
                    f'проверьте что предаете в контекст ключ `page_obj`'
                )

            with self.subTest(post=self.last_post_with_group):
                self.assertTrue(
                    self.last_post_with_group in posts,
                    f'Пост {self.last_post_with_group} c группой {self.group} '
                    f'отсутствует на странице {url}'
                )

    def test_post_located_in_incorrect_group(self):
        """Пост не попал в группу, для которой не был предназначен."""
        response = self.auth_client.get(self.url_group_without_post)
        try:
            context_page = response.context.get('page_obj').object_list
        except Exception as e:
            self.assertFalse(
                False,
                f'Ошибка {e} при получении контекст страницы '
                f'{self.url_group_without_post}, '
                f'проверьте что предаете в контекст ключ `page_obj`'
            )
        self.assertEqual(
            len(context_page),
            0,
            f'Посты {context_page} попадают на страницу группы'
            f'`{self.group_without_post.slug}` которая, по определению теста '
            f'не должна содержит постов.'
        )
