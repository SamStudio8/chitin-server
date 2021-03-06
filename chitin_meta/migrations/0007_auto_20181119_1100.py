# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-19 11:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

def set_default_resourcegroup_name(apps, schema_editor):
    ResourceGroup = apps.get_model('chitin_meta', 'ResourceGroup')
    for rg in ResourceGroup.objects.all():
        rg.name = str(rg.current_path)
        rg.physical = True
        rg.save()

class Migration(migrations.Migration):

    dependencies = [
        ('chitin_meta', '0006_command_group_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='groups',
            field=models.ManyToManyField(related_name='tagged_resources', to='chitin_meta.ResourceGroup'),
        ),
        migrations.AddField(
            model_name='resourcegroup',
            name='name',
            field=models.CharField(default='', max_length=512),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='resourcegroup',
            name='parent_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chitin_meta.ResourceGroup'),
        ),
        migrations.AddField(
            model_name='resourcegroup',
            name='physical',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.RunPython(set_default_resourcegroup_name),
    ]
