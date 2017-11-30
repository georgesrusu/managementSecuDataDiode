from django.http import Http404,HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
from django.contrib import messages
import os

def adminInterface(request):
    if settings.DATADIODESTATUSRECEIVER == "halted":
        messages.info(request,
                      "The data diode transmitter is halted. You cannot receive files until the reception is turned off.")
    allFiles = getAllFilesFromFolder(request)
    context = {"allFiles": allFiles}
    return render(request, 'adminReceiver.html',context)

def userInterface(request):
    if settings.DATADIODESTATUSRECEIVER == "halted":
        messages.info(request,
                      "The data diode receiver is halted. You cannot receive files until the reception is turned on. For more information please address to your systems administrator!")
    allFiles = getAllFilesFromFolder(request)
    context = {"allFiles": allFiles}
    return render(request, 'userReceiver.html', context)

def getAllFilesFromFolder(request):
    cwd = settings.FOLDERRECEIVER
    directory = request.user.username + ";" + request.user.password+";"+str(request.user.is_staff)+"/"
    cwd+=directory
    allFiles=os.listdir(cwd)
    print(allFiles)
    for i in range(len(allFiles)):
        fileInfo = []
        filename=os.path.join(cwd, allFiles[i])
        fileInfo.append(allFiles[i])
        size = str(os.path.getsize(filename))
        fileInfo.append(size)
        filenameDate=allFiles[i].split(';')
        fileInfo.append(filenameDate[0])
        fileInfo.append(filenameDate[1])
        allFiles[i]=fileInfo
    return allFiles


def downloadFile(request):
    if request.method=="POST":
        fileToDownload=request.POST['fileToDownload']
        filename=fileToDownload.split(';')
        cwd = settings.FOLDERRECEIVER
        directory = request.user.username + ";" + request.user.password +";"+str(request.user.is_staff)+ "/"
        cwd+=directory
        file_path = os.path.join(cwd, fileToDownload)
        print(file_path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename='+filename[1]
                return response
        print("os path doensot exist")
    raise Http404


def deleteFile(request):
    if request.method=="POST":
        fileToDelete=request.POST['fileToDelete']
        cwd = settings.FOLDERRECEIVER
        directory = request.user.username + ";" + request.user.password +";"+str(request.user.is_staff)+"/"
        cwd+=directory
        file_path = os.path.join(cwd, fileToDelete)
        os.remove(file_path)
        if request.user.is_staff:
            return redirect('adminReceiverInterface')
        else:
            return redirect('userReceiverInterface')
    raise Http404

def configureReceiver(request):
    if request.method=="POST":
        changeTo=request.POST['diodeStatus']
        folder = request.POST['folder']
        ip1=request.POST['ip1']
        ip2=request.POST['ip2']
        ip3 = request.POST['ip3']
        ip4 = request.POST['ip4']
        settings.DATADIODESTATUSRECEIVER = changeTo
        settings.FOLDERRECEIVER=folder
        settings.RECEIVERADDRESSRECEIVER=str(ip1)+"."+str(ip2)+"."+str(ip3)+"."+str(ip4)
        print("service status : "+changeTo)
        print("settings status : " + settings.DATADIODESTATUSRECEIVER)
        print("folder : " + folder)
        print("settings folder : " + settings.FOLDERRECEIVER)
        print("receiver IP : " + folder)
        print("service status : " + str(ip1)+"."+str(ip2)+"."+str(ip3)+"."+str(ip4))
        print("service status : " + settings.RECEIVERADDRESSRECEIVER)

        context={"dataDiodeStatus":changeTo,"folder":folder,"IP1":ip1,"IP2":ip2,"IP3":ip3,"IP4":ip4}
        return render(request, "adminReceiverConfig.html", context)
    else:
        ip1,ip2,ip3,ip4 = settings.RECEIVERADDRESSRECEIVER.split(".")
        context = {"dataDiodeStatus": settings.DATADIODESTATUSRECEIVER, "folder": settings.FOLDERRECEIVER, "IP1": ip1, "IP2": ip2, "IP3": ip3, "IP4": ip4}
        return render(request,"adminReceiverConfig.html",context)