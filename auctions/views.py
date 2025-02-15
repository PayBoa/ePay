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

    # Minimum bid
    item = Listing.objects.get(id=listing_id)
    if not Bid.objects.filter(listing=listing_id):
        minimum_bid = int(item.starting_bid)
    else:
        minimum_bid = int(item.current_price) + 5

    # Count bid number
    bid_count = 0                                           # Initialize bid count
    listing_bids = Bid.objects.filter(listing=listing_id)   # Get all bids on the listing
    for bids in listing_bids:                               # Loop through all bids
        bid_count = bid_count + 1                               # Update bid count
    
    # Get last bid
    last_bid = Bid.objects.filter(listing=listing_id).order_by('-timestamp').first()

    # Your bid is the current bid message
    your_bid = ""
    if Bid.objects.filter(listing=listing_id).exists():
        if last_bid.user == request.user:
            your_bid = "Your bid is the current bid"
        

    # Add to watchlist button
    message = ""                                            # Initialize message
    if request.user.is_authenticated:                       # Verify if user is logged in

        if Watchlist.objects.filter(user=request.user,listing=listing_id).exists(): # If item is in user's watchlist
            message = "Remove from Watchlist"                                    # Message : remove from watchlist
        else:                                   # If item is not in user's watchlist
            message = "Add to Watchlist"        # Message : add to watchlist

    return render(request, "auctions/listing.html", {
        "item": item, 
        "message": message,
        "minimum_bid": minimum_bid,
        "bid_count": bid_count,
        "last_bid": last_bid,
        "your_bid": your_bid,
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
    watchlist_items = Watchlist.objects.filter(user=request.user) # Get all watchlist items for this user
    item_id = []                                                  # Initialize item_id array  
    for watchlist_item in watchlist_items:                        # Loop through all watchlist items
        item_id.append(watchlist_item.listing.id)                   # Add item id to the array  
    return render(request, "auctions/watchlist_page.html", {
        "listings": Listing.objects.filter(id__in=item_id)
    })

@login_required(login_url='login')
def placebid(request, listing_id):
    if request.method == "POST":
        new_bid = request.POST["bid"]           # Get new bid value
        i = Listing.objects.get(id=listing_id)  # Get listing's details

        if i.current_price <= int(new_bid):      # Check if new bid is higher than current price

            i.current_price = new_bid           # Set the new bid as the current price
            i.save()                            # Save new current price   

            bid = Bid(                          # Create new bid
                user = User.objects.get(username=request.user.username), 
                listing = Listing.objects.get(id=listing_id), 
                amount = new_bid)
            bid.save()                          # Save new bid
    return redirect('listing', listing_id)