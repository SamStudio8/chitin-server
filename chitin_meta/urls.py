from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    url(r'node/(?P<node_uuid>[0-9a-f-]+)/$', views.list_resources, name='list_resources'),
    url(r'node/(?P<group_uuid>[0-9a-f-]+)/$', views.list_resources, name='list_resource_group'),
    url(r'resource/(?P<resource_uuid>[0-9a-f-]+)/$', views.detail_resource, name='detail_resource'),
    url(r'command/(?P<command_uuid>[0-9a-f-]+)/$', views.detail_command, name='detail_command'),

    # API
    url(r'api/command/update/$', csrf_exempt(views.update_command), name='update_command'),
    url(r'api/command/new/$', csrf_exempt(views.new_command), name='new_command'),


    # Home
    url(r'$', views.home, name='home'),
]
