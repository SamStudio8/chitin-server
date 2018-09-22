# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import os
import json
from datetime import datetime

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



def new_command(request):
    #TODO Check valid JSON etc...
    json_data = json.loads(request.body)

    cmd_uuid = json_data["cmd_uuid"]
    cmd_str = json_data["cmd_str"]
    user = json_data.get("user", "somebody")
    queued_at = datetime.fromtimestamp(json_data["queued_at"])

    c = models.Command(id=cmd_uuid)
    c.cmd_str = cmd_str
    c.user = user
    c.queued_at = queued_at
    c.save()

    return HttpResponse(json.dumps({
        "cmd_uuid": c.id,
    }), content_type="application/json")

#def update_command(request, command_uuid):
def update_command(request):

    #TODO Check valid JSON etc...
    json_data = json.loads(request.body)
    c = get_object_or_404(models.Command, id=json_data["cmd_uuid"])

    started_at = datetime.fromtimestamp(json_data["started_at"])
    finished_at = datetime.fromtimestamp(json_data["finished_at"])
    return_code = json_data["return_code"]

    c.started_at = started_at
    c.finished_at = finished_at
    c.return_code = return_code
    c.save()

    resources = json_data.get("resources", [])
    if len(resources) == 0:
        # Command didn't have any effects, just ignore for now
        #TODO Delete uuid?
        return HttpResponse(json.dumps({
            "cmd_uuid": command_uuid,
            "updated": False,
            "reason": "No resources were affected",
        }), content_type="application/json")


    n_warnings = 0
    effect_code = 'X'
    updated_resources = []
    ignored_resources = []
    for resource in json_data.get("resources", {}):
        try:
            node = models.Node.objects.get(pk=resource["node_uuid"])

            dir_group = models.ResourceGroup.get_by_path(str(node.id), os.path.dirname(resource["path"]))
            if not dir_group:
                # New directory!
                dir_group = models.ResourceGroup()
                dir_group.current_node = node
                dir_group.current_path = os.path.dirname(resource["path"])
                dir_group.save()

            res = models.Resource.get_by_path(node.id, resource["path"])
            if not res:
                # New resource!
                #TODO Override the RES save to auto-build COR (or vice versa)
                effect_code = 'C'
                res = models.Resource()
            else:
                if not resource["exists"]:
                    # Deleted
                    effect_code = 'D'
                elif resource["hash"] is not None and res.current_hash != resource["hash"]:
                    # Modified
                    effect_code = 'M'
                else:
                    # Used
                    # Assume the file has just been used if the hash hasn't been updated
                    effect_code = 'U'

            cor = models.CommandOnResource()
            cor.command = c
            cor.resource = res
            cor.resource_hash = resource["hash"]
            cor.resource_size = resource["size"]
            cor.effect_status = effect_code
            cor.save()

            if effect_code != 'U':
                # If something happened

                if effect_code == 'D':
                    #TODO Might have to suppress adding the hash and size after rm
                    res.ghost = True
                else:
                    # If the file wasn't deleted
                    res.current_node = node
                    res.current_path = resource["path"]
                    res.current_hash = resource["hash"]
                    res.current_size = resource["size"]
                    res.current_master_group = dir_group

                res.save()

            updated_resources.append({
                "res_uuid": str(res.id),
                "res_path": res.current_path,
                "effect_code": effect_code
            })

        except Exception as e:
            n_warnings += 1
            ignored_resources.append({resource["path"]: str(e)})
            continue


    #meta...

    return HttpResponse(json.dumps({
        "cmd_uuid": str(c.id),
        "updated_resources": updated_resources,
        "ignored_resources": ignored_resources,
        "updated": True,
        "warnings": n_warnings,
    }), content_type="application/json")
