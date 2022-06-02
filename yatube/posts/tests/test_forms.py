from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
from http import HTTPStatus


User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.group.id)
        author = User.objects.get(username='auth')
        group = Group.objects.get(title='Тестовая группа')
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': post.author})
        )
        self.assertEqual(post.text, 'Текст из формы')
        self.assertEqual(author.username, 'auth')
        self.assertEqual(group.title, 'Тестовая группа')

    def test_post_create_guest_client(self):
        """
        Проверяем, что не авторизованный пользователь
        не может создать пост.
        """
        form_data = {
            'text': 'Пост от неавторизованного пользователя',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(
            Post.objects.filter(
                text='Пост от неавторизованного пользователя'
                ).exists()
        )

    def test_post_edit_authorized_client(self):
        """Проверяем, что авторизированный пользователь может изменить пост."""
        create_form_data = {
            'text': 'Текст из формы',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=create_form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.group.id)
        self.client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.id})
        )
        edit_form_data = {
            'text': 'Измененный текст из формы',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=edit_form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.group.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.text, 'Измененный текст из формы')
