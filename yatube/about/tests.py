from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class TestTemplateView(TestCase):
    """Тестирование URL приложения 'about'"""
    def setUp(self):
        self.guest_client = Client()

    def test_uses_url(self):
        urls = ['/about/author/', '/about/tech/']
        for url in urls:
            with self.subTest(user='anonymous', url=urls):
                try:
                    response = self.guest_client.get(url)
                except Exception as e:
                    self.asserFalse(
                        False,
                        msg=f"Страница {url} работает не правильно. "
                            f"Ошибка {e}")

                self.assertNotEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND,
                    f'Страница `{url}` не найдена, '
                    f'проверьте этот адрес в *urls.py*'
                )
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Ошибка {response.status_code} при открытиии `{url}`. '
                    f'Проверьте ее view-функцию'
                )
