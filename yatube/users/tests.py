from django.urls import reverse
from django.test import TestCase, Client
from http import HTTPStatus
from django.contrib.auth import get_user_model


User = get_user_model()


class UserURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_url_exists(self):
        """Проверка доступности страниц приложения users."""
        url_names = {
            '/auth/signup/': 'for_all',
            '/auth/logout/': 'for_all',
            '/auth/login/': 'for_all',
            '/auth/password_change/': 'only_authorized',
            '/auth/password_change/done/': 'only_authorized',
            '/auth/password_reset/': 'for_all',
            '/auth/password_reset/done/': 'for_all',
            '/auth/reset/<uidb64>/<token>/': 'for_all',
            '/auth/reset/done/': 'for_all',
        }
        for address in url_names:
            if url_names[address] != 'only_authorized':
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
            else:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_url_redirect(self):
        """Проверка редиректа для приложения users."""
        url_redirect = {
            '/auth/password_change/': (
                '/auth/login/?next=/auth/password_change/'
            ),
            '/auth/password_change/done/': (
                '/auth/login/?next=/auth/password_change/done/'
            ),
        }
        for address, template in url_redirect.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, template)

    def test_urls_users_correct_template(self):
        """
        URL-адрес приложения users использует соответствующий шаблон
        для не авторизованных пользователей.
        """
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/': (
               'users/password_reset_confirm.html'
            ),
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_users_correct_template_authorized(self):
        """
        URL-адрес приложения users использует соответствующий шаблон
        для авторизованных пользователей.
        """
        templates_url_names = {
            'users:password_change': 'users/password_change_form.html',
            'users:password_change_done': 'users/password_change_done.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(reverse(address))
                self.assertTemplateUsed(response, template)
