from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutTemplateViewTests(TestCase):

    def test_renders_template(self):
        """
        Проверяет, что представление /about/ возвращает статус 200
        и использует правильный шаблон 'pages/about.html'.
        """
        url = reverse('pages:about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'pages/about.html')
