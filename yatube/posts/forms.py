from django.forms import ModelForm, Textarea

from .models import Post, Comment, Follow


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group", "image"]
        labels = {
            "text": "Текст записи",
            "group": "Подборка записей",
            "image": "Какую картинку вы хотите добавить",
        }
        help_texts = {
            "text": (
                "Это поле для ввода текста Вашей записи. "
                "Текст будет виден на сайте как есть."
            ),
            "group": (
                "Группа постов, она же подборка записей, в которой"
                " Вы желаете разместить своё сообщение."
            ),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {"text": "комментарий"}
        widgets = {
            "text": Textarea(attrs={"class": "form-control"}),
        }

class FollowForm(ModelForm):

    class Meta:
        exclude = set()
        model = Follow
