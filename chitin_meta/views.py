# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from . import models

def home(request):
    return render(request, 'list_nodes.html', {
        "nodes": models.Node.objects.all()
    })

def list_resources(request, node_uuid):
    node = get_object_or_404(models.Node, id=node_uuid)
    return render(request, 'list_resources.html', {
        "resources": models.Resource.objects.filter(current_node = node),
        "node": node,
    })

def detail_resource(request, resource_uuid):
    return render(request, 'detail_resource.html', {
        "resource": get_object_or_404(models.Resource, id=resource_uuid)
    })

def detail_command(request, command_uuid):
    return render(request, 'detail_command.html', {
        "command": get_object_or_404(models.Command, id=command_uuid)
    })
