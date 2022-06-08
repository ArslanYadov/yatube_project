from django.urls import reverse
from django.test import TestCase, Client
from http import HTTPStatus
from django.contrib.auth import get_user_model


User = get_user_model()


class UserURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login_url = ('users:login', ())
        cls.logout_url = ('users:logout', ())
        cls.signup_url = ('users:signup', ())
        cls.password_change_url = ('users:password_change', ())
        cls.password_change_done_url = ('users:password_change_done', ())
        cls.password_reset_url = ('users:password_reset', ())
        cls.password_reset_done_url = ('users:password_reset_done', ())
        cls.password_reset_confirm_url = (
            'users:password_reset_confirm',
            ('uidb64', 'token')
        )
        cls.password_reset_complete_url = ('users:password_reset_complete', ())
        cls.public_urls = (
            UserURLTest.login_url,
            UserURLTest.logout_url,
            UserURLTest.signup_url,
            UserURLTest.password_reset_url,
            UserURLTest.password_reset_done_url,
            UserURLTest.password_reset_confirm_url,
            UserURLTest.password_reset_complete_url
        )
        cls.private_urls = (
            UserURLTest.password_change_url,
            UserURLTest.password_change_done_url
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_url_exists(self):
        """Проверка доступности страниц приложения users."""
        for name, args in UserURLTest.public_urls:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for name, _ in UserURLTest.private_urls:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_url_redirect(self):
        """Проверка редиректа для приложения users."""
        login_url_name, _ = UserURLTest.login_url
        for name, args in UserURLTest.private_urls:
            with self.subTest(name=name):
                response = self.guest_client.get(
                    reverse(name, args=args),
                    follow=True
                )
                self.assertRedirects(
                    response,
                    reverse(login_url_name)
                    + '?next='
                    + reverse(name, args=args)
                )
