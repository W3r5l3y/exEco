from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm


def forum_home(request):
    post_id = request.GET.get("post_id")
    if post_id:
        post = get_object_or_404(Post, post_id=post_id)
        return render(request, "forum/forum_home.html", {"posts": [post]})
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "forum/forum_home.html", {"posts": posts})


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("forum_home")
    else:
        form = PostForm()
    return render(request, "forum/create_post.html", {"form": form})


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
