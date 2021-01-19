from django.test import Client, TestCase
from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        response = self.guest_client.get("/about/author/")
        self.assertEqual(response.status_code, 200)

    def test_technologies(self):
        response = self.guest_client.get("/about/tech/")
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
            "index.html": "/",
            "new.html": "/new/",
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_id_edit_uses_correct_template(self):
        """URL-адрес /username/post_id/edit/ использует соответствующий шаблон"""
        post = PostURLTests.post

        response = self.authorized_author.get(
            f"/{self.author.username}/{post.id}/edit/"
        )
        self.assertTemplateUsed(response, "new.html")

    # Status code tests
    def test_urls_status_code_anonymous(self):
        """Доступность страниц анонимному пользователю"""
        post = PostURLTests.post
        author = PostURLTests.author

        url_routes = {
            "/": 200,
            "/new/": 302,
            f"/{self.user.username}/": 200,
            f"/{author.username}/{post.id}/": 200,
            f"/{author.username}/{post.id}/edit/": 302,
            f"/{author.username}/{post.id}/comment/": 302,
            f"/{author.username}/follow/": 302,
            f"/{author.username}/unfollow/": 302,
            "/something/really/weird/": 404,
        }
        for route, status_code in url_routes.items():
            with self.subTest():
                response = self.guest_client.get(route)
                self.assertEqual(response.status_code, status_code, route)

    def test_urls_status_code_authorized(self):
        """Доступность страниц авторизованному пользователю"""
        post = PostURLTests.post
        author = PostURLTests.author

        url_routes = {
            "/": 200,
            "/new/": 200,
            f"/{author.username}/{post.id}/edit/": 302,
        }
        for route, status_code in url_routes.items():
            with self.subTest():
                response = self.authorized_client.get(route)
                self.assertEqual(response.status_code, status_code)

    def test_post_id_edit_url_status_code_author(self):
        """Страница /username/post_id/edit/ доступна автору"""
        post = PostURLTests.post

        response = self.authorized_author.get(
            f"/{self.author.username}/{post.id}/edit/"
        )
        self.assertEqual(response.status_code, 200)

    # Redirect tests
    def test_urls_redirect_anonymous(self):
        """Данные страницы перенаправят анонимного
        пользователя на страницу логина"""
        post = PostURLTests.post
        author = PostURLTests.author

        url_routes = {
            "/new/": "/auth/login/?next=/new/",
            f"/{self.user.username}/{post.id}/edit/": f"/auth/login/?next=/{self.user.username}/{post.id}/edit/",
            f"/{author.username}/{post.id}/comment/": f"/auth/login/?next=/{author.username}/{post.id}/comment/",
        }
        for route, target in url_routes.items():
            with self.subTest():
                response = self.guest_client.get(route, follow=True)
                self.assertRedirects(response, target)

    def test_post_id_edit_url_redirect_authorized_on_post_id(self):
        """Страница /username/post_id/edit/ перенаправит авторизированного
        пользователя (не автора поста) на страницу поста"""
        post = PostURLTests.post
        author = PostURLTests.author

        response = self.authorized_client.get(
            f"/{author.username}/{post.id}/edit/", follow=True
        )
        self.assertRedirects(
            response,
            f"/{author.username}/{post.id}/",
        )


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
        response = self.guest_client.get("/group/test-slug/")
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location_authorized(self):
        """Страница /group/test-slug/ доступна авторизированному пользователю"""
        response = self.authorized_client.get("/group/test-slug/")
        self.assertEqual(response.status_code, 200)

    def test_group_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        response = self.guest_client.get("/group/test-slug/")
        self.assertTemplateUsed(response, "group.html")
