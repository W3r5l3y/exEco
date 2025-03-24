from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import Post, PostLike, Comment, PostReport
from .forms import PostForm
from accounts.models import CustomUser, UserPoints, UserCoins
from django.contrib import messages
from challenges.models import UserChallenge
import json

def forum_home(request):
    # Display a single post if post_id is provided in the query params, else display all posts
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
    # Create a new post
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        # Check if the form is valid, if so save the post
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            # Update Challenge Progress
            user_challenges = UserChallenge.objects.filter(
                user=request.user, challenge__game_category="forum", completed=False
            )
            for user_challenge in user_challenges:
                user_challenge.progress += 1
                if user_challenge.progress >= user_challenge.challenge.goal:
                    user_challenge.completed = True
                user_challenge.save()

            return redirect("forum_home")

    return render(request, "forum/create_post.html", {"active_page": "create_post"})


@login_required
@require_POST
def like_post(request, post_id):
    # Like or unlike a post
    post = get_object_or_404(Post, post_id=post_id)
    post_like, created = PostLike.objects.get_or_create(user=request.user, post=post)

    if not created:  # If the like already exists, toggle the liked status
        post_like.liked = not post_like.liked
        post_like.save()
    else:  # If the like is being created for the first time, set liked to True
        post_like.liked = True
        post_like.save()

    post.likes = PostLike.objects.filter(post=post, liked=True).count()
    post.save()

    # Add coins to the post's user
    user_coins, _ = UserCoins.objects.get_or_create(user=post.user)
    user_coins.update_forum_coins()
    print(user_coins.coins)

    return JsonResponse(
        {"success": True, "likes": post.likes, "liked": post_like.liked}
    )


@login_required
def report_post(request, post_id):
    # Report a post
    post = get_object_or_404(Post, post_id=post_id)

    # Check if the report already exists, if not create a new report
    report, created = PostReport.objects.get_or_create(user=request.user, post=post)

    if created:
        messages.success(request, "Post reported successfully.")
    else:
        messages.info(request, "You have already reported this post.")

    return redirect("forum_home")


@login_required
def user_profile(request, user_id):
    # Display the profile of a user
    user = get_object_or_404(CustomUser, id=user_id)
    user_posts = Post.objects.filter(user=user).order_by("-created_at")
    return render(
        request,
        "forum/user_profile.html",
        {
            "user": user,
            "posts": user_posts,
            "logged_in_user": request.user,
            "active_page": "user_profile",
        },
    )


@require_POST
@login_required
def add_comment(request, post_id):
    # Add a comment to a post
    post = get_object_or_404(Post, post_id=post_id)
    text = request.POST.get("text")
    if text:
        comment = Comment.objects.create(user=request.user, post=post, text=text)
        return JsonResponse(
            {"success": True, "text": comment.text, "user_email": comment.user.email}
        )

    # Add coins to the post's user
    user_coins, _ = UserCoins.objects.get_or_create(user=post.user)
    user_coins.update_forum_coins()
    print(user_coins.coins)

    return JsonResponse({"success": False})


@login_required
@require_POST
def edit_post(request, post_id):
    # Edit a post
    post = get_object_or_404(Post, post_id=post_id)
    #Check if user is somehow editing somebody else's post
    if post.user != request.user:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    else:
        data = request.POST
    new_description = data.get("description", "").strip()

    if not new_description:  # Check if the description is empty
        return JsonResponse(
            {"success": False, "error": "Description cannot be empty"}, status=400
        )

    post.description = new_description
    post.save()

    # Add coins to the post's user
    user_coins, _ = UserCoins.objects.get_or_create(user=post.user)
    user_coins.update_forum_coins()
    print(user_coins.coins)

    return JsonResponse({"success": True, "message": "Post updated successfully"})


@login_required
@require_POST
def delete_post(request, post_id):
    # Delete a post
    post = get_object_or_404(Post, post_id=post_id)

    if post.user != request.user:  # Check if the user is the owner of the post
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    post.delete()

    # Add coins to the post's user
    user_coins, _ = UserCoins.objects.get_or_create(user=post.user)
    user_coins.update_forum_coins()
    print(user_coins.coins)

    return JsonResponse({"success": True, "message": "Post deleted successfully"})
