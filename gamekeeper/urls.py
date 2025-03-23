from django.urls import path
from .views import (
    gamekeeper_view,
    add_location_to_qr,
    unlink_strava,
    get_strava_links,
    add_item_to_bingame,
    add_points,
    get_qr_codes,
    enable_qr,
    disable_qr,
    get_user_ids,
    add_item_to_shop,
    add_challenge,
    load_contact_requests,
    respond_contact,
    get_reported_posts,
    get_reported_post_details,
    delete_reported_post,
    delete_report,
)

urlpatterns = [
    path("gamekeeper/", gamekeeper_view, name="gamekeeper"),
    path(
        "add-location-to-qr/<str:location_code>/<str:location_name>/<str:location_fact>/<int:cooldown_length>/<int:location_value>/",
        add_location_to_qr,
        name="add_location_to_qr",
    ),
    path("unlink-strava/<int:user_id>/", unlink_strava, name="unlink_strava"),
    path("get-strava-links/", get_strava_links, name="get_strava_links"),
    path("add-item-to-bingame/", add_item_to_bingame, name="add_item_to_bingame"),
    path(
        "add-points/<str:type>/<int:user_id>/<int:amount>/",
        add_points,
        name="add_points",
    ),
    path("get-qr-codes/", get_qr_codes, name="get_qr_codes"),
    path("enable-qr/<str:qr_id>/", enable_qr, name="enable_qr"),
    path("disable-qr/<str:qr_id>/", disable_qr, name="disable_qr"),
    path("get-user-ids/", get_user_ids, name="get_user_ids"),
    path("add-item-to-shop/", add_item_to_shop, name="add_item_to_shop"),
    path("add-challenge/", add_challenge, name="add_challenge"),
    path("contact-requests/", load_contact_requests, name="load_contact_requests"),
    path("respond-contact/", respond_contact, name="respond_contact"),
    path("get-reported-posts/", get_reported_posts, name="get_reported_posts"),
    path(
        "get-reported-post-details/<int:post_id>/",
        get_reported_post_details,
        name="get_reported_post_details",
    ),
    path(
        "delete-reported-post/<int:post_id>/",
        delete_reported_post,
        name="delete_reported_post",
    ),
    path("delete-report/<int:post_id>/", delete_report, name="delete_report"),
]
