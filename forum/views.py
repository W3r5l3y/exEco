from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import Post, PostLike, Comment, PostReport
from .forms import PostForm
from accounts.models import CustomUser
from django.contrib import messages
from challenges.models import UserChallenge
import json


def forum_home(request):
    """
        Checks if the request is for a specific post, returning a page for that specific post if so.
        Else returns default forum home page

        Parameters:
        request: The page request.

        Returns:
        rendered forum_home html template
    """
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
    """
        Checks if create post has already been submitted. If it hasn't , return create post page.
        If it has and the post request form is valid, save post to database and redirect.

        Parameters:
        request: The page request.

        Returns:
        rendered forum_home/create_post html template
    """
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
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
    """
        Likes/Unlikes post and saves the value to the database.

        Parameters:
        request: The page request.
        post_id: The id of the post to like.

        Returns:
        json response with post like count
    """
    post = get_object_or_404(Post, post_id=post_id)
    post_like, created = PostLike.objects.get_or_create(user=request.user, post=post)
    if not created:
        post_like.liked = not post_like.liked
        post_like.save()
    else:
        post_like.liked = True
        post_like.save()
    post.likes = PostLike.objects.filter(post=post, liked=True).count()
    post.save()
    return JsonResponse(
        {"success": True, "likes": post.likes, "liked": post_like.liked}
    )


@login_required
def report_post(request, post_id):
    """
        Attempts to report post, checking if it has already been reported by the user before.

        Parameters:
        request: The page request.
        post_id: The id of the post to report.

        Returns:
        rendered forum_home html template
    """
    post = get_object_or_404(Post, post_id=post_id)
    
    # Check if the report already exists
    report, created = PostReport.objects.get_or_create(user=request.user, post=post)
    
    if created:
        messages.success(request, "Post reported successfully.")
    else:
        messages.info(request, "You have already reported this post.")
    
    return redirect("forum_home")


@login_required
def user_profile(request, user_id):
    """
        Gets a profile of a specific user.

        Parameters:
        request: The page request.
        user_id: user_id of the user's profile.

        Returns:
        rendered user_profile html template
    """
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
    """
        Submits a comment on a specific post.

        Parameters:
        request: The page request.
        post_id: id of post to add a comment to

        Returns:
        json response stated whether comment was successfully added.
    """
    post = get_object_or_404(Post, post_id=post_id)
    text = request.POST.get("text")
    if text:
        comment = Comment.objects.create(user=request.user, post=post, text=text)
        return JsonResponse(
            {"success": True, "text": comment.text, "user_email": comment.user.email}
        )
    return JsonResponse({"success": False})


@login_required
@require_POST
def edit_post(request, post_id):
    """
        Submits the edit of the user's post.

        Parameters:
        request: The page request.
        post_id: post_id of the post to submit edit for.

        Returns:
        json response stating whether edit was successful.
    """
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

    if not new_description:
        return JsonResponse({"success": False, "error": "Description cannot be empty"}, status=400)

    post.description = new_description
    post.save()

    return JsonResponse({"success": True, "message": "Post updated successfully"})



@login_required
@require_POST
def delete_post(request, post_id):
    """
        Submits the deletion of the user's post.

        Parameters:
        request: The page request.
        post_id: post_id of the post to submit edit for.

        Returns:
        json response stating whether deletion was successful.
    """
    post = get_object_or_404(Post, post_id=post_id)

    if post.user != request.user:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    post.delete()
    return JsonResponse({"success": True, "message": "Post deleted successfully"})

