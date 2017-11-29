from django.shortcuts import render

def adminInterface(request):
    return render(request, 'adminReceiver.html')

def userInterface(request):
    return render(request, 'userReceiver.html')
