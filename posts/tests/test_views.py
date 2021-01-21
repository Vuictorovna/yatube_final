import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post, User


class TestPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )

        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="test-slug",
            description="Тестовое описание",
        )

        Group.objects.create(
            title="Другая группа",
            slug="other_group-slug",
            description="Чужая группа. Вам сюда не надо",
        )

        cls.author = User.objects.create(username="User1")

        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.author,
            group=cls.group,
            image=cls.uploaded,
        )

        cls.count = Post.objects.count()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create(username="User2")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author = TestPagesTests.author
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    # Templates tests
    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
            "index.html": reverse("index"),
            "new.html": reverse("new_post"),
            "group.html": reverse("group", kwargs={"slug": "test-slug"}),
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Cache test
    def test_cache_index_page(self):
        """ Проверка работы кэша главной страницы """
        index_1 = self.authorized_client.get(
            reverse(
                "index",
            )
        )
        Post.objects.create(
            text="Тестовый текст для проверки кэша",
            author=TestPagesTests.author,
        )
        index_2 = self.authorized_client.get(
            reverse(
                "index",
            )
        )

        self.assertHTMLEqual(str(index_1.content), str(index_2.content))

    # Context tests
    def test_index_page_shows_correct_context(self):
        """Шаблон index_page сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse("index"))
        post = response.context.get("page").object_list[0]
        expected_data = {
            "Тестовый текст": post.text,
            "posts/small.gif": post.image,
        }
        for value, expected in expected_data.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_group_page_shows_correct_context(self):
        """Шаблон group_page сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse("group", kwargs={"slug": "test-slug"})
        )
        context_group = response.context.get("group")

        self.assertEqual(context_group.title, "Тестовый заголовок")
        self.assertEqual(context_group.description, "Тестовое описание")
        self.assertEqual(context_group.slug, "test-slug")
        self.assertEqual(
            response.context.get("page")[0].image, TestPagesTests.post.image
        )

    def test_new_post_page_shows_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse("new_post"))

        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_shows_correct_context(self):
        """Шаблон post_edit_page сформирован с правильным контекстом"""
        response = self.authorized_author.get(
            reverse(
                "post_edit",
                kwargs={
                    "username": TestPagesTests.author,
                    "post_id": TestPagesTests.post.id,
                },
            )
        )
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get("post"), TestPagesTests.post)

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile_page сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse("profile", kwargs={"username": TestPagesTests.author})
        )

        self.assertEqual(response.context.get("author"), TestPagesTests.author)
        self.assertEqual(response.context.get("count"), TestPagesTests.count)

        post = response.context.get("page")[0]
        self.assertEqual(post, TestPagesTests.post)
        self.assertEqual(post.image, TestPagesTests.post.image)

    def test_post_page_shows_correct_context(self):
        """Шаблон post_page сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                "post",
                kwargs={
                    "username": TestPagesTests.author,
                    "post_id": TestPagesTests.post.id,
                },
            )
        )

        post = response.context.get("post")
        self.assertEqual(post, TestPagesTests.post)
        self.assertEqual(post.image, TestPagesTests.post.image)

        self.assertEqual(response.context.get("author"), TestPagesTests.author)
        self.assertEqual(response.context.get("count"), TestPagesTests.count)

    # New post tests
    def test_new_post_with_group_on_index_page(self):
        """Новый пост с указанной группой на главной странице"""
        response = self.authorized_client.get(reverse("index"))
        post_text = response.context.get("page").object_list[0]
        post_group = response.context.get("page")[0].group

        self.assertEqual(post_text.text, "Тестовый текст")
        self.assertEqual(post_group, TestPagesTests.group)

    def test_new_post_with_group_on_group_page(self):
        """Новый пост с указанной группой на странице группы"""
        response = self.authorized_client.get(
            reverse("group", kwargs={"slug": "test-slug"})
        )
        post_text = response.context.get("page")[0].text
        post_group = response.context.get("page")[0].group.slug

        self.assertEqual(post_text, "Тестовый текст")
        self.assertEqual(post_group, "test-slug")

    def test_no_new_post_on_other_group_page(self):
        """Новый пост с указанной группой отсутствеут на странице другой группы"""
        response = self.authorized_client.get(
            reverse("group", kwargs={"slug": "other_group-slug"})
        )

        self.assertFalse(response.context.get("posts"))

    # Following tests
    def test_follow_function_authtorized(self):
        """Доступность функции подписки авторизованному пользователю"""
        self.authorized_client.post(
            reverse(
                "profile_follow", kwargs={"username": TestPagesTests.author}
            )
        )
        following = Follow.objects.filter(
            user=self.user, author=TestPagesTests.author
        ).exists()
        self.assertTrue(following)

    def test_unfollow_function_authtorized(self):
        """Доступность функции отписки авторизованному пользователю"""
        self.authorized_client.post(
            reverse(
                "profile_unfollow", kwargs={"username": TestPagesTests.author}
            )
        )
        following = Follow.objects.filter(
            user=self.user, author=TestPagesTests.author
        ).exists()
        self.assertFalse(following)

    def test_new_author_post_on_follower_page(self):
        """Новый пост автора в ленте подписчика"""
        self.authorized_client.post(
            reverse(
                "profile_follow", kwargs={"username": TestPagesTests.author}
            )
        )
        response = self.authorized_client.get(reverse("follow_index"))
        post = response.context.get("page").object_list[0]
        expected_data = {
            "Тестовый текст": post.text,
            "User1": post.author.username,
        }
        for value, expected in expected_data.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_no_new_author_post_on_other_page(self):
        """Новый пост автора отсутствеут в ленте остальных пользователей"""
        response = self.authorized_client.get(reverse("follow_index"))
        post_list = response.context.get("page").object_list
        self.assertSequenceEqual(post_list, [])

    # Comments test
    def test_add_comment_authorized(self):
        """Авторизированный пользователь может оставить комментарий"""
        commets_count_before = TestPagesTests.post.comments.count()
        form_data = {
            "text": "Комментарий для теста",
        }

        self.authorized_client.post(
            reverse(
                "add_comment",
                kwargs={
                    "username": TestPagesTests.author,
                    "post_id": TestPagesTests.post.id,
                },
            ),
            data=form_data,
        )
        commets_count_after = TestPagesTests.post.comments.count()

        self.assertEqual(commets_count_before + 1, commets_count_after)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title="Тестовый заголовок №2",
            slug="test2-slug",
            description="Тестовое описание№2",
        )

        cls.author = User.objects.create(username="User2")

        posts = []
        for i in range(1, 14):
            posts.append(
                Post(text="text" + str(i), author=cls.author, group=cls.group)
            )
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.author)

    def test_first_page_containse_ten_records(self):
        """Количество постов на первой странице равно 10"""
        response = self.client.get(reverse("index"))
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_second_page_containse_three_records(self):
        """Количество постов на второй странице равно 3"""
        response = self.client.get(reverse("index") + "?page=2")
        self.assertEqual(len(response.context.get("page").object_list), 3)
