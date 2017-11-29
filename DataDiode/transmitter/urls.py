from django.conf.urls import url
from transmitter import views

urlpatterns = [

    url(r'^adminConfig/$', views.adminInterface, name='adminTransmitterInterface'),
    url(r'^userConfig/$', views.userInterface, name='userTransmitterInterface'),
    url(r'^downloadFiles/$', views.downloadFile, name='downloadFile'),
    url(r'^deleteFile/$', views.deleteFile, name='deleteFile'),

]
