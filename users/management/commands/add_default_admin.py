import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q
from dotenv import load_dotenv

from users.models import PendingUser

load_dotenv(override=True)


class Command(BaseCommand):
    help = 'Создает дефолтного администратора, если он не существует'

    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

    def handle(self, *args, **kwargs):
        User = get_user_model()

        missing_vars = []
        if not self.ADMIN_USERNAME:
            missing_vars.append('ADMIN_USERNAME')
        if not self.ADMIN_EMAIL:
            missing_vars.append('ADMIN_EMAIL')
        if not self.ADMIN_PASSWORD:
            missing_vars.append('ADMIN_PASSWORD')

        if missing_vars:
            self.stderr.write(
                f'❌ Не заданы переменные окружения: {", ".join(missing_vars)}'
            )

        if User.objects.filter(
            username=self.ADMIN_USERNAME, is_superuser=True
        ).exists():
            self.stdout.write(
                f'✅ Администратор "{self.ADMIN_USERNAME}" уже существует.'
            )
            return

        pending_deleted, _ = PendingUser.objects.filter(
            Q(username=self.ADMIN_USERNAME) | Q(email=self.ADMIN_EMAIL)
        ).delete()
        if pending_deleted:
            self.stdout.write(
                f'🧹 Удалены PendingUser с username="{self.ADMIN_USERNAME}" '
                f'или email="{self.ADMIN_EMAIL}"'
            )

        user_deleted, _ = User.objects.filter(
            Q(username=self.ADMIN_USERNAME) | Q(email=self.ADMIN_EMAIL),
        ).exclude(is_superuser=True).delete()
        if user_deleted:
            self.stdout.write(
                '🧹 Удалены обычные пользователи с '
                f'username="{self.ADMIN_USERNAME}" или '
                f'email="{self.ADMIN_EMAIL}"'
            )

        User.objects.create_user(
            username=self.ADMIN_USERNAME,
            email=self.ADMIN_EMAIL,
            password=self.ADMIN_PASSWORD,
            role='user',
            is_staff=True,
            is_superuser=True,
        )

        self.stdout.write(
            f'✅ Администратор "{self.ADMIN_USERNAME}" успешно создан.'
        )
