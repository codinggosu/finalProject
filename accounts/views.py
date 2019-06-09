from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from catalog.models import Profile
# Create your views here.


def signup(request):
    if request.method == "POST":
        if request.POST["password1"] == request.POST["password2"] and request.POST["gender"] and request.POST["skin_type"] and request.POST["age"] and request.POST["nickname"]:

            user = User.objects.create_user(
                username=request.POST["username"], password=request.POST["password1"],
            )
            newprofile= Profile()
            newprofile.nickname = request.POST['nickname']
            newprofile.gender = request.POST["gender"]
            newprofile.skin_type = request.POST["skin_type"]
            newprofile.age = request.POST["age"]
            newprofile.profile_id = user.id
            newprofile.user = user
            newprofile.save()
            print(newprofile)
            user.profile = newprofile
            print(user)
            auth.login(request, user)
            return redirect('my_page')
        else:
            return render(request, 'signup.html', {'error': 'please enter the information correctly'})
    else:
        return render(request, 'signup.html')


def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('my_page')
        else:
            return render(request, 'login.html', {'error': 'user name or password is incorrect'})
    return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return render(request, 'login.html')
