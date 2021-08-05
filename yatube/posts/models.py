from typing import cast
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.base import Model
from django.db.models.deletion import CASCADE

User = get_user_model()


class Post(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    group = models.ForeignKey(
        "Group",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts"
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    verbose_name = "Пост"

    def __str__(self):
        return self.text

    class Meta:
        ordering = ("-pub_date",)


class Group(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    text = models.TextField(
        verbose_name="комментарий",
        help_text="Оставьте свой комментарий"
    )
    created = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.text

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Избранный автор"
    )
    post = models.ForeignKey(Post,
        on_delete=models.CASCADE,
        related_name="follow_text",
        null=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=["user", "author"],
                                    name="uniq_follow"),
        )
        

    def __str__(self):
        return str(self.user.username)
