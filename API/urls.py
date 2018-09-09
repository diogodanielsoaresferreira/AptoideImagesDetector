from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^md5sum=(?P<app_md5>[0-9a-zA-Z]+)/(reload=(?P<cache_reload>(0|1))/)?$', views.getbyMD5, name='md5'),
    url(r'^id=(?P<app_id>[0-9]+)/(reload=(?P<cache_reload>(0|1))/)?$', views.getbyId, name='id'),
]