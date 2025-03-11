from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import Post, PostLike, Comment
from .forms import PostForm
from accounts.models import CustomUser
from django.contrib import messages


def forum_home(request):
    post_id = request.GET.get("post_id")
    if post_id:
        post = get_object_or_404(Post, post_id=post_id)
        return render(request, "forum/forum_home.html", {"posts": [post]})
    posts = Post.objects.all().order_by("-created_at")
    return render(
        request, "forum/forum_home.html", {"posts": posts, "active_page": "home"}
    )


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("forum_home")

    return render(request, "forum/create_post.html", {"active_page": "create_post"})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    post_like, created = PostLike.objects.get_or_create(user=request.user, post=post)
    if not created:
        post_like.liked = not post_like.liked
        post_like.save()
    post.likes = PostLike.objects.filter(post=post, liked=True).count()
    post.save()
    return JsonResponse({"likes": post.likes, "liked": post_like.liked})


@login_required
def report_post(request, post_id):
    # Implement report functionality here
    return redirect("forum_home")


@login_required
def user_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user_posts = Post.objects.filter(user=user).order_by("-created_at")
    return render(
        request,
        "forum/user_profile.html",
        {"user": user, "posts": user_posts, "logged_in_user": request.user,"active_page": "user_profile"},
    )


@require_POST
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    text = request.POST.get("text")
    if text:
        comment = Comment.objects.create(user=request.user, post=post, text=text)
        return JsonResponse(
            {"success": True, "text": comment.text, "user_email": comment.user.email}
        )
    return JsonResponse({"success": False})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    if post.user != request.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect("user_profile", user_id=request.user.id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect("user_profile", user_id=request.user.id)
    else:
        form = PostForm(instance=post)
    return render(request, "forum/edit_post.html", {"form": form, "post": post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    if post.user != request.user:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect("user_profile", user_id=request.user.id)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect("user_profile", user_id=request.user.id)
    return render(request, "forum/delete_post.html", {"post": post})
