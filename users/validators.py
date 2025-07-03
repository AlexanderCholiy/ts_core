from django.core.exceptions import ValidationError


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
                'Регистрация с этим email ожидает подтверждения.')


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
                'Регистрация с этим email ожидает подтверждения.')
