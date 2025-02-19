from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("closed_listing", views.closed_listing, name="closed_listing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createlisting, name="createlisting"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("<int:listing_id>/watchlist_button", views.watchlist_button, name="watchlist_button"),
    path("watchlist_page", views.watchlist_page, name="watchlist_page"),
    path("<int:listing_id>/placebid", views.placebid, name="placebid"),
    path("<int:listing_id>/close_auction", views.close_auction, name="close_auction"),
    
    path("vehicles", views.vehicles, name="vehicles"),
    path("real_estate", views.real_estate, name="real_estate"),
    path("electronices", views.electronics, name="electronics"),
    path("fashion_accessories", views.fashion_accessories, name="fashion_accessories"),
    path("home_garden", views.home_garden, name="home_garden"),
    path("hobbies_leisure", views.hobbies_leisure, name="hobbies_leisure"),
    path("services", views.services, name="services"),
    path("professional_equipment", views.professional_equipment, name="professional_equipment"),
    path("pets", views.pets, name="pets"),
    path("others", views.others, name="others"),
]
