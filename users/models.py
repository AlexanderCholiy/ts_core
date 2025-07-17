import time
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import default_storage
from django.utils import timezone
from django.conf import settings

from .constants import (
    MAX_USER_EMAIL_LEN,
    MAX_USER_USERNAME_LEN,
    MAX_USER_PASSWORD_LEN,
    MAX_USER_ROLE_LEN,
    USERNAME_HELP_TEXT,
    PASSWORD_HELP_TEXT,
)
from .validators import (
    username_format_validators,
    password_validators,
    validate_user_username,
    validate_user_email,
    validate_pending_username,
    validate_pending_email,
)


class Roles(models.TextChoices):
    GUEST = ('guest', 'Гость')
    USER = ('user', 'Пользователь')


class User(AbstractUser):
    email = models.EmailField(
        'Email',
        unique=True,
        max_length=MAX_USER_EMAIL_LEN,
        help_text='Введите адрес электронной почты',
        validators=[validate_user_email]
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_USER_USERNAME_LEN,
        unique=True,
        validators=username_format_validators + [validate_user_username],
        help_text=USERNAME_HELP_TEXT,
    )
    password = models.CharField(
        max_length=MAX_USER_PASSWORD_LEN,
        validators=[v.validate for v in password_validators],
        help_text=PASSWORD_HELP_TEXT,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True,
        help_text='Загрузите аватар пользователя в формате JPG или PNG',
    )
    role = models.CharField(
        'Роль',
        max_length=MAX_USER_ROLE_LEN,
        choices=Roles.choices,
        default=Roles.GUEST,
        help_text='Выберите роль пользователя',
    )
    date_of_birth = models.DateField(
        'Дата рождения',
        null=True,
        blank=True,
        help_text='Формат: ГГГГ-ММ-ДД'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def temporary_username(self):
        """Генерирует уникальное временное имя с timestamp"""
        return f'{self.username}__temp_{int(time.time())}_{self.pk}'

    def delete(self, *args, **kwargs):
        if self.avatar:
            self.avatar.delete(save=False)
        super().delete(*args, **kwargs)

    def clean(self):
        super().clean()
        validate_user_username(self.username, self)
        validate_user_email(self.email, self)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        try:
            old_avatar = User.objects.get(pk=self.pk).avatar
        except User.DoesNotExist:
            old_avatar = None

        super().save(*args, **kwargs)

        if old_avatar and old_avatar != self.avatar:
            if default_storage.exists(old_avatar.name):
                default_storage.delete(old_avatar.name)


class PendingUser(models.Model):
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_USER_USERNAME_LEN,
        unique=True,
        validators=username_format_validators + [validate_pending_username],
        help_text=USERNAME_HELP_TEXT,
    )
    email = models.EmailField(
        'Почта',
        unique=True,
        max_length=MAX_USER_EMAIL_LEN,
        validators=[validate_pending_email],
        help_text='Введите адрес электронной почты',
    )
    password = models.CharField(
        max_length=MAX_USER_PASSWORD_LEN,
        validators=[v.validate for v in password_validators],
        help_text=PASSWORD_HELP_TEXT,
    )

    last_login = models.DateTimeField('Дата регистрации', default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'регистрация пользователя'
        verbose_name_plural = 'Регистрация пользоватей'

    def __str__(self) -> str:
        return self.username

    @property
    def original_username(self):
        """Извлекает оригинальное имя пользователя"""
        parts = self.username.rsplit('__temp_', 1)
        return parts[0] if len(parts) > 1 else self.username

    def clean(self):
        super().clean()
        validate_pending_username(self.username, self)
        validate_pending_email(self.email, self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_email_field_name(self) -> str:
        return 'email'

    @property
    def is_expired(self) -> bool:
        """
        Данный метод нужен, чтобы удалять пользователей давно не
        подтверждавших регистрацию.
        """
        return (
            timezone.now() - self.last_login
            > settings.REGISTRATION_ACCESS_TOKEN_LIFETIME
        )
