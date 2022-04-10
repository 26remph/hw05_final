from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )

        cls.post_for_edit = Post.objects.create(
            author=cls.user,
            text='Text before editing',
            group=cls.group
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_new_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()

        form_data = {
            'group': self.group.pk,
            'text': 'Test post text',
        }

        self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        with self.subTest(msg='Save form data:', form_data=form_data):
            self.assertEqual(Post.objects.count(), post_count + 1)
            self.assertTrue(
                Post.objects.filter(
                    group=self.group,
                    text='Test post text',
                    author=self.user
                ).exists(),
            )

    def test_edit_post_database_changed(self):

        form_data = {
            'group': self.group.pk,
            'text': 'Text after editing',
        }

        self.auth_client.post(
            reverse('posts:post_edit', args=[self.post_for_edit.pk]),
            data=form_data,
            follow=True
        )
        text_after = Post.objects.get(pk=self.post_for_edit.pk).text
        self.assertMultiLineEqual(
            text_after,
            'Text after editing',
            f'Post_id `{self.post_for_edit.pk}`, author `{self.user}`, '
            f'текст {self.post_for_edit.text} не сохраняет редактирования.'
        )
