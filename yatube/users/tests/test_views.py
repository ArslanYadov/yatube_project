from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model


User = get_user_model()


class UserViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login_url = (
            'users:login',
            'users/login.html',
            ()
        )
        cls.logout_url = (
            'users:logout',
            'users/logged_out.html',
            ()
        )
        cls.signup_url = (
            'users:signup',
            'users/signup.html',
            ()
        )
        cls.password_change_url = (
            'users:password_change',
            'users/password_change_form.html',
            ()
        )
        cls.password_change_done_url = (
            'users:password_change_done',
            'users/password_change_done.html',
            ()
        )
        cls.password_reset_url = (
            'users:password_reset',
            'users/password_reset_form.html',
            ()
        )
        cls.password_reset_done_url = (
            'users:password_reset_done',
            'users/password_reset_done.html',
            ()
        )
        cls.password_reset_confirm_url = (
            'users:password_reset_confirm',
            'users/password_reset_confirm.html',
            ('uidb64', 'token')
        )
        cls.password_reset_complete_url = (
            'users:password_reset_complete',
            'users/password_reset_complete.html',
            ()
        )
        cls.public_urls = (
            UserViewsTest.login_url,
            UserViewsTest.logout_url,
            UserViewsTest.signup_url,
            UserViewsTest.password_reset_url,
            UserViewsTest.password_reset_done_url,
            UserViewsTest.password_reset_confirm_url,
            UserViewsTest.password_reset_complete_url
        )
        cls.private_urls = (
            UserViewsTest.password_change_url,
            UserViewsTest.password_change_done_url
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_users_correct_template(self):
        """
        URL-адрес приложения users использует соответствующий шаблон
        для не авторизованных пользователей.
        """
        for name, template, args in UserViewsTest.public_urls:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name, args=args))
                self.assertTemplateUsed(response, template)

    def test_urls_users_correct_template_authorized(self):
        """
        URL-адрес приложения users использует соответствующий шаблон
        для авторизованных пользователей.
        """
        for name, template, _ in UserViewsTest.private_urls:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
