from django.conf.urls import url
from Login import views

urlpatterns = [

    #url(r'^$', views.loginTransmitter, name='login'),
    url(r'^$', views.loginReceiver, name='login'),
    url(r'^logout/$', views.logoutUser, name='logout'),
]
