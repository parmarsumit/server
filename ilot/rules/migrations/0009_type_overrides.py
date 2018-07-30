# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-15 15:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0008_attribute_regexp_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='type',
            name='overrides',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='overriding', to='rules.Type', verbose_name='Overrides type'),
        ),
    ]
