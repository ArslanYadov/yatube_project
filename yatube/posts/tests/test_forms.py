from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post


User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_post_create(self):
        """Тестируем, что пост создается."""
        form_data = {
            'text': 'Текст из формы',
            'author': PostCreateFormTests.user,
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post = Post.objects.first()
        group = PostCreateFormTests.group
        self.assertRedirects(
            response,
            reverse('posts:profile', args={post.author})
        )
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, form_data['author'])
        self.assertEqual(group.id, form_data['group'])

    def test_post_create_guest_client(self):
        """
        Проверяем, что не авторизованный пользователь
        перенаправляется залогиниться,
        и такой пост не создается.
        """
        form_data = {
            'text': 'Пост от неавторизованного пользователя',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_create')
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_post_edit_authorized_client(self):
        """
        Проверяем, что авторизированный пользователь может изменить пост.
        При редактировании поста новый не создается.
        """
        new_post = Post.objects.create(
            text='Текст cуществующего поста',
            author=PostCreateFormTests.user,
            group=PostCreateFormTests.group,
        )
        response = self.authorized_client.get(
            reverse('posts:post_edit', args={new_post.id})
        )
        form_data = response.context['form'].initial
        form_data['text'] = 'Отредактированный текст'
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={new_post.id}),
            data=form_data,
            follow=True,
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.text, form_data['text'])
