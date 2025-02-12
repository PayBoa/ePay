from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createlisting, name="createlisting"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("<int:listing_id>/watchlist_button", views.watchlist_button, name="watchlist_button"),
    path("watchlist_page", views.watchlist_page, name="watchlist_page"),
    path("<int:listing_id>/placebid", views.placebid, name="placebid"),
]
