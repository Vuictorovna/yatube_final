from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related("group")

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "index.html",
        {
            "page": page,
            "paginator": paginator,
        },
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "group.html",
        context={
            "group": group,
            "page": page,
            "paginator": paginator,
        },
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")

    return render(request, "new.html", {"form": form})


def is_following(user, author):
    if not user.is_authenticated:
        return False
    return Follow.objects.filter(user=user, author=author).exists()


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.author_posts.all()
    count = posts.count()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    following = is_following(request.user, author)

    following_number = author.following.count()
    followers_number = author.follower.count()

    return render(
        request,
        "profile.html",
        {
            "author": author,
            "count": count,
            "page": page,
            "paginator": paginator,
            "following": following,
            "followers_number": followers_number,
            "following_number": following_number,
        },
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    count = author.author_posts.count()
    comments = post.comments.all()

    following_number = author.following.count()
    followers_number = author.follower.count()

    form = CommentForm(request.POST or None)

    return render(
        request,
        "post.html",
        {
            "post": post,
            "author": author,
            "count": count,
            "post_id": post_id,
            "comments": comments,
            "form": form,
            "followers_number": followers_number,
            "following_number": following_number,
        },
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author

    if request.user != author:
        return redirect("post", username=author.username, post_id=post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect("post", username=author.username, post_id=post_id)

    return render(
        request,
        "new.html",
        {
            "form": form,
            "post": post,
            "is_edit": True,
        },
    )


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    count = author.author_posts.count()

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("post", username=author.username, post_id=post_id)

    return render(
        request,
        "post.html",
        {
            "form": form,
            "post": post,
            "author": author,
            "count": count,
        },
    )


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "follow.html",
        {
            "page": page,
            "paginator": paginator,
        },
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (
        author != request.user
        and not Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    ):
        Follow.objects.create(user=request.user, author=author)

        return redirect("profile", username=username)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if (
        author != request.user
        and Follow.objects.filter(user=request.user, author=author).exists()
    ):
        Follow.objects.get(user=request.user, author=author).delete()
        return redirect("profile", username=username)
    return redirect("profile", username=username)
