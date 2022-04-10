from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User


class TestCache(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Post for test cache.',
        )
        cls.first_page = 1

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_index_page_key_in_templates(self):
        """Проверка наличия ключа `index_page` в post/index.html"""

        self.client.get(reverse('posts:index'))

        key = make_template_fragment_key('index_page', [self.first_page])
        self.assertIsNotNone(
            cache.get(key),
            'Cache key `index page page_obj.number` not present in templates'
        )

    def test_posts_in_cache(self):
        """Проверка кеширования контента post/index.html"""
        response = self.client.get(reverse('posts:index'))
        content_before = response.content
        self.assertTrue(self.post in response.context['page_obj'])

        self.post.delete()

        content_after = self.client.get(reverse('posts:index')).content
        self.assertEqual(content_before, content_after)

        cache.clear()

        content_clear = self.client.get(reverse('posts:index')).content
        self.assertNotEqual(content_before, content_clear)
