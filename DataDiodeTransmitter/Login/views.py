from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password,make_password
import os

def loginTransmitter(request):
    if request.user.is_authenticated():
        if request.user.is_staff:
            return redirect('adminTransmitterInterface')
        else:
            return redirect('userTransmitterInterface')

    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.is_staff:
                return redirect('adminTransmitterInterface')
            else:
                return redirect('userTransmitterInterface')
        else:
            messages.error(request,"Username or Password incorrect!")
            return render(request, "index.html")
    else:
        return render(request,"index.html")


def logoutUser(request):
        logout(request)
        return render(request, "index.html")
