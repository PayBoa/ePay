from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment, Watchlist


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='login')
def createlisting(request):
    if request.method == "POST":
        # Get all infos from the form submitted
        title = request.POST["title"]
        description = request.POST["description"]
        startingbid = request.POST["startingbid"]
        category = request.POST["category"]
        image_url = request.POST.get("image_url", "").strip() 
        # If the field is empty, set it to the model’s default value
        if not image_url:
            image_url = Listing._meta.get_field("image_url").get_default()   
        owner = User.objects.get(username=request.user.username)
        
        # Create the Listing object and save it
        listing = Listing(
            title = title,
            description = description,
            starting_bid = startingbid,
            current_price = startingbid,  
            category = category,
            image_url = image_url if image_url else None,
            owner = owner
        )
        listing.save()

        # Return to index page
        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/createlisting.html")


def listing(request, listing_id):
    item = Listing.objects.get(id=listing_id) # Get all infos of the listing
    message = "" # Initialize message
    if request.user.is_authenticated: # Verify if user is logged in

        if Watchlist.objects.filter(user=request.user,listing=item.id).exists(): # If item is in user's watchlist
            message = "Remove from Watchlist"
        else:                                   # If item is not in user's watchlist
            message = "Add to Watchlist"        # Message : add to watchlist
    return render(request, "auctions/listing.html", {
        "item": item, 
        "message": message
    })

@login_required(login_url='login')
def watchlist_button(request, listing_id):
    if request.method == "POST":
        item = Listing.objects.get(id=listing_id) # Get all infos of the listing
        watchlist_entry = Watchlist.objects.filter(user=request.user, listing=item) # Get Watchlist entry for this item and this user
        if watchlist_entry.exists(): # If it exists, delete it
            watchlist_entry.delete()
        else:   # Else, create it
            Watchlist.objects.create(user=request.user, listing=item)   
    return redirect('listing', listing_id)

@login_required(login_url='login')
def watchlist_page(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    item_id = []
    for watchlist_item in watchlist_items:
        item_id.append(watchlist_item.listing.id)
    return render(request, "auctions/watchlist_page.html", {
        "listings": Listing.objects.filter(id__in=item_id)
    })

@login_required(login_url='login')
def placebid(request, listing_id):

    item = Listing.objects.get(id=listing_id)
    new_bid = request.POST["bid"]
    print(listing_id)
    print(request.user)
    print(item.title)
    print(new_bid)
    
    i = Listing(id=listing_id) 
    i.current_price = new_bid
    i.save()
    # BUGGING HERE
    return redirect('listing', listing_id)