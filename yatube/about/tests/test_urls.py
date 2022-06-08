from django.test import TestCase, Client
from django.urls import reverse


class StaticPageViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_url = ('about:author', 'about/author.html')
        cls.tech_url = ('about:tech', 'about/tech.html')
        cls.about_app_urls = (
            StaticPageViewsTests.author_url,
            StaticPageViewsTests.tech_url
        )

    def setUp(self):
        self.guest_client = Client()

    def test_url_for_static_page_templates(self):
        """URL-адрес статичных страниц использует соответствующий шаблон."""
        for name, template in StaticPageViewsTests.about_app_urls:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
