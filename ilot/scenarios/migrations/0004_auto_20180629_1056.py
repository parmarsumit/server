# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-29 10:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scenarios', '0003_auto_20180627_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenario',
            name='interface',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='scenarios', to='ilot.Interface'),
        ),
        migrations.AlterField(
            model_name='step',
            name='next',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='following', to='scenarios.Step'),
        ),
    ]
