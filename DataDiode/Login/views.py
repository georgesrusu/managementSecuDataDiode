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
        if username == "admin" and password == "admin" and settings.ADMINACCOUNT == 0:
            settings.ADMINACCOUNT += 1
            ip1, ip2, ip3, ip4 = settings.WEBADDRESSRECEIVER.split(".")
            ip5, ip6, ip7, ip8 = settings.NETMASKADDRESSRECEIVER.split(".")
            ip9, ip10, ip11, ip12 = settings.BROADCASTADDRESSRECEIVER.split(".")
            context = {"dataDiodeStatus": settings.DATADIODESTATUSRECEIVER, "folder": settings.FOLDERRECEIVER,
                       "IP1": ip1, "IP2": ip2, "IP3": ip3, "IP4": ip4, "IP5": ip5, "IP6": ip6, "IP7": ip7, "IP8": ip8,
                       "IP9": ip9, "IP10": ip10, "IP11": ip11, "IP12": ip12}
            return render(request, 'adminReceiverConfig.html',context)
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
    if os.path.exists(cwd):
        allFolder=os.listdir(cwd)
        for i in range(len(allFolder)):
            userFile = allFolder[i].split(";")
            if (userFile[0]==username):
                if (check_password(password,userFile[1].replace(":","/"))):
                    user = UserReceiver.objects.create_user(username=username, password=password,passWordHashed=userFile[1].replace("/",":"),isStaff=userFile[2])
                    return True
    return False
