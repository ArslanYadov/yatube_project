from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse
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
            text='Тестовый пост',
            group=cls.group
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
        url_names = {
            reverse('posts:index'): 'for_all',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'for_all',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            ): 'for_all',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'for_all',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'only_authorized',
            reverse('posts:post_create'): 'only_authorized',
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
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
