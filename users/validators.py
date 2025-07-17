from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
    UserAttributeSimilarityValidator
)

from .constants import (
    MIN_USER_USERNAME_LEN,
    MIN_USER_PASSWORD_LEN,
)


username_format_validators = [
    RegexValidator(
        regex=r'^[a-zA-Z0-9._-]+$',
        message=(
            'Недопустимые символы в имени пользователя. '
            'Разрешены только: английские буквы, цифры и . - _'
        )
    ),
    MinLengthValidator(
        limit_value=MIN_USER_USERNAME_LEN,
        message=(
            'Имя пользователя должно содержать минимум '
            f'{MIN_USER_USERNAME_LEN} символа.'
        )
    )
]

password_validators = [
    MinimumLengthValidator(min_length=MIN_USER_PASSWORD_LEN),
    UserAttributeSimilarityValidator(user_attributes=('username', 'email')),
    CommonPasswordValidator(),
    NumericPasswordValidator(),
]


def validate_user_username(username: str, instance=None):
    from .models import User, PendingUser

    if instance is not None:
        qs = User.objects.filter(username__iexact=username)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise ValidationError('Имя пользователя уже занято.')

    pending = PendingUser.objects.filter(username=username).first()
    if pending:
        if pending.is_expired:
            pending.delete()
        else:
            raise ValidationError('Имя пользователя ожидает подтверждения.')


def validate_user_email(email: str, instance=None):
    from .models import User, PendingUser

    if instance is not None:
        qs = User.objects.filter(email=email)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise ValidationError('Email уже зарегистрирован.')

    pending = PendingUser.objects.filter(email=email).first()
    if pending:
        if pending.is_expired:
            pending.delete()
        else:
            raise ValidationError(
                'Данный email ожидает подтверждения.')


def validate_pending_username(username: str, instance=None):
    from .models import User, PendingUser

    if User.objects.filter(username=username).exists():
        raise ValidationError('Имя пользователя уже занято.')

    qs = PendingUser.objects.filter(username=username)
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    pending = qs.first()
    if pending:
        if pending.is_expired:
            pending.delete()
        else:
            raise ValidationError('Имя пользователя ожидает подтверждения.')


def validate_pending_email(email: str, instance=None):
    from .models import User, PendingUser

    if User.objects.filter(email=email).exists():
        raise ValidationError('Email уже зарегистрирован.')

    qs = PendingUser.objects.filter(email=email)
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    pending = qs.first()
    if pending:
        if pending.is_expired:
            pending.delete()
        else:
            raise ValidationError(
                'Дынный email ожидает подтверждения.')
