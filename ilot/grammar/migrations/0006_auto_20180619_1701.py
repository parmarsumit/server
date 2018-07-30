# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-19 17:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('grammar', '0005_notification_discards'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['type', 'status', 'target']},
        ),
        migrations.AlterField(
            model_name='notification',
            name='discards',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='discarding', to='grammar.Notification', verbose_name='Discards ...'),
        ),
    ]
