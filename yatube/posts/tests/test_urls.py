from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from ..models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists(self):
        """
        Проверка доступности страниц для не авторизованных
        и авторизованных пользователей.
        """
        group = PostURLTests.group
        post = PostURLTests.post
        url_names = {
            '/': 'for_all',
            f'/group/{group.slug}/': 'for_all',
            f'/profile/{post.author}/': 'for_all',
            f'/posts/{post.pk}/': 'for_all',
            f'/posts/{post.pk}/edit/': 'only_authorized',
            '/create/': 'only_authorized',
            '/unexisting_page/': 'for_all',
        }
        for address in url_names:
            if address != '/unexisting_page/':
                if url_names[address] != 'only_authorized':
                    with self.subTest(address=address):
                        response = self.guest_client.get(address)
                        self.assertEqual(response.status_code, HTTPStatus.OK)
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
            else:
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_uses_redirect(self):
        """Проверка редиректов."""
        post = PostURLTests.post
        redirect_url_names = {
            f'/posts/{post.pk}/edit/': (
                f'/auth/login/?next=/posts/{post.pk}/edit/'
            ),
            '/create/': '/auth/login/?next=/create/',
        }
        for address, template in redirect_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, template)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group = PostURLTests.group
        post = PostURLTests.post
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{post.author}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
