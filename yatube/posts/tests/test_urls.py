from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="AndreyG")
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="test-slug",
            description="testtest"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=User.objects.create_user(username="Zayan"),
            group=Group.objects.get(title="Тестовый заголовок"),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_post_url_redirect_anonymous_on_login(self):
        response = self.guest_client.get("/new/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/new/")

    def test_urls_post_url_exists_at_desired_location(self):
        response = self.authorized_client.get("/new/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_edit_post_unauthorized_user(self):
        response = self.guest_client.get("/Zayan/1/edit/")
        self.assertRedirects(response, "/auth/login/?next=/Zayan/1/edit/")

    def test_urls_edit_post_authorized_user_non_author(self):
        response = self.authorized_client.get("/Zayan/1/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_non_exist_page(self):
        response = self.authorized_client.get("/Fedor/3/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):

        templates_url_names = {
            "posts/index.html": "/",
            "posts/group.html": "/group/test-slug/",
            "posts/new_post.html": "/new/",
            "posts/profile.html": "/Zayan/",
            "posts/post.html": "/Zayan/1/",
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)


class AuthorizedUserTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='some_username')
        cls.post = Post.objects.create(
            text="Text for text",
            author=cls.user,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_urls_edit_post_authorized_user(self):
        response = self.author_client.get("/some_username/1/edit/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
