from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "group",
            "text",
            "image",
        )
        labels = {
            "group": "Выберите группу ",
            "text": "Введите текст",
        }
        help_texts = {
            "group": "Здесь Вы можете выбрать группу",
            "text": "Место для Вашего рассказа",
        }


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Comment
        fields = ("text",)
        labels = {"text": "Ваш комментарий"}
        help_texts = {
            "text": "Пожалуйста, поделитесь своим мнением",
        }
