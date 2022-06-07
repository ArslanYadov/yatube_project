from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase
from django import forms
from posts.models import Post, Group


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostPagesTests.user,
            group=PostPagesTests.group
        )
        cls.posts = []
        for _ in range(12):
            PostPagesTests.posts.append(
                Post(
                    text=PostPagesTests.post.text,
                    author=PostPagesTests.user,
                    group=PostPagesTests.group
                )
            )
        Post.objects.bulk_create(PostPagesTests.posts)
        cls.template_urls = (
            (
                reverse('posts:index'),
                'posts/index.html'
            ),
            (
                reverse('posts:group_list', args={PostPagesTests.group.slug}),
                'posts/group_list.html'
            ),
            (
                reverse('posts:profile', args={PostPagesTests.post.author}),
                'posts/profile.html'
            ),
            (
                reverse('posts:post_detail', args={PostPagesTests.post.id}),
                'posts/post_detail.html'
            ),
            (reverse('posts:post_create'), 'posts/create_post.html'),
            (
                reverse('posts:post_edit', args={PostPagesTests.post.id}),
                'posts/create_post.html'
            ),
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

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
        for url, template in PostPagesTests.template_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.get_context_from_response(
            response.context['page_obj'][0],
            'page_obj'
        )

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args={PostPagesTests.group.slug})
        )
        context_list = (
            (response.context['page_obj'][0], 'page_obj'),
            (response.context['group'], 'group'),
        )
        for response_obj, context_name in context_list:
            self.get_context_from_response(response_obj, context_name)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', args={PostPagesTests.post.author})
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
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={PostPagesTests.post.id})
        )
        self.get_context_from_response(response.context['post'], 'post')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args={PostPagesTests.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
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
        data = {
            'text': 'Тестовый пост',
            'group': 'Тестовая группа для поста',
        }
        response = self.authorized_client.get(
            reverse('posts:post_create'),
            data=data
        )
        url_list = {
            reverse('posts:index'): 'index',
            reverse(
                'posts:group_list',
                args={PostPagesTests.group.slug}
            ): 'group_list',
            reverse(
                'posts:profile',
                args={PostPagesTests.post.author}
            ): 'profile',
        }
        for url_name in url_list:
            with self.subTest(url_name=url_name):
                self.assertTrue(response, url_name)

    def test_paginator_for_first_page(self):
        """Тестируем паджинацию первой страницы."""
        POSTS_PER_PAGE = 10
        url_dict = {
            reverse('posts:index'): 'index',
            reverse(
                'posts:group_list',
                args={PostPagesTests.group.slug}
            ): 'group',
            reverse(
                'posts:profile',
                args={PostPagesTests.posts[0].author.username}
            ): 'profile',
        }
        for url_name in url_dict:
            with self.subTest(url_name=url_name):
                response = self.client.get(url_name)
                self.assertEqual(
                    len(response.context.get('page_obj').object_list),
                    POSTS_PER_PAGE
                )

    def test_paginator_for_second_page(self):
        """Тестируем паджинацию второй страницы."""
        POSTS_PER_PAGE = 3
        url_dict = {
            reverse('posts:index') + '?page=2': 'index',
            reverse(
                'posts:group_list',
                args={PostPagesTests.group.slug}
            ) + '?page=2': 'group',
            reverse(
                'posts:profile',
                args={PostPagesTests.posts[0].author.username}
            ) + '?page=2': 'profile',
        }
        for url_name in url_dict:
            with self.subTest(url_name=url_name):
                response = self.client.get(url_name)
                self.assertEqual(
                    len(response.context.get('page_obj').object_list),
                    POSTS_PER_PAGE
                )
