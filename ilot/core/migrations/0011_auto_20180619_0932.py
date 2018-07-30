# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-19 09:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0010_auto_20180617_1227'),
        ('core', '0010_inferedtype_silence'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='inferedtype',
            unique_together=set([('context', 'actor', 'type')]),
        ),
    ]
