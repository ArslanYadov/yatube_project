import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django import forms
from posts.models import Post, Group, Follow
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.conf import settings
from PIL import Image
from io import BytesIO
from http import HTTPStatus


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='TestSlug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
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
        cls.all_posts_app_urls = (
            PostPagesTests.index_url,
            PostPagesTests.group_list_url,
            PostPagesTests.profile_url,
            PostPagesTests.post_detail_url,
            PostPagesTests.post_create_url,
            PostPagesTests.post_edit_url
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        cache.clear()

    def get_context_from_response(self, response_obj, context_name):
        """Функция для проверки контекста в тестах."""
        if context_name == 'page_obj' or context_name == 'post':
            object_list = (
                (response_obj.text, PostPagesTests.post.text),
                (response_obj.author, PostPagesTests.post.author),
                (response_obj.group.title, PostPagesTests.group.title),
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
        self.assertFalse(
            response.context['following']
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        name, _, args = PostPagesTests.post_detail_url
        response = self.authorized_client.get(
            reverse(name, args=args)
        )
        self.get_context_from_response(response.context['post'], 'post')
        form_fields = (
            ('text', forms.fields.CharField),
        )
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

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

    def test_index_cache(self):
        """Тестируем кэш для главное страницы."""
        new_post = Post.objects.create(
            text='Новый пост',
            author=PostPagesTests.user
        )
        name, _, _ = PostPagesTests.index_url
        response = self.authorized_client.get(
            reverse(name)
        )
        response_old = response
        new_post.delete()
        response = self.authorized_client.get(
            reverse(name)
        )
        self.assertEqual(response.content, response_old.content)
        cache.clear()
        response = self.authorized_client.get(
            reverse(name)
        )
        self.assertNotEqual(response.content, response_old.content)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostWithImageViewTest(TestCase):
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

    def test_post_with_image_use_correct_context(self):
        """
        Проверяем, что при выводе поста с картинкой
        изображение передаётся в словаре context:
        - на главную страницу,
        - на страницу профайла,
        - на страницу группы,
        - на отдельную страницу поста.
        """
        post = Post.objects.create(
            text='Тестовый пост c картинкой',
            author=PostWithImageViewTest.user,
            group=PostWithImageViewTest.group,
            image=self.get_image_file()
        )
        index_url = ('posts:index', ())
        group_list_url = (
            'posts:group_list',
            (post.group.slug,)
        )
        profile_url = (
            'posts:profile',
            (post.author,)
        )
        post_detail_url = (
            'posts:post_detail',
            (post.id,)
        )
        post_urls = (
            index_url,
            group_list_url,
            profile_url,
            post_detail_url
        )
        for name, args in post_urls:
            with self.subTest(name=name):
                response = self.client.get(
                    reverse(name, args=args)
                )
                if not post_detail_url:
                    self.assertEqual(
                        post.image,
                        response.context['page_obj'][0].image
                    )
                self.assertEqual(
                    post.image,
                    response.context['post'].image
                )


class PostWithCommentViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='TestSlug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост с комментарием',
            author=PostWithCommentViewTest.user,
            group=PostWithCommentViewTest.group,
        )
        cls.post_detail_url = (
            'posts:post_detail',
            (PostWithCommentViewTest.post.id,)
        )
        cls.add_comment_url = (
            'posts:add_comment',
            (PostWithCommentViewTest.post.id,)
        )

    def setUp(self):
        self.authorized_client_for_comment = Client()
        self.authorized_client_for_comment.force_login(
            User.objects.create(username='CommentUser')
        )

    def test_non_authorized_user_can_not_comment_post(self):
        """
        Не авторизированный пользователь не может комментить посты.
        """
        name, args = PostWithCommentViewTest.add_comment_url
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
        name, args = PostWithCommentViewTest.add_comment_url
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
        name, args = PostWithCommentViewTest.post_detail_url
        response = self.client.get(
            reverse(name, args=args)
        )
        self.assertContains(response, comment.text)


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blog_author = User.objects.create_user(username='Bloger')
        cls.user = User.objects.create_user(username='Follower')

    def setUp(self):
        self.authorized_blog_author = Client()
        self.authorized_follower_user = Client()
        self.authorized_blog_author.force_login(FollowViewTest.blog_author)
        self.authorized_follower_user.force_login(FollowViewTest.user)

    def test_authorized_user_can_follow(self):
        """Аторизированный пользователь может зафолловиться на блогера."""
        response = self.authorized_follower_user.get(
            reverse(
                'posts:profile_follow',
                args=(FollowViewTest.blog_author,)
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        follow = Follow.objects.first()
        users_list = (
            (follow.user, FollowViewTest.user),
            (follow.author, FollowViewTest.blog_author),
        )
        for name, expected in users_list:
            with self.subTest(name=name):
                self.assertEqual(name, expected)
        self.assertEqual(Follow.objects.count(), 1)

    def test_authorized_user_can_infollow(self):
        """
        Аторизированный пользователь может отписаться от блогера.
        После отписки от блогера его посты не появляются в ленте.
        """
        Follow.objects.create(
            user=FollowViewTest.user,
            author=FollowViewTest.blog_author
        )
        response = self.authorized_follower_user.get(
            reverse(
                'posts:profile_unfollow',
                args=(FollowViewTest.blog_author,)
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), 0)
        self.authorized_blog_author.post(
            reverse('posts:post_create'),
            data={
                'text': 'Пост для подписчиков'
            },
            follow=True
        )
        post = Post.objects.first()
        response = self.authorized_follower_user.get(
            reverse('posts:follow_index')
        )
        self.assertNotContains(response, post.text)

    def test_new_post_for_follower(self):
        """
        Фолловер видит в ленте новую запись от блогера,
        на которого подписан.
        """
        Follow.objects.create(
            user=FollowViewTest.user,
            author=FollowViewTest.blog_author
        )
        self.authorized_blog_author.post(
            reverse('posts:post_create'),
            data={
                'text': 'Пост для подписчиков'
            },
            follow=True
        )
        post = Post.objects.first()
        response = self.authorized_follower_user.get(
            reverse('posts:follow_index')
        )
        self.assertContains(response, post.text)
        response = self.authorized_blog_author.get(
            reverse('posts:follow_index')
        )
        self.assertNotContains(response, post.text)
