from django.test import TestCase

from ..models import Group, Post, User

SLICE_POST = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        task = PostModelTest.post
        model_repr = task.__str__()
        self.assertEqual(model_repr, task.text[:SLICE_POST],
                         f'проверьте что__str__ метод модели {Post.__name__} '
                         f'возвращает значение равное {Post.__name__}'
                         f'.text[:{SLICE_POST}] '
                         )

        task = PostModelTest.group
        model_repr = task.__str__()
        self.assertEqual(model_repr, task.title,
                         f"проверьте что __str__ метод модели {Group.__name__}"
                         f"возвращает значение из поля 'title'"
                         )

    def test_models_have_correct_verbose_names(self):
        """
        Проверяем что у модели Post заданы человеко читаемые имена полей
        """
        task = PostModelTest.post
        field_verboses = {
            'author': 'Автор',
            'text': 'Текст поста',
            'group': 'Группа',
        }
        for field, value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name, value
                )

    def test_models_have_correct_help_text(self):
        """
        Проверяем что у модели Post заданы корректные подсказки для полей
        """
        task = PostModelTest.post
        field_help_texts = {
            'text': 'Опустоши свой разум, будь аморфным, '
                    'бесформенным как вода.',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, value
                )
