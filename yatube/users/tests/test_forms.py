from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class SignUpFormTest(TestCase):
    def setUp(self):
        self.first_name = 'Snake'
        self.last_name = 'Plissken'
        self.username = 'callMeSnake'
        self.email = 'test_email@mailbox.com'
        self.password = 'Pass_Word_123'

    def test_sign_up_new_user(self):
        """Тест формы регистрации нового пользователя."""
        form_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password,
        }
        self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), 1)
        new_user = User.objects.first()
        user_fields = (
            (new_user.first_name, form_data['first_name']),
            (new_user.last_name, form_data['last_name']),
            (new_user.username, form_data['username']),
            (new_user.email, form_data['email']),
        )
        for value, expected in user_fields:
            with self.subTest(value=value):
                self.assertEqual(value, expected)