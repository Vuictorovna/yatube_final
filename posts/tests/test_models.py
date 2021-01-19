from django.test import TestCase
from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(username="user1")
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=user,
        )

    def test_text_label(self):
        """verbose_name поля text совпадает с ожидаемым"""
        post = PostModelTest.post
        verbose = post._meta.get_field("text").verbose_name
        self.assertEquals(verbose, "Текст поста")

    def test_text_help_text(self):
        """help_text поля text совпадает с ожидаемым"""
        post = PostModelTest.post
        help_text = post._meta.get_field("text").help_text
        self.assertEquals(help_text, "Введите свой текст")

    def test_object_name_is_title_field(self):
        """__str__  post - это строчка с содержимым post.text"""
        post = PostModelTest.post
        self.assertEquals(str(post), post.text)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title="Заголовок тестовой задачи",
        )
        cls.group = Group.objects.get()

    def test_title_label(self):
        """verbose_name поля title совпадает с ожидаемым"""
        group = GroupModelTest.group
        verbose = group._meta.get_field("title").verbose_name
        self.assertEquals(verbose, "Группа")

    def test_text_help_title(self):
        """help_text поля title совпадает с ожидаемым"""
        group = GroupModelTest.group
        help_text = group._meta.get_field("title").help_text
        self.assertEquals(help_text, "Название группы")

    def test_object_name_is_title_fild(self):
        """__str__  group - это строчка с содержимым group.title"""
        group = GroupModelTest.group
        self.assertEquals(str(group), group.title)
