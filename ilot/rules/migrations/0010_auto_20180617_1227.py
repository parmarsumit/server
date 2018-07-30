# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-17 12:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0009_type_overrides'),
    ]

    operations = [
        migrations.AlterField(
            model_name='type',
            name='scope',
            field=models.CharField(choices=[('event', 'Event'), ('item', 'Item'), ('children', '+Children'), ('descendants', '+Descendants')], default='item', max_length=96, verbose_name='and applies to '),
        ),
    ]
