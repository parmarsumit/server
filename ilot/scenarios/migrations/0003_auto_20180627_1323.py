# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-27 13:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ilot', '0012_interface_action'),
        ('scenarios', '0002_step_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenario',
            name='entry_url',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='scenario',
            name='interface',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ilot.Interface'),
        ),
    ]
