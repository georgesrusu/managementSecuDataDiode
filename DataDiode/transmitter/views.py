from django.http import Http404,HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.conf import settings
from .forms import UploadFileForm
import datetime
import os


def adminInterface(request):
    if settings.DATADIODESTATUSTRANSMITTER == "halted":
        messages.info(request,
                      "The data diode transmitter is halted. You can continue to add files, they will be sent when the transmitter will be started.")
    if request.method == 'POST':
        createUserFolder(request)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request, request.FILES['file'])
            allFiles = getAllFilesFromFolder(request)
            form = UploadFileForm()
            context = {"allFiles": allFiles, "form": form,"type":"running"}
            return render(request, 'adminTransmitter.html', context)
        raise Http404
    else:
        createUserFolder(request)
        allFiles = getAllFilesFromFolder(request)
        form = UploadFileForm()
        context = {"allFiles": allFiles, "form": form, "type":"running"}
        return render(request, 'adminTransmitter.html', context)

def userInterface(request):
    if settings.DATADIODESTATUSTRANSMITTER == "halted":
        messages.info(request,
                      "The data diode transmitter is halted. You can continue to add files, they will be sent when the transmitter will be started. For more information please address to your systems administrator!")
    if request.method == 'POST':
        print("uploading form")
        createUserFolder(request)
        form = UploadFileForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            handle_uploaded_file(request,request.FILES['file'])
            allFiles = getAllFilesFromFolder(request)
            form = UploadFileForm()
            context = {"allFiles": allFiles, "form": form}
            return render(request, 'userTransmitter.html',context)
        raise Http404
    else:
        createUserFolder(request)
        allFiles=getAllFilesFromFolder(request)
        form = UploadFileForm()
        context={"allFiles":allFiles,"form":form}
        return render(request, 'userTransmitter.html',context)

def createUserFolder(request):
    #wdInit=os.getcwd()
    cwd = settings.FOLDERTRANSMITTER
    #os.chdir(cwd)
    directory=request.user.username+";"+request.user.password+";"+str(request.user.is_staff)
    filename = os.path.join(cwd, directory)
    if not os.path.exists(filename):
        os.makedirs(filename)
    #os.chdir(wdInit)
    #print(os.getcwd())

def getAllFilesFromFolder(request):
    cwd = settings.FOLDERTRANSMITTER
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
    #print(os.getcwd())

def handle_uploaded_file(request,f):
    cwd = settings.FOLDERTRANSMITTER
    directory = request.user.username + ";" + request.user.password +";"+str(request.user.is_staff)+"/"
    currentDate=datetime.datetime.now()
    cwd += directory+str(currentDate.day)+":"+str(currentDate.month)+":"+str(currentDate.year)+";"+f.name
    with open(cwd, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)



def downloadFile(request):
    if request.method=="POST":
        fileToDownload=request.POST['fileToDownload']
        filename=fileToDownload.split(';')
        cwd = settings.FOLDERTRANSMITTER
        directory = request.user.username + ";" + request.user.password +";"+str(request.user.is_staff)+ "/"
        cwd+=directory
        file_path = os.path.join(cwd, fileToDownload)
        print(file_path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename='+filename[1]
                return response
    raise Http404


def deleteFile(request):
    if request.method=="POST":
        fileToDelete=request.POST['fileToDelete']
        cwd = settings.FOLDERTRANSMITTER
        directory = request.user.username + ";" + request.user.password +";"+str(request.user.is_staff)+"/"
        cwd+=directory
        file_path = os.path.join(cwd, fileToDelete)
        os.remove(file_path)
        if request.user.is_staff:
            return redirect('adminTransmitterInterface')
        else:
            return redirect('userTransmitterInterface')
    raise Http404

def setDataDiodeStatus(mode):
    status,pid=settings.DATADIODESTATUSTRANSMITTER, settings.DATADIODEPIDTRANSMITTER
    if mode=="running" and status=="halted":
        print('lancer data diode')
        settings.DATADIODEPID=10
    elif mode=="halted" and status=="running":
        print('eteint la data diode')
        settings.DATADIODEPID="stoppped"
    settings.DATADIODESTATUSTRANSMITTER=mode

def configure(request):
    if request.method=="POST":
        changeTo=request.POST['diodeStatus']
        folder = request.POST['folder']
        ip1=request.POST['ip1']
        ip2=request.POST['ip2']
        ip3 = request.POST['ip3']
        ip4 = request.POST['ip4']
        time = request.POST['time']
        settings.DATADIODESTATUSTRANSMITTER= changeTo
        settings.FOLDERTRANSMITTER=folder
        settings.RECEIVERADDRESSTRANSMITTER=str(ip1)+"."+str(ip2)+"."+str(ip3)+"."+str(ip4)
        settings.TIMETOSYNC=time
        print("service status : "+changeTo)
        print("settings status : " + settings.DATADIODESTATUSTRANSMITTER)
        print("folder : " + folder)
        print("settings folder : " + settings.FOLDERTRANSMITTER)
        print("receiver IP : " + folder)
        print("service status : " + str(ip1)+"."+str(ip2)+"."+str(ip3)+"."+str(ip4))
        print("service status : " + settings.RECEIVERADDRESSTRANSMITTER)
        print("time sync : " + time)
        print("time sync : " + settings.TIMETOSYNC)

        context={"dataDiodeStatus":changeTo,"folder":folder,"IP1":ip1,"IP2":ip2,"IP3":ip3,"IP4":ip4,"time":time}
        return render(request,'adminTransmitterConfig.html',context)
    else:
        ip1,ip2,ip3,ip4 = settings.RECEIVERADDRESSTRANSMITTER.split(".")
        context = {"dataDiodeStatus": settings.DATADIODESTATUSTRANSMITTER, "folder": settings.FOLDERTRANSMITTER, "IP1": ip1, "IP2": ip2, "IP3": ip3, "IP4": ip4,
                   "time": settings.TIMETOSYNC}
        return render(request, 'adminTransmitterConfig.html',context)