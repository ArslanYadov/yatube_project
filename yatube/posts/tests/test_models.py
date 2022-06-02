from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
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

    def test_models_have_correct_object_names(self):
        """Тестируем правильную работу функций __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        expected_object_group_title = group.title
        expected_object_post_text = post.text
        str_func = {
            group: expected_object_group_title,
            post: expected_object_post_text,
        }
        for models_name, expected_value in str_func.items():
            with self.subTest(models_name=models_name):
                self.assertEqual(str(models_name), expected_value)

    def test_post_verboses_name(self):
        """Тестируем verboses_name для Post."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_post_help_text(self):
        """Тестироуем help_text для Post."""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'author': 'Введите имя автора',
            'group': 'Группа, к которой относится пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value
                )
