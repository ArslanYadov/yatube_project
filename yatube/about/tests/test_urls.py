from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class StaticPageURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_for_static_page_exists(self):
        """Проверка доступности URL для статичных страниц."""
        url_name = (
            ('about:author'),
            ('about:tech'),
        )
        for address in url_name:
            with self.subTest(address=address):
                response = self.guest_client.get(reverse(address))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_static_page_templates(self):
        """URL-адрес статичных страниц использует соответствующий шаблон."""
        templates_url_name = (
            ('about:author', 'about/author.html'),
            ('about:tech', 'about/tech.html'),
        )
        for address, template in templates_url_name:
            with self.subTest(address=address):
                response = self.guest_client.get(reverse(address))
                self.assertTemplateUsed(response, template)
