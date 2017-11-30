from django.http import Http404,HttpResponse
from django.shortcuts import render,redirect
import os

def adminInterface(request):
    allFiles = getAllFilesFromFolder(request)
    context = {"allFiles": allFiles}
    return render(request, 'adminReceiver.html',context)

def userInterface(request):
    allFiles = getAllFilesFromFolder(request)
    context = {"allFiles": allFiles}
    return render(request, 'userReceiver.html', context)

def getAllFilesFromFolder(request):
    cwd = os.getcwd()
    cwd += "/bftpReceive/"
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
        cwd = os.getcwd()
        cwd += "/bftpReceive/"
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
        cwd = os.getcwd()
        cwd += "/bftpReceive/"
        directory = request.user.username + ";" + request.user.password +";"+str(request.user.is_staff)+"/"
        cwd+=directory
        file_path = os.path.join(cwd, fileToDelete)
        os.remove(file_path)
        if request.user.is_staff:
            return redirect('adminReceiverInterface')
        else:
            return redirect('userReceiverInterface')
    raise Http404