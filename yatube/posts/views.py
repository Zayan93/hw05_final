from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@login_required
@require_http_methods(["GET", "POST"])
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author_id = request.user.id
        new_post.save()
        return redirect("index")
    return render(request, "posts/new_post.html", {
        "form": form, "is_edit": False
    })


@login_required
@require_http_methods(["GET", "POST"])
def edit_post(request, username, post_id):
    post = get_object_or_404(
        Post,
        author__username=username,
        pk=post_id
    )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if request.user != post.author:
        return redirect("post", username, post_id)

    if form.is_valid():
        form.save()
        return redirect("post", post_id=post_id, username=username)

    return render(request, "posts/new_post.html", {
        "form": form, "is_edit": True, "post": post,
    })


@require_GET
def index(request):
    page_number = request.GET.get('page')
    key = f"index-cache-page-{page_number}"
    page = cache.get(key)
    if page is None:
        posts = Post.objects.all()
        paginator = Paginator(posts, 10)
        page = paginator.get_page(page_number)
        cache.set(key, page, timeout=20)

    context = {'page': page}
    return render(request, 'posts/index.html', context)


@require_GET
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/group.html", {
        "page": page, "group": group, "posts": posts,
    })


@require_GET
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.post_set.all()
    posts_count = posts.count()
    followers_count = Follow.objects.filter(author=user).count()
    follow_count = Follow.objects.filter(user=user).count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=user).exists()
    context = {
        "author": user,
        "posts_count": posts_count,
        "page": page,
        "following": following,
        "followers_count": followers_count,
        "follow_count": follow_count,
    }

    return render(
        request,
        "posts/profile.html",
        context
    )


@require_http_methods(["GET", "POST"])
def post_view(request, username, post_id):
    post = get_object_or_404(
        Post,
        author__username=username,
        pk=post_id
    )
    form = CommentForm(request.POST or None)
    object_for_post = get_object_or_404(User, username=username)
    posts_count = object_for_post.post_set.all().count()
    comments = post.comments.all()
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(
            author=post.author, user=request.user
        ).exists():
            following = True
    followers_count = Follow.objects.filter(author=post.author).count()
    follow_count = Follow.objects.filter(user=post.author).count()
    context = {
        "post": post,
        "form": form,
        "author": post.author,
        "comments": comments,
        "object_for_post": object_for_post,
        "posts_count": posts_count,
        "following": following,
        "followers_count": followers_count,
        "follow_count": follow_count,
    }

    return render(
        request,
        "posts/post.html",
        context
    )


@require_http_methods(["GET", "POST"])
@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect("post", username, post_id)

    return render(request, "posts/post.html", {'form': form, "post": post})


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/follow.html", {
        "page": page,
        "post": posts,
    })


@login_required
def profile_follow(request, username):
    follow_author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    if not Follow.objects.filter(
        author=follow_author, user=request.user
    ).exists() and user != follow_author:
        Follow.objects.get_or_create(
            user_id=request.user.id, author_id=follow_author.id
        )
    return redirect("profile", username)


@login_required
def profile_unfollow(request, username):
    follow_author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user_id=request.user.id,
        author_id=follow_author.id).delete()
    return redirect("profile", username)
