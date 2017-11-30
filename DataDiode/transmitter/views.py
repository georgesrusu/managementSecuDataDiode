from django.http import Http404,HttpResponse
from django.shortcuts import render,redirect
from django.utils.encoding import smart_str

from .forms import UploadFileForm
import datetime
import os

def adminInterface(request):
    if request.method == 'POST':
        createUserFolder(request)

        return render(request, 'adminTransmitter.html')
    else:

        createUserFolder(request)
        form = UploadFileForm()
        return render(request, 'adminTransmitter.html')

def userInterface(request):
    if request.method == 'POST':
        print("uploading form")
        createUserFolder(request)
        form = UploadFileForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            handle_uploaded_file(request,request.FILES['file'])
            print('file')
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
    cwd = os.getcwd()
    cwd += "/bftpTransmit/"
    #os.chdir(cwd)
    directory=request.user.username+";"+request.user.password+";"+str(request.user.is_staff)
    filename = os.path.join(cwd, directory)
    if not os.path.exists(filename):
        os.makedirs(filename)
    #os.chdir(wdInit)
    #print(os.getcwd())

def getAllFilesFromFolder(request):
    cwd = os.getcwd()
    cwd += "/bftpTransmit/"
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
    cwd = os.getcwd()
    cwd += "/bftpTransmit/"
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
        cwd = os.getcwd()
        cwd += "/bftpTransmit/"
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
        cwd = os.getcwd()
        cwd += "/bftpTransmit/"
        directory = request.user.username + ";" + request.user.password +";"+str(request.user.is_staff)+"/"
        cwd+=directory
        file_path = os.path.join(cwd, fileToDelete)
        os.remove(file_path)
        if request.user.is_staff:
            return redirect('adminTransmitterInterface')
        else:
            return redirect('userTransmitterInterface')
    raise Http404
