from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Post, Group
from yatube.settings import TRIM_STRING_LENGTH


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=PostModelTest.user,
            text='Тестовый пост',
            group=PostModelTest.group
        )

    def test_models_have_correct_object_names(self):
        """
        Тестируем правильную вывод функций __str__.
        """
        str_func = (
            (PostModelTest.group, self.group.title),
            (PostModelTest.post, self.post.text),
        )
        for models_name, expected_value in str_func:
            with self.subTest(models_name=models_name):
                self.assertEqual(str(models_name), expected_value)

    def test_post_text_trim(self):
        """Тестируем обрезку поля текст."""
        long_post = Post.objects.create(
            text='Тестовый пост' * 10,
            author=PostModelTest.user,
            group=PostModelTest.group
        )

        self.assertEqual(len(long_post.text), TRIM_STRING_LENGTH)

    def test_post_verboses_name(self):
        """Тестируем verboses_name для Post."""
        field_verboses = (
            ('text', 'Текст'),
            ('author', 'Автор'),
            ('group', 'Группа'),
        )
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_post_help_text(self):
        """Тестироуем help_text для Post."""
        field_help_text = (
            ('text', 'Введите текст поста'),
            ('author', 'Введите имя автора'),
            ('group', 'Группа, к которой относится пост'),
        )
        for field, expected_value in field_help_text:
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text,
                    expected_value
                )
