from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import UserDevice
import hashlib

def home(request):
    return render(request,"home.html")


def signup(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.save()

        return redirect("login")

    return render(request,"signup.html")

def dashboard(request):

    if not request.user.is_authenticated:
        return redirect("login")

    return render(request,"dashboard.html")



def login_view(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:

            # device fingerprint
            user_agent = request.META.get('HTTP_USER_AGENT')
            ip = request.META.get('REMOTE_ADDR')

            device_string = user_agent + ip
            device_hash = hashlib.md5(device_string.encode()).hexdigest()

            obj, created = UserDevice.objects.get_or_create(user=user)

            # first login
            if obj.device_id == "":
                obj.device_id = device_hash
                obj.save()

            # login from another device
            elif obj.device_id != device_hash:

                obj.is_blocked = True
                obj.save()

                return render(request,"login.html",{
                    "error":"Account blocked. Logged in from another device."
                })

            if obj.is_blocked:
                return render(request,"login.html",{
                    "error":"Your account is blocked. Contact admin."
                })

            login(request,user)

            return redirect("dashboard")

    return render(request,"login.html")

def logout_view(request):
    logout(request)
    return redirect('login')    