import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="test-slug",
            description="Тестовое описание",
        )

        cls.author = User.objects.create(username="User1")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        tasks_count = Post.objects.count()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "group": PostFormTests.group.id,
            "text": "Тестовый текст",
            "image": uploaded,
        }

        response = self.authorized_client.post(
            reverse("new_post"), data=form_data, follow=True
        )

        self.assertRedirects(response, "/")
        self.assertEqual(Post.objects.count(), tasks_count + 1)

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post"""
        post = Post.objects.create(
            text="Просто текст", author=PostFormTests.author
        )
        form_data = {
            "text": "Тестовый текст",
        }
        self.authorized_client.post(
            reverse(
                "post_edit",
                kwargs={"username": post.author, "post_id": post.id},
            ),
            data=form_data,
            follow=True,
        )
        post.refresh_from_db()
        self.assertEqual(post.text, form_data["text"])
