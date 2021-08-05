from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text="G" * 20,
            author=User.objects.create_user(username="Test"),
            group=Group.objects.create(title="testgroup")
        )

    def test_models_object_name_is_text(self):
        post = PostModelTest.post

        expected_object_name = post.text[:15]

        self.assertEqual(expected_object_name, "G" * 15)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text="Text for group",
            author=User.objects.create_user(username="Test"),
            group=Group.objects.create(title="testgroup")
        )

    def test_models_group_title(self):
        group = self.post.group

        expected_group_title = group.title

        self.assertEqual(expected_group_title, "testgroup")
