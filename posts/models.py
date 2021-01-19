from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Группа",
        help_text="Название группы",
    )
    slug = models.SlugField(max_length=40, unique=True)
    description = models.TextField(max_length=5000)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Введите свой текст",
    )
    pub_date = models.DateTimeField(
        "date published", auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="author_posts"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="group_posts",
        blank=True,
        null=True,
    )
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField(
        verbose_name="Комментарий",
        help_text="Введите свой комментарий",
    )
    created = models.DateTimeField("date published", auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
