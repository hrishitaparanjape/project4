from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User
from .models import Post
from django.contrib.auth.decorators import login_required


def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    return render(request, "network/index.html", {
        "posts": posts
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def new_post(request):
    if request.method == "POST":
        content = request.POST["content"]
        image_url = request.POST["image_url"]
        user = request.user

        # Create new post
        post = Post(content=content, image_url=image_url, user=user)
        post.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/new_post.html")
    
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).order_by('-timestamp')
    is_following = request.user in user.followers.all()

    return render(request, "network/profile.html", {
        "profile_user": user,
        "posts": posts,
        "is_following": is_following
    })

def follow_button(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if request.user in user_to_follow.followers.all():
        user_to_follow.followers.remove(request.user)
    else:
        user_to_follow.followers.add(request.user)

    return HttpResponseRedirect(reverse('profile', args=[username]))