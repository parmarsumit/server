# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-15 07:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0016_auto_20180715_0753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='behavior',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='behaviors', to='rules.Action', verbose_name='Request behavior '),
        ),
        migrations.AlterField(
            model_name='action',
            name='webhook',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='actions', to='webhooks.Webhook', verbose_name='Webhook'),
        ),
    ]
