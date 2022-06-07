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
            cls.public_urls = (
                (
                    reverse('posts:index'),
                    'posts/index.html'
                ),
                (
                    reverse('posts:group_list', args={PostURLTests.group.slug}),
                    'posts/group_list.html'
                ),
                (
                    reverse('posts:profile', args={PostURLTests.post.author}),
                    'posts/profile.html'
                ),
                (
                    reverse('posts:post_detail', args={PostURLTests.post.id}),
                    'posts/post_detail.html'
                ),
            )
            cls.private_urls = (
                (reverse('posts:post_create'), 'posts/create_post.html'),
                (
                    reverse('posts:post_edit', args={PostURLTests.post.id}),
                    'posts/create_post.html'
                ),
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
        for url in PostURLTests.public_urls:
            with self.subTest(url=url[0]):
                response = self.guest_client.get(url[0])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_all_urls_response_status_ok_with_authorized_user(self):
        """
        Тестируем существование всех URL-адресов приложения posts,
        доступных авторизированным пользователям.
        """
        posts_urls = PostURLTests.public_urls + PostURLTests.private_urls
        for url in posts_urls:
            with self.subTest(url=url[0]):
                response = self.authorized_client.get(url[0])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_urls_uses_correct_template(self):
        """
        Тестироуем, что публичные URL-адреса приложения posts
        использвуют правильный шаблон.
        """
        for url, template in PostURLTests.public_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_all_urls_uses_correct_template(self):
        """
        Тестироуем, что все URL-адреса приложения posts
        для авторизованного пользователя использвуют правильный шаблон.
        """
        posts_urls = PostURLTests.public_urls + PostURLTests.private_urls
        for url, template in posts_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_access_denied_for_non_authorized_user(self):
        """
        Тестируем недоступность URL-адресов приложения posts
        для не авторизированных пользователей.
        """
        for url in PostURLTests.private_urls:
            with self.subTest(url=url[0]):
                response = self.guest_client.get(url[0])
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_url_posts_uses_redirect_for_non_authorized_user(self):
        """Проверка редиректов для URL-адресов приложения posts."""
        redirect_url_names = (
            (
                reverse('posts:post_edit', args={PostURLTests.post.id}),
                reverse('users:login')
                + '?next='
                + reverse('posts:post_edit', args={PostURLTests.post.id})
            ),
            (
                reverse('posts:post_create'),
                reverse('users:login')
                + '?next='
                + reverse('posts:post_create')
            ),
        )
        for url, redirect_url in redirect_url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_non_exist_url_has_404_page(self):
        """
        Проверяем, что не существующий URL-адрес
        ведет на страницу 404.
        """
        response = self.guest_client.get('/non-exist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
