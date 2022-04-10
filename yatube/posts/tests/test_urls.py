from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.other_user = User.objects.create_user(username='auth_other')
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
        cls.url_edit_post = f'/posts/{str(cls.post.pk)}/edit/'
        cls.url_expected_for_redirect = f'/posts/{cls.post.pk}/'
        cls.url_404 = '/unexisting_page/'

        cls.template_for_all_client = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }
        cls.template_for_auth_client = {
            cls.url_edit_post: 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        self.authorized_other_client = Client()
        self.authorized_other_client.force_login(PostsURLTests.other_user)

    def test_url_uses_correct_templates(self):
        """
        URL-адрес использует соответствующий шаблон.
        """
        for url, template in self.template_for_all_client.items():
            with self.subTest(url=url, user='anonymous'):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

            with self.subTest(url=url, user='auth'):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_uses_correct_redirect(self):
        """
        Проверка редиректа для страниц требующих авторизации.
        """
        for url, template in self.template_for_auth_client.items():

            with self.subTest(url=url, user='anonymous'):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, f'/auth/login/?next={url}')

    def test_url_uses_correct_redirect_for_edit_post_page(self):
        """
        Проверка редиректа страницы автора поста.
        """
        response = self.authorized_other_client.get(
            self.url_edit_post, follow=True
        )
        self.assertRedirects(
            response,
            expected_url=self.url_expected_for_redirect,
            msg_prefix='Страница автора поста доступна для редактирования '
                       'всем авторизированным пользователям!'
        )

    def test_url_unexisting_page_404(self):
        """
        Проверка на несуществующую страницу.
        """
        response = self.guest_client.get(self.url_404)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
