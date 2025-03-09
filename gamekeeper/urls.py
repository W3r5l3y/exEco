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
)

urlpatterns = [
    path('gamekeeper/', gamekeeper_view, name='gamekeeper'),
    path('add-location-to-qr/<str:location_code>/<str:location_name>/<str:location_fact>/<int:cooldown_length>/<int:location_value>/', add_location_to_qr, name='add_location_to_qr'),
    path('unlink-strava/<int:user_id>/', unlink_strava, name='unlink_strava'),
    path('get-strava-links/', get_strava_links, name='get_strava_links'),
    path('add-item-to-bingame/', add_item_to_bingame, name='add_item_to_bingame'),
    path('add-points/<str:type>/<int:user_id>/<int:amount>/', add_points, name='add_points'),
    path('get-qr-codes/', get_qr_codes, name='get_qr_codes'),
    path('enable-qr/<str:qr_id>/', enable_qr, name='enable_qr'),
    path('disable-qr/<str:qr_id>/', disable_qr, name='disable_qr'),
    path('get-user-ids/', get_user_ids, name='get_user_ids'),
]
