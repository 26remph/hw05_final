from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from ..models import Follow, Post, User


class TestComments(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_mike = User.objects.create_user(username='mike')
        cls.user_gretta = User.objects.create_user(username='gretta')

        cls.author_leo = User.objects.create_user(username='leo')
        cls.author_steven = User.objects.create_user(username='steven')

        cls.posts_leo = mixer.cycle(4).blend(
            Post,
            author=cls.author_leo,
        )
        cls.posts_steven = mixer.cycle(2).blend(
            Post,
            author=cls.author_steven,
        )

        Follow.objects.create(
            user=cls.user_mike,
            author=cls.author_steven,
        )

        Follow.objects.create(
            user=cls.user_gretta,
            author=cls.author_steven,
        )
        cls.anonymous = 'anonymous'

        cls.view_follow_index = 'posts:follow_index'
        cls.view_profile_follow = 'posts:profile_follow'
        cls.view_profile_unfollow = 'posts:profile_unfollow'

        cls.url_follow_index = '/follow/'
        cls.url_profile_follow = f'/profile/{cls.author_leo.username}/follow/'
        cls.url_profile_unfollow = (f'/profile/'
                                    f'{cls.author_leo.username}/unfollow/')

        cls.template_for_auth_client = {
            cls.url_follow_index: 'posts/follow.html',
        }

    def setUp(self):
        self.auth_mike = Client()
        self.auth_mike.force_login(self.user_mike)
        self.auth_gretta = Client()
        self.auth_gretta.force_login(self.user_mike)

    def test_allow_subscribe_only_auth_user(self):
        """Check subscribe allow, only auth users"""
        url = reverse(self.view_follow_index)
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/follow/')

        url = reverse(self.view_profile_follow, args=[self.anonymous])
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            '/auth/login/?next=/profile/anonymous/follow/')

    def test_url_uses_correct_redirect(self):
        """
        Проверка редиректа после подписки/отписки.
        """
        url = reverse(
            self.view_profile_follow,
            args=[self.author_leo.username])
        response = self.auth_mike.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.author_leo.username])
        )

        url = reverse(
            self.view_profile_unfollow,
            args=[self.author_leo.username])
        response = self.auth_mike.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('posts:index')
        )

    def test_url_uses_correct_templates(self):
        """
        URL-адрес использует соответствующий шаблон.
        """
        for url, template in self.template_for_auth_client.items():
            with self.subTest(url=url, user=self.user_mike.username):
                response = self.auth_mike.get(url)
                self.assertTemplateUsed(response, template)

    def test_follow_index_page_receive_context(self):
        """page posts/follow/' receive expected context in her template"""
        url = reverse(self.view_follow_index)
        response = self.auth_mike.get(url, follow=True)
        context_posts = response.context.get('page_obj').object_list

        authors = self.user_mike.follower.values('author_id')
        expected_posts = Post.objects.select_related(
            'author'
        ).filter(
            author__in=authors
        )
        self.assertEqual(
            context_posts, list(expected_posts),
            f'Список {context_posts} постов контекста '
            f'страницы {url}'
            f'не соответствует ожидаемому {expected_posts}'
        )

    def test_add_entry_in_follow(self):
        """Тестируем добавление записей в базу"""
        count = Follow.objects.count()
        url = reverse(
            self.view_profile_follow,
            args=[self.author_leo.username]
        )
        self.auth_mike.get(url, follow=True)
        self.assertEqual(Follow.objects.count(), count + 1)

        following = self.user_mike.follower.filter(
            author=self.author_leo,
            user=self.user_mike
        ).exists()
        self.assertTrue(following)

    def test_delete_entry_in_follow(self):
        """Тестируем удаление записей в базу"""
        count = Follow.objects.count()

        url = reverse(
            self.view_profile_unfollow,
            args=[self.author_steven.username]
        )
        self.auth_mike.get(url, follow=True)
        self.assertEqual(Follow.objects.count(), count - 1)

        following = self.user_mike.follower.filter(
            author=self.author_steven,
            user=self.user_mike
        ).exists()
        self.assertFalse(following)
