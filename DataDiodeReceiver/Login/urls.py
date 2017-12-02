from django.conf.urls import url
from Login import views

urlpatterns = [

    url(r'^$', views.loginReceiver, name='login'),  #---------receiver---------
    url(r'^logout/$', views.logoutUser, name='logout'),
]
