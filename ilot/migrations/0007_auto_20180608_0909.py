# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-08 09:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ilot', '0006_organization_application'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='application',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='applications', to='ilot.Organization'),
        ),
    ]
