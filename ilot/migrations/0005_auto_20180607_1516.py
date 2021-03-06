# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-07 15:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0004_auto_20180607_1516'),
        ('grammar', '0003_auto_20180606_1048'),
        ('ilot', '0004_auto_20180606_0553'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='behavior',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='rules.Action'),
        ),
        migrations.AddField(
            model_name='organization',
            name='content',
            field=models.TextField(default='{% extends "index.html" %}'),
        ),
        migrations.AddField(
            model_name='organization',
            name='notification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='grammar.Notification'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='cname',
            field=models.CharField(blank=True, max_length=128, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(blank=True, max_length=128, null=True, unique=True),
        ),
    ]
