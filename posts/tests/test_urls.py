from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        response = self.guest_client.get(reverse("about:author"))
        self.assertEqual(response.status_code, 200)

    def test_technologies(self):
        response = self.guest_client.get(reverse("about:tech"))
        self.assertEqual(response.status_code, 200)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="author")
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.author,
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create(username="User1")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author = PostURLTests.author
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    # Template tests
    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_url_names = {
            "index.html": reverse(
                "index",
            ),
            "new.html": reverse(
                "new_post",
            ),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_id_edit_uses_correct_template(self):
        """URL-адрес /username/post_id/edit/ использует соответствующий шаблон"""
        response = self.authorized_author.get(
            reverse(
                "post_edit",
                kwargs={
                    "username": PostURLTests.author,
                    "post_id": PostURLTests.post.id,
                },
            )
        )
        self.assertTemplateUsed(response, "new.html")

    # Status code tests
    def test_urls_status_code_anonymous(self):
        """Доступность страниц анонимному пользователю"""
        url_routes = {
            reverse(
                "index",
            ): 200,
            reverse(
                "new_post",
            ): 302,
            reverse(
                "profile",
                kwargs={"username": PostURLTests.author},
            ): 200,
            reverse(
                "post",
                kwargs={
                    "username": PostURLTests.author,
                    "post_id": PostURLTests.post.id,
                },
            ): 200,
            reverse(
                "post_edit",
                kwargs={
                    "username": PostURLTests.author,
                    "post_id": PostURLTests.post.id,
                },
            ): 302,
            reverse(
                "add_comment",
                kwargs={
                    "username": PostURLTests.author,
                    "post_id": PostURLTests.post.id,
                },
            ): 302,
            reverse(
                "profile_follow",
                kwargs={"username": PostURLTests.author},
            ): 302,
            reverse(
                "profile_unfollow",
                kwargs={"username": PostURLTests.author},
            ): 302,
            "/something/really/weird/": 404,
        }
        for route, status_code in url_routes.items():
            with self.subTest():
                response = self.guest_client.get(route)
                self.assertEqual(response.status_code, status_code, route)

    def test_urls_status_code_authorized(self):
        """Доступность страниц авторизованному пользователю"""
        url_routes = {
            reverse(
                "index",
            ): 200,
            reverse(
                "new_post",
            ): 200,
            reverse(
                "post_edit",
                kwargs={
                    "username": PostURLTests.author,
                    "post_id": PostURLTests.post.id,
                },
            ): 302,
        }
        for route, status_code in url_routes.items():
            with self.subTest():
                response = self.authorized_client.get(route)
                self.assertEqual(response.status_code, status_code)

    def test_post_id_edit_url_status_code_author(self):
        """Страница /username/post_id/edit/ доступна автору"""
        response = self.authorized_author.get(
            reverse(
                "post_edit",
                kwargs={
                    "username": PostURLTests.author,
                    "post_id": PostURLTests.post.id,
                },
            )
        )
        self.assertEqual(response.status_code, 200)

    # Redirect tests
    def test_urls_redirect_anonymous(self):
        """Данные страницы перенаправят анонимного
        пользователя на страницу логина"""
        url_routes = {
            reverse("new_post"): ("/auth/login/?next=" + reverse("new_post")),
            reverse(
                "post_edit",
                kwargs={
                    "username": PostURLTests.author,
                    "post_id": PostURLTests.post.id,
                },
            ): (
                "/auth/login/?next="
                + reverse(
                    "post_edit",
                    kwargs={
                        "username": PostURLTests.author,
                        "post_id": PostURLTests.post.id,
                    },
                )
            ),
            reverse(
                "add_comment",
                kwargs={
                    "username": PostURLTests.author,
                    "post_id": PostURLTests.post.id,
                },
            ): (
                "/auth/login/?next="
                + reverse(
                    "add_comment",
                    kwargs={
                        "username": PostURLTests.author,
                        "post_id": PostURLTests.post.id,
                    },
                )
            ),
        }
        for route, target in url_routes.items():
            with self.subTest():
                response = self.guest_client.get(route, follow=True)
                self.assertRedirects(response, target)

    def test_post_id_edit_url_redirect_authorized_on_post_id(self):
        """Страница /username/post_id/edit/ перенаправит авторизированного
        пользователя (не автора поста) на страницу поста"""
        response = self.authorized_client.get(
            reverse(
                "post_edit",
                kwargs={
                    "username": PostURLTests.author,
                    "post_id": PostURLTests.post.id,
                },
            ),
            follow=True,
        )
        path = reverse(
            "post",
            kwargs={
                "username": PostURLTests.author,
                "post_id": PostURLTests.post.id,
            },
        )
        self.assertRedirects(response, path)


class GroupURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Тестовый заголовок", slug="test-slug"
        )

    def setUp(self):
        self.guest_client = Client()

        user = User.objects.create(username="User1")
        self.authorized_client = Client()
        self.authorized_client.force_login(user)

    def test_group_url_exists_at_desired_location_anonymous(self):
        """Страница /group/test-slug/ доступна любому пользователю"""
        response = self.guest_client.get(
            reverse("group", kwargs={"slug": "test-slug"})
        )
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location_authorized(self):
        """Страница /group/test-slug/ доступна авторизированному пользователю"""
        response = self.authorized_client.get(
            reverse("group", kwargs={"slug": "test-slug"})
        )
        self.assertEqual(response.status_code, 200)

    def test_group_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        response = self.guest_client.get(
            reverse("group", kwargs={"slug": "test-slug"})
        )
        self.assertTemplateUsed(response, "group.html")
