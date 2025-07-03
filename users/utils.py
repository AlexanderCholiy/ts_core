from datetime import timedelta

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpRequest
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import PendingUser, User


def timedelta_to_human_time(time_delta: timedelta) -> str:
    seconds = int(time_delta.total_seconds())
    if seconds <= 0:
        raise ValueError('Значение должно быть > 0')

    time_units = {
        'день': 86400,
        'час': 3600,
        'минута': 60,
        'секунда': 1,
    }

    parts = []
    remaining_seconds = seconds

    for unit_name, unit_seconds in time_units.items():
        if remaining_seconds >= unit_seconds:
            unit_value = remaining_seconds // unit_seconds
            remaining_seconds %= unit_seconds

            if unit_name == 'день':
                if unit_value % 10 == 1 and unit_value % 100 != 11:
                    unit_name_formatted = 'день'
                elif (
                    2 <= unit_value % 10 <= 4
                    and (unit_value % 100 < 10 or unit_value % 100 >= 20)
                ):
                    unit_name_formatted = 'дня'
                else:
                    unit_name_formatted = 'дней'
            elif unit_name == 'час':
                if unit_value % 10 == 1 and unit_value % 100 != 11:
                    unit_name_formatted = 'час'
                elif (
                    2 <= unit_value % 10 <= 4
                    and (unit_value % 100 < 10 or unit_value % 100 >= 20)
                ):
                    unit_name_formatted = 'часа'
                else:
                    unit_name_formatted = 'часов'
            elif unit_name == 'минута':
                if unit_value % 10 == 1 and unit_value % 100 != 11:
                    unit_name_formatted = 'минута'
                elif (
                    2 <= unit_value % 10 <= 4
                    and (unit_value % 100 < 10 or unit_value % 100 >= 20)
                ):
                    unit_name_formatted = 'минуты'
                else:
                    unit_name_formatted = 'минут'
            elif unit_name == 'секунда':
                if unit_value % 10 == 1 and unit_value % 100 != 11:
                    unit_name_formatted = 'секунда'
                elif (
                    2 <= unit_value % 10 <= 4
                    and (unit_value % 100 < 10 or unit_value % 100 >= 20)
                ):
                    unit_name_formatted = 'секунды'
                else:
                    unit_name_formatted = 'секунд'

            parts.append(f'{unit_value} {unit_name_formatted}')

    return ', '.join(parts)


def send_activation_email(
    pending_user: PendingUser, request: HttpRequest
) -> None:
    token = default_token_generator.make_token(pending_user)
    uid = urlsafe_base64_encode(force_bytes(pending_user.pk))
    activation_path = reverse(
        'users:activate', kwargs={'uidb64': uid, 'token': token})
    activation_link = request.build_absolute_uri(activation_path)
    host = request.get_host()
    valid_period: int = timedelta_to_human_time(
        settings.REGISTRATION_ACCESS_TOKEN_LIFETIME)

    subject = f'Подтверждение почты на {host}'
    message = (
        f'Здравствуйте, {pending_user.username}!\n\n'
        f'Вы указали этот адрес при регистрации на {host}.\n'
        f'Для подтверждения перейдите по ссылке: \n{activation_link}\n\n'
        f'Срок действия ссылки — {valid_period}.\n\n'
        f'Если вы не регистрировались — просто проигнорируйте это письмо.'
    )
    send_mail(
        subject, message, settings.DEFAULT_FROM_EMAIL, [pending_user.email])


def send_confirm_email(user: User, request: HttpRequest):
    pass
