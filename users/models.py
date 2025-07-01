from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.core.files.storage import default_storage

from .constants import (
    MAX_USER_EMAIL_LEN,
    MAX_USER_FIRST_NAME_LEN,
    MAX_USER_LAST_NAME_LEN,
    MAX_USER_USERNAME_LEN,
)


username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message=(
        'Недопустимые символы в username. Разрешены только: буквы, цифры '
        'и . @ + - _'
    )
)


class User(AbstractUser):
    email = models.EmailField(
        'Почта',
        unique=True,
        max_length=MAX_USER_EMAIL_LEN,
        help_text='Введите адрес электронной почты',
    )
    username = models.CharField(
        'Никнейм',
        max_length=MAX_USER_USERNAME_LEN,
        unique=True,
        validators=[username_validator],
        help_text='Введите имя пользователя (никнейм)',
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_USER_FIRST_NAME_LEN,
        help_text='Введите имя пользователя',
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_USER_LAST_NAME_LEN,
        help_text='Введите фамилию пользователя',
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True,
        help_text='Загрузите аватар пользователя',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def delete(self, *args, **kwargs):
        if self.avatar:
            self.avatar.delete(save=False)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs) -> None:
        try:
            old_avatar = User.objects.get(pk=self.pk).avatar
        except User.DoesNotExist:
            old_avatar = None

        super().save(*args, **kwargs)

        if old_avatar and old_avatar != self.avatar:
            if default_storage.exists(old_avatar.name):
                default_storage.delete(old_avatar.name)
