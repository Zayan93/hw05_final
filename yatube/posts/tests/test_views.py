from datetime import datetime
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()


class PostPagesTest(TestCase):
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
            author=cls.user,
            group=cls.group,
            pub_date=datetime(2021, 7, 11)
        )
        cls.other_post = Post.objects.create(
            text="текст другого автора",
            author=User.objects.create_user(username="Maxim"),
            group=cls.group,
            pub_date=datetime(2021, 7, 12)
        )
        cls.post_cache = Post.objects.create(
            text="Test cache text",
            author=User.objects.create_user(username="Oleg"),
            group=cls.group,
            pub_date=datetime(2021, 7, 13)
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_views_pages_show_correct_template(self):
        templates_pages_names = {
            "posts/index.html": reverse("index"),
            "posts/group.html": reverse(
                "group_posts", kwargs={"slug": "test-slug"}
            ),
            "posts/new_post.html": reverse("new_post"),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_views_post_shows_correct_context(self):
        response = self.authorized_client.get(reverse("index"))

        post = response.context["page"][0]

        self.assertEqual(post.text, "Test cache text")

    def test_views_post_shows_correct_author(self):
        response = self.authorized_client.get(
            reverse("profile", kwargs={"username": "Maxim"})
        )

        other_post = response.context["page"][0]
        follow = response.context["following"]

        self.assertEqual(other_post.author.username, "Maxim")
        self.assertEqual(other_post.text, "текст другого автора")
        self.assertEqual(follow, False)

    def test_views_follow_author(self):
        self.authorized_client.get(
            reverse(
                'profile_follow',
                kwargs={'username': "Oleg"}))

        follow_count = Follow.objects.filter(author__username="Oleg").count()

        self.assertEqual(follow_count, 1)

    def test_views_unfollow_author(self):
        Follow.objects.create(
            author=User.objects.get(username="AndreyG"),
            user=User.objects.get(username="Oleg")
        )
        self.authorized_client.post(
            reverse("profile_unfollow", kwargs={"username": "Oleg"})
        )
        follow_count = Follow.objects.filter(author__username="Oleg").count()

        self.assertEqual(follow_count, 0)

    def test_views_group_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse("group_posts", kwargs={"slug": "test-slug"})
        )

        group = response.context["group"]

        self.assertEqual(group.title, "Тестовый заголовок")
        self.assertEqual(group.slug, "test-slug")
        self.assertEqual(group.description, "testtest")

    def test_unauthorized_client_edit_post(self):
        response = self.guest_client.get("/AnderyG/1/edit/")
        self.assertRedirects(response, "/auth/login/?next=/AnderyG/1/edit/")

    def test_views_non_author_edit(self):
        response = self.authorized_client.get("/Maxim/1/edit/").status_code
        self.assertEqual(response, HTTPStatus.NOT_FOUND)

    def test_views_correct_author(self):
        form_data = {"text": "112gdfsgdfgdfg", "author": "Maxim"}
        self.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True)

        self.assertTrue(Post.objects.filter(
            text="112gdfsgdfgdfg",
            author=self.user).exists())

    def test_cache(self):
        post = Post.objects.create(text="Кэш тест текст", author=self.user)
        response = self.authorized_client.get(reverse("index"))
        content = response.content
        post.delete()
        response = self.authorized_client.get(reverse("index"))
        self.assertEqual(content, response.content)
        cache.clear()
        response = self.authorized_client.get(reverse("index"))
        self.assertNotEqual(content, response.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="ZayanG")
        objs = (Post(
            text="Тестовый текст",
            author=cls.user) for i in range(13))
        Post.objects.bulk_create(objs)

    def test_views_first_page(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_views_second_page_contains_three_records(self):
        response = self.client.get(reverse("index") + "?page=2")
        self.assertEqual(len(response.context.get("page").object_list), 3)

    def test_views_page_contains_correct_context(self):
        response = self.client.get(reverse("index"))
        page_context = response.context.get("page").object_list[0].text
        self.assertEqual(page_context, "Тестовый текст")
