from django.conf.urls import url
from transmitter import views

urlpatterns = [

    url(r'^adminConfig/$', views.adminInterface, name='adminTransmitterInterface'),
    url(r'^userConfig/$', views.userInterface, name='userTransmitterInterface'),
    url(r'^download/$', views.downloadFile, name='downloadFile'),

]
