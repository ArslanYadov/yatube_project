from django.test import TestCase
from http import HTTPStatus


class CoreViewTest(TestCase):
    def test_error_page_404_has_correct_status(self):
        """Тестируем статус страницы с ошибкой 404."""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )

    def test_error_page_404_use_correct_template(self):
        """
        Тестируем, что страница с ошибкой 404
        использует правильный щаблон.
        """
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
