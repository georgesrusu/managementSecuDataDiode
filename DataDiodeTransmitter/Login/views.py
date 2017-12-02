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
        if username=="admin" and password=="admin" and settings.ADMINACCOUNT==0:
            settings.ADMINACCOUNT+=1
            return render(request,'adminReceiverConfig.html')
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
                user= User.objects.create_user(username=username,password=password,is_staff=userFile[2])
                oldFileName=cwd+allFolder[i];
                print(oldFileName)
                newFileName=cwd+username+";"+user.password+";"+userFile[2]
                print(newFileName)
                os.rename(oldFileName,newFileName)
                print("creation user")
                return True
    return False
