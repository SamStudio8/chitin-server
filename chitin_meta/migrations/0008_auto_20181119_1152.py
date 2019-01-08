# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-19 11:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chitin_meta', '0007_auto_20181119_1100'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resourcegroup',
            old_name='parent_group',
            new_name='physical_parent_group',
        ),
        migrations.AddField(
            model_name='resourcegroup',
            name='groups',
            field=models.ManyToManyField(related_name='tagged_groups', to='chitin_meta.ResourceGroup'),
        ),
    ]