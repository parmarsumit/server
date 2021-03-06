# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-12 05:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0006_auto_20180611_0854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='datatype',
            field=models.CharField(choices=[('string', 'Word'), ('title', 'Title (A sentence)'), ('description', 'Description (A text)'), ('markdown', 'Markdown (A markdown text)'), ('target', 'Target Selector'), ('query', 'Target Query'), ('image', 'Media Selector'), ('uploader', 'Media Uploader'), ('datetime', 'DateTime chooser'), ('number', 'Number'), ('integer', 'Integer'), ('boolean', 'Boolean'), ('email', 'Email'), ('url', 'Url'), ('slug', 'Slug field (this-is-a-slug)'), ('parent', 'Parent Item (An item)'), ('start', 'Start Datetime (Core)'), ('end', 'End Datetime (Core)')], default='string', max_length=36),
        ),
    ]
