from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_views_author_tech_page_exists(self):
        tests = ["about:author", "about:tech"]
        for test in tests:
            response = self.guest_client.get(reverse(test))
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_views_author_tech_pages_uses_correct_template(self):
        templates_url_names = {
            "about/author.html": "about:author",
            "about/tech.html": "about:tech",
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(reverse(adress))
                self.assertTemplateUsed(response, template)
