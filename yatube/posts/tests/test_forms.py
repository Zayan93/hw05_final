import shutil
import tempfile
from datetime import datetime
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostCreatForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Андрей")
        cls.group = Group.objects.create(title="testgroup", slug="testslug",)
        cls.other_group = Group.objects.create(
            title="OtherGroup", slug="OtherGR"
        )
        cls.post = Post.objects.create(
            text="Text of the post",
            author=cls.user,
            group=cls.group,
            pub_date=datetime(2021, 8, 1)
        )
        cls.other_post = Post.objects.create(
            text="Text without group",
            author=cls.user,
            pub_date=datetime(2021, 8, 1)
        )
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_forms_new_post_forms(self):
        posts_count = Post.objects.count()
        form_data = {"text": "test forms", "group": PostCreatForm.group.id}

        response = self.authorized_client.post(
            reverse("new_post"), data=form_data, follow=True
        )

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="test forms", group=PostCreatForm.group.id
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_forms_new_post_without_group(self):
        posts_count = Post.objects.count()
        form_data = {"text": "test forms without group"}

        response = self.authorized_client.post(
            reverse("new_post"), data=form_data, follow=True
        )

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="test forms without group",
                group__isnull=True,
                author=self.user
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.post.group, None)

    def test_forms_edit_post_forms(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Changed text of the post",
            "pub_date": datetime(2021, 7, 30)
        }

        self.authorized_client.post(
            reverse(
                "post_edit",
                kwargs={
                    "username": "Андрей",
                    "post_id": self.post.id
                },
            ),
            data=form_data,
            follow=True,
        )
        PostCreatForm.post.refresh_from_db()

        self.assertEqual(
            PostCreatForm.post.text,
            form_data["text"]
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_forms_edit_group_forms(self):
        form_data = {
            "text": "Three times changed text",
            "group": PostCreatForm.other_group.id,
            "pub_date": datetime(2021, 8, 1)
        }

        self.authorized_client.post(
            reverse(
                "post_edit",
                kwargs={
                    "username": "Андрей",
                    "post_id": self.post.id
                },
            ),
            data=form_data,
            follow=True,
        )

        self.post.refresh_from_db()

        self.assertEqual(self.post.group, self.other_group)

    def test_forms_picture(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        form_data = {
            "text": "Тестовый текст",
            "group": PostCreatForm.group.id,
            "pub_date": datetime(2021, 8, 5),
            "image": uploaded,
        }
        self.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()

        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст",
                image="posts/small.gif"
            ).exists()
        )
