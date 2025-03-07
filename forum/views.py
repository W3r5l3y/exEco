from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm


def forum_home(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "forum/forum_home.html", {"posts": posts, "active_page": "home"})


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
    post = Post.objects.get(post_id=post_id)
    post.likes += 1
    post.save()
    return redirect("forum_home")


@login_required
def report_post(request, post_id):
    # Implement report functionality here
    return redirect("forum_home")
