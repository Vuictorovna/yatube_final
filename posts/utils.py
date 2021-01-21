from .models import Follow


def is_following(user, author):
    if not user.is_authenticated:
        return False
    return Follow.objects.filter(user=user, author=author).exists()
