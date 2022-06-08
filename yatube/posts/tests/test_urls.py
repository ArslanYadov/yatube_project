from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse
from posts.models import Post, Group
from django.db import transaction


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with transaction.atomic():
            cls.user = User.objects.create_user(username='auth')
            cls.group = Group.objects.create(
                title='Тестовая группа',
                description='Тестовое описание'
            )
            cls.post = Post.objects.create(
                author=PostURLTests.user,
                text='Тестовый пост',
                group=PostURLTests.group
            )
        cls.index_url = (
            'posts:index',
            'posts/index.html',
            ()
        )
        cls.group_list_url = (
            'posts:group_list',
            'posts/group_list.html',
            (PostURLTests.group.slug,)
        )
        cls.profile_url = (
            'posts:profile',
            'posts/profile.html',
            (PostURLTests.post.author,)
        )
        cls.post_detail_url = (
            'posts:post_detail',
            'posts/post_detail.html',
            (PostURLTests.post.id,)
        )
        cls.post_create_url = (
            'posts:post_create',
            'posts/create_post.html',
            ()
        )
        cls.post_edit_url = (
            'posts:post_edit',
            'posts/create_post.html',
            (PostURLTests.post.id,)
        )
        cls.public_urls = (
            PostURLTests.index_url,
            PostURLTests.group_list_url,
            PostURLTests.profile_url,
            PostURLTests.post_detail_url
        )
        cls.private_urls = (
            PostURLTests.post_create_url,
            PostURLTests.post_edit_url
        )
        cls.all_post_app_urls = (
            PostURLTests.public_urls + PostURLTests.private_urls
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_public_urls_response_status_ok(self):
        """
        Тестируем существование URL-адресов приложения posts,
        доступных всем пользователям.
        """
        for name, _, args in PostURLTests.public_urls:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_all_urls_response_status_ok_with_authorized_user(self):
        """
        Тестируем существование всех URL-адресов приложения posts,
        доступных авторизированным пользователям.
        """
        for name, _, args in PostURLTests.all_post_app_urls:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_urls_uses_correct_template(self):
        """
        Тестироуем, что публичные URL-адреса приложения posts
        использвуют правильный шаблон.
        """
        for name, template, args in PostURLTests.public_urls:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name, args=args))
                self.assertTemplateUsed(response, template)

    def test_all_urls_uses_correct_template(self):
        """
        Тестироуем, что все URL-адреса приложения posts
        для авторизованного пользователя использвуют правильный шаблон.
        """
        for name, template, args in PostURLTests.all_post_app_urls:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name, args=args))
                self.assertTemplateUsed(response, template)

    def test_url_access_denied_for_non_authorized_user(self):
        """
        Тестируем недоступность URL-адресов приложения posts
        для не авторизированных пользователей.
        """
        for name, _, args in PostURLTests.private_urls:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_url_posts_uses_redirect_for_non_authorized_user(self):
        """Проверка редиректов для URL-адресов приложения posts."""
        for name, _, args in PostURLTests.private_urls:
            with self.subTest(name=name):
                response = self.guest_client.get(
                    reverse(name, args=args),
                    follow=True
                )
                self.assertRedirects(
                    response,
                    reverse('users:login')
                    + '?next='
                    + reverse(name, args=args)
                )

    def test_non_exist_url_has_404_page(self):
        """
        Проверяем, что не существующий URL-адрес
        ведет на страницу 404.
        """
        response = self.guest_client.get('/non-exist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
