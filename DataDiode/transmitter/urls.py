from django.conf.urls import url
from transmitter import views

urlpatterns = [

    url(r'^AdminConfig/$', views.adminInterface, name='adminTransmitterInterface'),
    url(r'^UserConfig/$', views.userInterface, name='userTransmitterInterface'),
    url(r'^DownloadFiles/$', views.downloadFile, name='downloadFile'),
    url(r'^DeleteFile/$', views.deleteFile, name='deleteFile'),
    url(r'^DataDiodeStatus/$', views.changeDiodeStatus, name='dataDiodeStatus'),
    url(r'^Configuration/$', views.configure, name='config'),


]
