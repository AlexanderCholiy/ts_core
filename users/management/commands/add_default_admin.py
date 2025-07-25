import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from users.models import PendingUser
from dotenv import load_dotenv


load_dotenv(override=True)


class Command(BaseCommand):
    help = 'Создает дефолтного администратора, если он не существует'
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@newtowers.ru')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '3uGMw69J6fflgFsSpA76ebSuk')

    def handle(self, *args, **kwargs):
        User = get_user_model()

        if User.objects.filter(
            username=ADMIN_USERNAME, is_superuser=True
        ).exists():
            print(f'✅ Пользователь "{ADMIN_USERNAME}" уже существует.')
            return

        # Удаляем PendingUser с таким же username или email, если есть
        deleted, _ = PendingUser.objects.filter(
            username=ADMIN_USERNAME
        ).delete()
        if deleted:
            self.stdout.write(f"🧹 Удалён PendingUser с username='{ADMIN_USERNAME}'")

        deleted, _ = PendingUser.objects.filter(
            email=ADMIN_EMAIL
        ).delete()
        if deleted:
            self.stdout.write(f"🧹 Удалён PendingUser с email='{ADMIN_EMAIL}'")

        # Создаем пользователя
        user = User.objects.create_user(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            role='user'  # или 'admin', если добавишь такую роль
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f"✅ Администратор '{ADMIN_USERNAME}' успешно создан."))
