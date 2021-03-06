# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-12 05:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0007_auto_20180612_0549'),
        ('grammar', '0003_auto_20180606_1048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='panel',
            name='other_success',
        ),
        migrations.RemoveField(
            model_name='panel',
            name='other_title',
        ),
        migrations.AddField(
            model_name='panel',
            name='close',
            field=models.BooleanField(default=True, verbose_name='Close on success'),
        ),
        migrations.AddField(
            model_name='panel',
            name='redirect',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='rules.Action', verbose_name='Action to redirect on success'),
        ),
    ]
