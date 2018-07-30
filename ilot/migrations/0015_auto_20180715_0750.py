# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-15 07:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ilot', '0014_auto_20180701_0457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='action',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='rules.Action'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='application',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='interfaces', to='ilot.Organization'),
        ),
    ]
