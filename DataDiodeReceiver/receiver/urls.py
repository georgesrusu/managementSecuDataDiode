from django.conf.urls import url
from receiver import views

urlpatterns = [

    url(r'^AdminConfig/$', views.adminInterface, name='adminReceiverInterface'),
    url(r'^UserConfig/$', views.userInterface, name='userReceiverInterface'),
    url(r'^DownloadFiles/$', views.downloadFile, name='downloadReceiverFile'),
    url(r'^DeleteFile/$', views.deleteFile, name='deleteReceiverFile'),
    url(r'^Configuration/$', views.configureReceiver, name='configReceiver'),
]
