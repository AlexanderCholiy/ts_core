from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.files.storage import default_storage
from django.utils import timezone
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
    UserAttributeSimilarityValidator
)
from django.conf import settings

from .constants import (
    MAX_USER_EMAIL_LEN,
    MAX_USER_USERNAME_LEN,
    MIN_USER_USERNAME_LEN,
    MAX_USER_PASSWORD_LEN,
    MIN_USER_PASSWORD_LEN,
    MAX_USER_ROLE_LEN,
)
from .validators import (
    validate_user_username,
    validate_user_email,
    validate_pending_username,
    validate_pending_email
)


username_format_validators = [
    RegexValidator(
        regex=r'^[a-zA-Z._-]+$',
        message=(
            'Недопустимые символы в имени пользователя. '
            'Разрешены только: английские буквы, цифры и . - _'
        )
    ),
    MinLengthValidator(
        limit_value=MIN_USER_USERNAME_LEN,
        message=(
            'Имя пользователя должно содержать минимум '
            f'{MIN_USER_USERNAME_LEN} символов.'
        )
    )
]

password_validators = [
    MinimumLengthValidator(min_length=MIN_USER_PASSWORD_LEN),
    UserAttributeSimilarityValidator(user_attributes=('username', 'email')),
    CommonPasswordValidator(),
    NumericPasswordValidator(),
]


class Roles(models.TextChoices):
    GUEST = ('guest', 'Гость')
    USER = ('user', 'Пользователь')


class User(AbstractUser):
    email = models.EmailField(
        'Почта',
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
        help_text=(
            'Имя пользователя должно содержать минимум '
            f'{MIN_USER_USERNAME_LEN} символов. '
            'Допустимые символы: буквы, цифры и .-_'
        ),
    )
    password = models.CharField(
        max_length=MAX_USER_PASSWORD_LEN,
        validators=[v.validate for v in password_validators],
        help_text=(
            f'Пароль должен содержать минимум {MIN_USER_PASSWORD_LEN} '
            'символов, не может быть полностью числовым, '
            'не должен быть похож на имя пользователя и '
            'не должен быть слишком простым.'
        ),
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True,
        help_text='Загрузите аватар пользователя',
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
        help_text=(
            'Имя пользователя должно содержать минимум '
            f'{MIN_USER_USERNAME_LEN} символов. '
            'Допустимые символы: буквы, цифры и .-_'
        ),
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
        help_text=(
            f'Пароль должен содержать минимум {MIN_USER_PASSWORD_LEN} '
            'символов, не может быть полностью числовым, '
            'не должен быть похож на имя пользователя и '
            'не должен быть слишком простым.'
        ),
    )

    last_login = models.DateTimeField('Дата регистрации', default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'регистрация пользователя'
        verbose_name_plural = 'Регистрация пользоватей'

    def __str__(self) -> str:
        return self.username

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
