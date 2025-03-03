from django.urls import path
from .views import shop_view
#from .views import null

urlspatterns = [
    path('shop/', shop_view, name='shop'),
]