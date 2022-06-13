import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django import forms
from posts.models import Post, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from yatube.settings import MEDIA_ROOT


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=MEDIA_ROOT)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание'
        )
        cls.small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostPagesTests.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
            image=PostPagesTests.uploaded
        )
        cls.index_url = (
            'posts:index',
            'posts/index.html',
            ()
        )
        cls.group_list_url = (
            'posts:group_list',
            'posts/group_list.html',
            (PostPagesTests.group.slug,)
        )
        cls.profile_url = (
            'posts:profile',
            'posts/profile.html',
            (PostPagesTests.post.author,)
        )
        cls.post_detail_url = (
            'posts:post_detail',
            'posts/post_detail.html',
            (PostPagesTests.post.id,)
        )
        cls.post_create_url = (
            'posts:post_create',
            'posts/create_post.html',
            ()
        )
        cls.post_edit_url = (
            'posts:post_edit',
            'posts/create_post.html',
            (PostPagesTests.post.id,)
        )
        cls.add_comment_url = (
            'posts:add_comment',
            'posts/post_detail.html',
            (PostPagesTests.post.id,)
        )
        cls.all_posts_app_urls = (
            PostPagesTests.index_url,
            PostPagesTests.group_list_url,
            PostPagesTests.profile_url,
            PostPagesTests.post_detail_url,
            PostPagesTests.post_create_url,
            PostPagesTests.post_edit_url
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        self.authorized_client_for_comment = Client()
        self.authorized_client_for_comment.force_login(
            User.objects.create(username='CommentUser')
        )

    def get_context_from_response(self, response_obj, context_name):
        """Функция для проверки контекста в тестах."""
        if context_name == 'page_obj' or context_name == 'post':
            object_list = (
                (response_obj.text, PostPagesTests.post.text),
                (response_obj.author, PostPagesTests.post.author),
                (response_obj.group.title, PostPagesTests.group.title),
                (response_obj.image, PostPagesTests.post.image),
            )
        if context_name == 'group':
            object_list = (
                (response_obj.title, PostPagesTests.group.title),
                (response_obj.slug, PostPagesTests.group.slug),
                (response_obj.description, PostPagesTests.group.description),
            )
        for value, expected in object_list:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_pages_show_correct_template(self):
        """URL-адрес view-функций posts использует соответствующий шаблон."""
        for name, template, args in PostPagesTests.all_posts_app_urls:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name, args=args))
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        name, _, _ = PostPagesTests.index_url
        response = self.authorized_client.get(reverse(name))
        self.get_context_from_response(
            response.context['page_obj'][0],
            'page_obj'
        )

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        name, _, args = PostPagesTests.group_list_url
        response = self.authorized_client.get(
            reverse(name, args=args)
        )
        context_list = (
            (response.context['page_obj'][0], 'page_obj'),
            (response.context['group'], 'group'),
        )
        for response_obj, context_name in context_list:
            self.get_context_from_response(response_obj, context_name)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        name, _, args = PostPagesTests.profile_url
        response = self.authorized_client.get(
            reverse(name, args=args)
        )
        self.get_context_from_response(
            response.context['page_obj'][0],
            'page_obj'
        )
        self.assertEqual(
            response.context['author'].username,
            PostPagesTests.post.author.username
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        name, _, args = PostPagesTests.post_detail_url
        response = self.authorized_client.get(
            reverse(name, args=args)
        )
        self.get_context_from_response(response.context['post'], 'post')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        name, _, _ = PostPagesTests.post_create_url
        response = self.authorized_client.get(
            reverse(name)
        )
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.models.ModelChoiceField),
            ('image', forms.fields.ImageField),
        )
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        name, _, args = PostPagesTests.post_edit_url
        response = self.authorized_client.get(
            reverse(name, args=args)
        )
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.models.ModelChoiceField),
            ('image', forms.fields.ImageField),
        )
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.get_context_from_response(response.context['post'], 'post')

    def test_post_create_with_group(self):
        """
        Проверка, что при создании поста с группой, она появится:
        - на главной странице сайта,
        - на странице выбранной группы,
        - в профайле пользователя.
        """
        name, _, _ = PostPagesTests.post_create_url
        form_data = {
            'text': 'Тестовый пост1',
            'group': PostPagesTests.group.id,
        }
        response = self.authorized_client.post(
            reverse(name),
            data=form_data,
            follow=True
        )
        url_list = (
            PostPagesTests.index_url,
            PostPagesTests.group_list_url,
            PostPagesTests.profile_url,
        )
        post = Post.objects.last()
        for name, _, args in url_list:
            with self.subTest(name=name):
                response = self.client.get(
                    reverse(name, args=args)
                )
                self.assertContains(response, post.text)

    def test_non_authorized_user_can_not_comment_post(self):
        """
        Не авторизированный пользователь не может комментить посты.
        """
        name, _, args = PostPagesTests.add_comment_url
        self.client.post(
            reverse(name, args=args),
            data={
                'text': 'Комментарий к посту',
            },
            follow=True
        )
        post = Post.objects.first()
        self.assertEqual(post.comments.count(), 0)

    def test_authorized_user_can_comment_post(self):
        """
        Авторизированный пользователь может комментить посты.
        """
        name, _, args = PostPagesTests.add_comment_url
        self.authorized_client_for_comment.post(
            reverse(name, args=args),
            data={
                'text': 'Комментарий к посту',
            },
            follow=True
        )
        post = Post.objects.first()
        comment = post.comments.first()
        self.assertEqual(post.comments.count(), 1)
        self.assertNotEqual(comment.author, post.author)
        name, _, args = PostPagesTests.post_detail_url
        response = self.client.get(
            reverse(name, args=args)
        )
        self.assertContains(response, comment.text)

    def test_paginator(self):
        """Тестируем паджинацию."""
        POSTS_AMOUNT_FIRST_PAGE = 10
        POSTS_AMOUNT_SECOND_PAGE = 3
        posts_list = [
            Post(
                text=PostPagesTests.post.text,
                author=PostPagesTests.user,
                group=PostPagesTests.group
            ) for _ in range(12)
        ]
        Post.objects.bulk_create(posts_list)
        paginated_urls = (
            PostPagesTests.index_url,
            PostPagesTests.group_list_url,
            PostPagesTests.profile_url,
        )
        pages = (
            (1, POSTS_AMOUNT_FIRST_PAGE),
            (2, POSTS_AMOUNT_SECOND_PAGE),
        )
        for name, _, args in paginated_urls:
            for page, count in pages:
                with self.subTest(name=name, page=page):
                    if page < 2:
                        response = self.client.get(
                            reverse(name, args=args)
                        )
                    if page > 1:
                        response = self.client.get(
                            reverse(name, args=args) + f'?page={page}'
                        )
                    self.assertEqual(
                        len(response.context.get('page_obj').object_list),
                        count
                    )
