from django.urls import path

from apps.favorites.api.v1.views import FavoriteView

urlpatterns = [
    path("", FavoriteView.as_view(), name="favorites"),
]
