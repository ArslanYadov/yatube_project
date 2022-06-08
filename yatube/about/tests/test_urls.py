from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class StaticPageURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_url = ('about:author', 'about/author.html')
        cls.tech_url = ('about:tech', 'about/tech.html')
        cls.about_app_urls = (
            StaticPageURLTests.author_url,
            StaticPageURLTests.tech_url
        )

    def setUp(self):
        self.guest_client = Client()

    def test_url_for_static_page_exists(self):
        """Проверка доступности URL для статичных страниц."""
        for name, _ in StaticPageURLTests.about_app_urls:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_static_page_templates(self):
        """URL-адрес статичных страниц использует соответствующий шаблон."""
        for name, template in StaticPageURLTests.about_app_urls:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
