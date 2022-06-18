import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from PIL import Image
from io import BytesIO
from http import HTTPStatus


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='TestSlug',
            description='Тестовое описание'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def get_image_file(self):
        image = Image.new('RGBA', size=(1, 1), color=(0, 0, 0))
        image_file = BytesIO()
        image.save(image_file, 'gif')
        image_file.seek(0)
        file = SimpleUploadedFile(
            name='small.gif',
            content=image_file.read()
        )
        return file

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
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        group = PostCreateFormTests.group
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(post.author,))
        )
        form_fields = (
            (post.text, form_data['text']),
            (post.author, form_data['author']),
            (group.id, form_data['group']),
        )
        for value, expected in form_fields:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_post_create_with_image(self):
        """Тестируем создание поста с картинкой."""
        form_data = {
            'text': 'Текст из формы',
            'author': PostCreateFormTests.user,
            'group': PostCreateFormTests.group.id,
            'image': self.get_image_file()
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        group = PostCreateFormTests.group
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(post.author,))
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = (
            (post.text, form_data['text']),
            (post.author, form_data['author']),
            (group.id, form_data['group']),
            (post.image, response.context['post'].image),
        )
        for value, expected in form_fields:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

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
        new_group = Group.objects.create(
            title='Новая группа',
            slug='NewSlug'
        )
        new_post = Post.objects.create(
            text='Текст cуществующего поста',
            author=PostCreateFormTests.user,
            group=new_group,
        )
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=(new_post.id,))
        )
        form_data = response.context['form'].initial
        form_data['text'] = 'Отредактированный текст'
        form_data['image'] = ''
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(new_post.id,)),
            data=form_data,
            follow=True,
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertNotEqual(post.group, PostCreateFormTests.group.id)
