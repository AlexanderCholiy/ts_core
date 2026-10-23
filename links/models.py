from django.db import models

from links.constants import MAX_LINK_TITLE, MAX_LINK_URL_LEN


class ExternalResource(models.Model):
    title = models.CharField(
        max_length=MAX_LINK_TITLE,
        verbose_name='Название ресурса',
        db_index=True,
    )
    url = models.URLField(
        max_length=MAX_LINK_URL_LEN,
        verbose_name='Ссылка на внешний ресурс',
        db_index=True,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно',
        help_text='Отображать ли ссылку в боковом меню',
    )
    created_at = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Внешний ресурс'
        verbose_name_plural = 'Внешние ресурсы'
        ordering = ['title', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'url'],
                name='unique_title_url_resource'
            )
        ]

    def __str__(self):
        return self.title
