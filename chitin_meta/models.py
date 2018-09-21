# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
import os

from django.db import models


class Node(models.Model):
    """Any device or computer capable of storing a Resource, or executing a Command."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, unique=True, db_index=True)

    def __str__(self):
        return "%s (%s)" % (self.name, str(self.id)[-5:])

class ResourceGroup(models.Model):
    # A ResourceGroup could be an entire directory (indeed, that is the minimum),
    # but it could also be a pseudo-folder like group of files that make up a database, or an experiment.
    # A Resource must have a ResourceGroup, but can be attached to other groups as 'tags'.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    current_node = models.ForeignKey('Node')
    current_path = models.CharField(max_length=512)
    current_hash = models.CharField(max_length=64)
    current_size = models.BigIntegerField(default=0)

    ghost = models.BooleanField()

    current_master_group = models.ForeignKey('ResourceGroup') # represents the physical directory

    def __str__(self):
        return "%s (%s)" % (self.full_path, self.current_hash[-5:])

    @property
    def full_path(self):
        return "chitin://%s:%s" % (self.current_node.name, self.current_path)

    @property
    def hash_friends(self):
        """Return other Resources who share the current_hash, that are not the current Resource, or ghosted."""
        return Resource.objects.filter(
                current_hash = self.current_hash,
                ghost = False
        ).exclude(
                id = self.id
        )

    @property
    def adjacent_files(self):
        """Return other Resources who share the current directory, that are not ghosted."""
        #TODO Use master_group
        return Resource.objects.filter(
                # current_groups__in = [self.current_master_group],
                current_path__startswith = os.path.dirname(self.current_path),
                ghost= False
        )

    @property
    def ghosts(self):
        return Resource.objects.filter(
                current_path=self.current_path,
                ghost = True,
        ).exclude(
                id = self.id
        )

    @property
    def metadata(self):
        #TODO Future, flatten (tag, name) records if they have been 'overwritten'
        return MetaRecord.objects.filter(
                resource=self,
        ).order_by('-timestamp')

class Command(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cmd_str = models.CharField(max_length=512)
    return_code = models.SmallIntegerField()

    # group_uuid
    # group_order

    # queued_at
    # started_at
    # finished_at

    @property
    def metadata(self):
        #TODO Future, flatten (tag, name) records if they have been 'overwritten'
        return MetaRecord.objects.filter(
                command=self,
        ).order_by('-timestamp')


class CommandOnResource(models.Model):
    """Record of a Command having an effect on a Resource"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    resource = models.ForeignKey('Resource', related_name="effects")
    command = models.ForeignKey('Command', related_name="effects")

    resource_hash = models.CharField(max_length=64)
    resource_size = models.BigIntegerField(default=0)

    # effect_status

class MetaRecord(models.Model):
    """Metadata pertaining to:
        * A Command, such as run time, or its parameters,
        * A Resource, such as the number of lines or records inside of it,
        * A Command and Resource, indicating a record for a Command that has changed a Resource
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    resource = models.ForeignKey('Resource', null=True, blank=True)
    command = models.ForeignKey('Command', null=True, blank=True)

    meta_tag = models.CharField(max_length=64, db_index=True)
    meta_name = models.CharField(max_length=64)

    value_type = models.CharField(max_length=48)
    value = models.CharField(max_length=128)

    timestamp = models.DateTimeField()

    def translate(self):
        # if value_type == "datetime"...
        #   return strftime
        # elif value_type == "resource"...
        #   return lookup resource
        return self.value

