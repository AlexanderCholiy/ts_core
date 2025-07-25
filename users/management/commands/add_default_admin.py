import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q
from dotenv import load_dotenv

from users.models import PendingUser

load_dotenv(override=True)


class Command(BaseCommand):
    help = 'Создает дефолтного администратора, если он не существует'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
        ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@newtowers.ru')
        ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '3uGMw69J6fflSpA76ebSuk')

        if User.objects.filter(
            username=ADMIN_USERNAME, is_superuser=True
        ).exists():
            self.stdout.write(
                f'✅ Администратор "{ADMIN_USERNAME}" уже существует.'
            )
            return

        pending_deleted, _ = PendingUser.objects.filter(
            Q(username=ADMIN_USERNAME) | Q(email=ADMIN_EMAIL)
        ).delete()
        if pending_deleted:
            self.stdout.write(
                f'🧹 Удалены PendingUser с username="{ADMIN_USERNAME}" '
                f'или email="{ADMIN_EMAIL}"'
            )

        user_deleted, _ = User.objects.filter(
            Q(username=ADMIN_USERNAME) | Q(email=ADMIN_EMAIL),
        ).exclude(is_superuser=True).delete()
        if user_deleted:
            self.stdout.write(
                '🧹 Удалены обычные пользователи с '
                f'username="{ADMIN_USERNAME}" или email="{ADMIN_EMAIL}"'
            )

        User.objects.create_user(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            role='user',
            is_staff=True,
            is_superuser=True,
        )

        self.stdout.write(
            f'✅ Администратор "{ADMIN_USERNAME}" успешно создан.'
        )
