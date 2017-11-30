from django.conf.urls import url
from receiver import views

urlpatterns = [

    url(r'^adminConfig/$', views.adminInterface, name='adminReceiverInterface'),
    url(r'^userConfig/$', views.userInterface, name='userReceiverInterface'),
    url(r'^downloadFiles/$', views.downloadFile, name='downloadReceiverFile'),
    url(r'^deleteFile/$', views.deleteFile, name='deleteReceiverFile'),
]
