from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Post, User


class TestComments(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Editable post for inserting image',
        )
        cls.post_id = cls.post.pk

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария для проверки шаблона',
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_allow_comment_only_auth_user(self):
        """Check comments allow, only auth users"""
        url = reverse('posts:add_comment', args=[self.post_id])
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post_id}/comment/'
        )

    def test_post_form_comments(self):
        """Post valid form `CommentForm` check """
        tasks_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'author': self.user,
            'text': 'Текст комментария.',
        }
        url = reverse('posts:add_comment', args=[self.post_id])
        response = self.auth_client.post(
            url,
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[self.post_id])
        )
        self.assertEqual(Comment.objects.count(), tasks_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                post=self.post,
            ).exists()
        )

    def test_get_post_comment_correct(self):
        """Comment on posts/1/comment/', transfer in context template"""
        url = reverse('posts:post_detail', args=[self.post_id])
        response = self.auth_client.get(url, follow=True)
        comments = response.context['comments']
        self.assertTrue(
            self.comment in comments,
            f'Comment {self.comment} поста `{self.post}` не передается'
            f'в словарь context. Cтраница шаблона {url}'
        )
