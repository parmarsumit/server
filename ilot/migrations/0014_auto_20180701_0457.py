# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-01 04:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ilot', '0013_auto_20180629_1056'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='address',
        ),
        migrations.AddField(
            model_name='interface',
            name='data',
            field=models.TextField(default='{}'),
        ),
    ]
