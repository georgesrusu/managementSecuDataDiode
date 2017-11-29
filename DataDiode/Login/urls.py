from django.conf.urls import url
from Login import views

urlpatterns = [

    url(r'^$', views.loginUser, name='login'),
    url(r'^logout/$', views.logoutUser, name='logout'),
]
