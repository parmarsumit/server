# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-28 16:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grammar', '0007_panel_ajax'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='panel',
            name='ajax',
        ),
        migrations.AddField(
            model_name='panel',
            name='confirm',
            field=models.BooleanField(default=False, verbose_name='Ask for user confirm on direct submit'),
        ),
    ]
