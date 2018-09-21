from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'node/(?P<node_uuid>[0-9a-f-]+)/$', views.list_resources, name='list_resources'),
    url(r'resource/(?P<resource_uuid>[0-9a-f-]+)/$', views.detail_resource, name='detail_resource'),
    url(r'command/(?P<command_uuid>[0-9a-f-]+)/$', views.detail_command, name='detail_command'),
    url(r'$', views.home, name='home'),
]
