from django.http import Http404,HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
from django.contrib import messages
import os
import subprocess
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
@login_required(login_url='login')
def adminInterface(request):
    if settings.DATADIODESTATUSRECEIVER == "halted":
        messages.info(request,
                      "The data diode receiver is halted. You cannot receive files until the reception is turned off.")
    allFiles = getAllFilesFromFolder(request)
    context = {"allFiles": allFiles}
    return render(request, 'adminReceiver.html',context)
@login_required(login_url='login')
def userInterface(request):
    if settings.DATADIODESTATUSRECEIVER == "halted":
        messages.info(request,
                      "The data diode receiver is halted. You cannot receive files until the reception is turned on. For more information please address to your systems administrator!")
    allFiles = getAllFilesFromFolder(request)
    context = {"allFiles": allFiles}
    return render(request, 'userReceiver.html', context)
@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
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

def setDataDiodeStatus(changeTo):
    oldStatus=settings.DATADIODESTATUSRECEIVER
    if (changeTo=="running" and oldStatus=="halted"):
        cmd="python BlindFTP_0.37/bftp.py -r "+str(settings.FOLDERRECEIVER)+" -a 10.37.129.6"
        process = subprocess.Popen(cmd,shell=True)
        settings.DATADIODEPIDRECEIVER=process.pid
    elif (changeTo=="halted" and oldStatus=="running"):
        process = subprocess.Popen("kill " + str(settings.DATADIODEPIDRECEIVER), shell=True)
        settings.DATADIODEPIDRECEIVER = "stopped"

@login_required(login_url='login')
def configureReceiver(request):
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
        setDataDiodeStatus(changeTo)
        settings.DATADIODESTATUSRECEIVER= changeTo
        settings.FOLDERRECEIVER=folder
        ip=str(ip1)+"."+str(ip2)+"."+str(ip3)+"."+str(ip4)
        netmask=str(ip5)+"."+str(ip6)+"."+str(ip7)+"."+str(ip8)
        broadcast=str(ip9) + "." + str(ip10) + "." + str(ip11) + "." + str(ip12)
        changeWebServerIp(ip,netmask,broadcast)
        settings.WEBADDRESSRECEIVER=ip
        settings.NETMASKADDRESSRECEIVER =netmask
        settings.BROADCASTADDRESSRECEIVER=broadcast
        context={"dataDiodeStatus":changeTo,"folder":folder,"IP1":ip1,"IP2":ip2,"IP3":ip3,"IP4":ip4,"IP5": ip5, "IP6": ip6, "IP7": ip7, "IP8": ip8,"IP9": ip9, "IP10": ip10, "IP11": ip11, "IP12": ip12}
        return render(request,'adminReceiverConfig.html',context)
    else:
        ip1,ip2,ip3,ip4 = settings.WEBADDRESSRECEIVER.split(".")
        ip5, ip6, ip7, ip8 = settings.NETMASKADDRESSRECEIVER.split(".")
        ip9, ip10, ip11, ip12 = settings.BROADCASTADDRESSRECEIVER.split(".")
        context = {"dataDiodeStatus": settings.DATADIODESTATUSRECEIVER, "folder": settings.FOLDERRECEIVER, "IP1": ip1, "IP2": ip2, "IP3": ip3, "IP4": ip4,"IP5": ip5, "IP6": ip6, "IP7": ip7, "IP8": ip8,"IP9": ip9, "IP10": ip10, "IP11": ip11, "IP12": ip12}
        return render(request, 'adminReceiverConfig.html',context)


def changeWebServerIp(ip,netmask,broadcast):
    oldip,oldmask,oldbroad = settings.WEBADDRESSRECEIVER,settings.NETMASKADDRESSRECEIVER,settings.BROADCASTADDRESSRECEIVER
    if (oldip != ip or oldmask != netmask or oldbroad!=broadcast):
        #TODO A changer
        cwd = os.getcwd()
        oldfile = open(cwd+"/etc/network/interfaces","r")
        newfile = open(cwd+"/etc/network/interfacesTemp.txt", "w")
        for line in oldfile:
            print(line)
            newfile.write(line)
            if str(line) == "allow-hotplug enp0s5\n":
                oldfile.readline()
                oldfile.readline()
                oldfile.readline()
                oldfile.readline()
                newfile.write("iface enp0s5 inet static\n")
                newfile.write("\taddress "+str(ip)+"\n")
                newfile.write("\tnetmask " + str(netmask) + "\n")
                newfile.write("\tbroadcast "+str(broadcast)+"\n")
        oldfile.close()
        newfile.close()
        newfile = open(cwd + "/etc/network/interfacesTemp.txt", "r")
        content=newfile.read()
        newfile.close()
        oldfile = open(cwd + "/etc/network/interfaces", "w")
        oldfile.write(content)
        oldfile.close()
        #os.rename(cwd+"/etc/network/interfacesTemp",cwd+"/etc/network/interfaces")
        os.remove(cwd+"/etc/network/interfacesTemp.txt")
        #cmd = "/etc/init.d/networking restart"
        #process = ess.Popen(cmd, shell=True)