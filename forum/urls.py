from django.urls import path
from .views import (
    forum_home,
    create_post,
    like_post,
    report_post,
    user_profile,
    add_comment,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("forum/", forum_home, name="forum_home"),
    path("create/", create_post, name="create_post"),
    path("like/<int:post_id>/", like_post, name="like_post"),
    path("report/<int:post_id>/", report_post, name="report_post"),
    path("profile/<int:user_id>/", user_profile, name="user_profile"),
    path("add_comment/<int:post_id>/", add_comment, name="add_comment"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
