from django.http import Http404,HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.conf import settings
from .forms import UploadFileForm
import datetime
import os
import subprocess
from hashlib import sha256
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
@login_required(login_url='login')
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

@login_required(login_url='login')
def userInterface(request):
    if settings.DATADIODESTATUSTRANSMITTER == "halted":
        messages.info(request,
                      "The data diode transmitter is halted. You can continue to add files, they will be sent when the transmitter will be started. For more information please address to your systems administrator!")
    if request.method == 'POST':
        createUserFolder(request)
        form = UploadFileForm(request.POST, request.FILES)
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

@login_required(login_url='login')
def createUserFolder(request):
    cwd = settings.FOLDERTRANSMITTER
    directory = request.user.username + str(request.user.is_staff)
    directory = sha256(directory.encode()).hexdigest()
    directory+=";"+ request.user.password.replace("/",":")
    filename = os.path.join(cwd, directory)
    if not os.path.exists(filename):
        os.makedirs(filename)

@login_required(login_url='login')
def getAllFilesFromFolder(request):
    cwd = settings.FOLDERTRANSMITTER
    directory = request.user.username + str(request.user.is_staff)
    directory = sha256(directory.encode()).hexdigest()
    directory += ";" + request.user.password.replace("/", ":")
    cwd+=directory+"/"
    allFiles=os.listdir(cwd)
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

@login_required(login_url='login')
def handle_uploaded_file(request,f):
    cwd = settings.FOLDERTRANSMITTER
    directory = request.user.username + str(request.user.is_staff)
    directory = sha256(directory.encode()).hexdigest()
    directory += ";" + request.user.password.replace("/", ":")+"/"
    currentDate=datetime.datetime.now()
    cwd += directory+str(currentDate.day)+":"+str(currentDate.month)+":"+str(currentDate.year)+";"+f.name
    with open(cwd, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


@login_required(login_url='login')
def downloadFile(request):
    if request.method=="POST":
        fileToDownload=request.POST['fileToDownload']
        filename=fileToDownload.split(';')
        cwd = settings.FOLDERTRANSMITTER
        directory = request.user.username + str(request.user.is_staff)
        directory = sha256(directory.encode()).hexdigest()
        directory += ";" + request.user.password.replace("/", ":")
        cwd+=directory+"/"
        file_path = os.path.join(cwd, fileToDownload)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename='+filename[1]
                return response
    raise Http404

@login_required(login_url='login')
def deleteFile(request):
    if request.method=="POST":
        fileToDelete=request.POST['fileToDelete']
        cwd = settings.FOLDERTRANSMITTER
        directory = request.user.username + str(request.user.is_staff)
        directory = sha256(directory.encode()).hexdigest()
        directory += ";" + request.user.password.replace("/", ":")
        cwd += directory + "/"
        file_path = os.path.join(cwd, fileToDelete)
        os.remove(file_path)
        if request.user.is_staff:
            return redirect('adminTransmitterInterface')
        else:
            return redirect('userTransmitterInterface')
    raise Http404

def setDataDiodeStatus(changeTo):
    oldStatus=settings.DATADIODESTATUSTRANSMITTER
    if (changeTo=="running" and oldStatus=="halted"):
        cmd="python /home/transmitter/Desktop/DataDiodeTransmitter/BlindFTP_0.37/bftp.py -b -S "+str(settings.FOLDERTRANSMITTER)+" -a 10.37.129.6 -P "+ settings.TIMETOSYNC
        process = subprocess.Popen(cmd,shell=True)
        settings.DATADIODEPIDTRANSMITTER=process.pid
    elif (changeTo=="halted" and oldStatus=="running"):
        process = subprocess.Popen("kill " + str(settings.DATADIODEPIDTRANSMITTER+1), shell=True)
        settings.DATADIODEPIDTRANSMITTER = "stopped"

@login_required(login_url='login')
def configure(request):
    if request.method=="POST":
        changeTo=request.POST['diodeStatus']
        folder = request.POST['folder']
        ip1=request.POST['ip1']
        ip2=request.POST['ip2']
        ip3 = request.POST['ip3']
        ip4 = request.POST['ip4']
        ip5 = request.POST['ip5']
        ip6 = request.POST['ip6']
        ip7 = request.POST['ip7']
        ip8 = request.POST['ip8']
        ip9 = request.POST['ip9']
        ip10 = request.POST['ip10']
        ip11 = request.POST['ip11']
        ip12 = request.POST['ip12']
        time = request.POST['time']
        setDataDiodeStatus(changeTo)
        settings.DATADIODESTATUSTRANSMITTER= changeTo
        settings.FOLDERTRANSMITTER=folder
        ip=str(ip1)+"."+str(ip2)+"."+str(ip3)+"."+str(ip4)
        netmask=str(ip5)+"."+str(ip6)+"."+str(ip7)+"."+str(ip8)
        broadcast=str(ip9) + "." + str(ip10) + "." + str(ip11) + "." + str(ip12)
        changeWebServerIp(ip,netmask,broadcast)
        settings.WEBADDRESSTRANSMITTER=ip
        settings.NETMASKADDRESSTRANSMITTER =netmask
        settings.BROADCASTADDRESSTRANSMITTER=broadcast
        settings.TIMETOSYNC=time
        context={"dataDiodeStatus":changeTo,"folder":folder,"IP1":ip1,"IP2":ip2,"IP3":ip3,"IP4":ip4,"time":time,"IP5": ip5, "IP6": ip6, "IP7": ip7, "IP8": ip8,"IP9": ip9, "IP10": ip10, "IP11": ip11, "IP12": ip12}
        return render(request,'adminTransmitterConfig.html',context)
    else:
        ip1,ip2,ip3,ip4 = settings.WEBADDRESSTRANSMITTER.split(".")
        ip5, ip6, ip7, ip8 = settings.NETMASKADDRESSTRANSMITTER.split(".")
        ip9, ip10, ip11, ip12 = settings.BROADCASTADDRESSTRANSMITTER.split(".")
        context = {"dataDiodeStatus": settings.DATADIODESTATUSTRANSMITTER, "folder": settings.FOLDERTRANSMITTER, "IP1": ip1, "IP2": ip2, "IP3": ip3, "IP4": ip4,
                   "time": settings.TIMETOSYNC,"IP5": ip5, "IP6": ip6, "IP7": ip7, "IP8": ip8,"IP9": ip9, "IP10": ip10, "IP11": ip11, "IP12": ip12}
        return render(request, 'adminTransmitterConfig.html',context)


def changeWebServerIp(ip,netmask,broadcast):
    oldip,oldmask,oldbroad = settings.WEBADDRESSTRANSMITTER,settings.NETMASKADDRESSTRANSMITTER,settings.BROADCASTADDRESSTRANSMITTER
    if (oldip != ip or oldmask != netmask or oldbroad!=broadcast):
        oldfile = open("/home/transmitter/Desktop/DataDiodeTransmitter/interfaces","r")
        newfile = open("/home/transmitter/Desktop/DataDiodeTransmitter/interfacesTemp.txt", "w")
        for line in oldfile:
            newfile.write(line)
            if str(line) == "auto enp0s5\n":
                line=oldfile.readline()
                if str(line)=="iface enp0s5 inet dhcp\n":
                    newfile.write("iface enp0s5 inet static\n")
                    newfile.write("\taddress "+str(ip)+"\n")
                    newfile.write("\tnetmask " + str(netmask) + "\n")
                    newfile.write("\tbroadcast "+str(broadcast)+"\n")
                if str(line)=="iface enp0s5 inet static\n":
                    oldfile.readline()
                    oldfile.readline()
                    oldfile.readline()
                    newfile.write("iface enp0s5 inet static\n")
                    newfile.write("\taddress "+str(ip)+"\n")
                    newfile.write("\tnetmask " + str(netmask) + "\n")
                    newfile.write("\tbroadcast "+str(broadcast)+"\n")
        oldfile.close()
        newfile.close()
        newfile = open("/home/transmitter/Desktop/DataDiodeTransmitter/interfacesTemp.txt", "r")
        content=newfile.read()
        newfile.close()
        oldfile = open("/home/transmitter/Desktop/DataDiodeTransmitter/interfaces", "w")
        oldfile.write(content)
        oldfile.close()
        os.remove("/home/transmitter/Desktop/DataDiodeTransmitter/interfacesTemp.txt")
        #cmd = "sudo /sbin/reboot"
        #process = subprocess.Popen(cmd, shell=True)
        os.system("reboot") 
