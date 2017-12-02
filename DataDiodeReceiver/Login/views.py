from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password,make_password
from .models import UserReceiver
import os

def loginTransmitter(request):
    if request.user.is_authenticated():
        if request.user.is_staff:
            return redirect('adminTransmitterInterface')
            #return redirect('adminReceiverInterface')
        else:
            return redirect('userTransmitterInterface')
            #return redirect('userReceiverInterface')

    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.is_staff:
                return redirect('adminTransmitterInterface')
                #return redirect('adminReceiverInterface')
            else:
                return redirect('userTransmitterInterface')
                #return redirect('userReceiverInterface')
        else:
            messages.error(request,"Username or Password incorrect!")
            return render(request, "index.html")
    else:
        return render(request,"index.html")


def logoutUser(request):
        logout(request)
        return render(request, "index.html")

def loginReceiver(request):
    if request.user.is_authenticated():
        if request.user.is_staff:
            return redirect('adminReceiverInterface')
        else:
            return redirect('userReceiverInterface')

    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.is_staff:
                return redirect('adminReceiverInterface')
            else:
                return redirect('userReceiverInterface')
        else:
            if (createUserFromFolder(username, password)):
                user = authenticate(request, username=username, password=password)
                login(request, user)
                if request.user.is_staff:
                    return redirect('adminReceiverInterface')
                else:
                    return redirect('userReceiverInterface')
            else:
                messages.error(request, "Username or Password incorrect!")
                return render(request, "index.html")
    else:
        return render(request,"index.html")



def createUserFromFolder(username,password):
    cwd = settings.FOLDERRECEIVER
    allFolder=os.listdir(cwd)
    for i in range(len(allFolder)):
        userFile = allFolder[i].split(";")
        if (userFile[0]==username):
            if (check_password(password,userFile[1])):
                user = UserReceiver.objects.create_user(username=username, password=password,passWordHashed=userFile[1],isStaff=userFile[2])
                return True
    return False
