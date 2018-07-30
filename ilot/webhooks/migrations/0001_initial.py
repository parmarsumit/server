# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-03 16:58
from __future__ import unicode_literals

from django.db import migrations, models
import ilot.core.manager
import ilot.core.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.CharField(default=ilot.core.manager.AppManager.get_new_uuid, editable=False, max_length=128, primary_key=True, serialize=False)),
                ('version', models.IntegerField(default=0, editable=False)),
                ('ref_time', models.BigIntegerField(default=ilot.core.manager.AppManager.get_ref_time, editable=False)),
                ('created_date', models.DateTimeField(default=ilot.core.manager.AppManager.get_valid_time, editable=False, verbose_name='created on')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='modified on')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('description', models.CharField(max_length=1024)),
                ('url', models.TextField(verbose_name='Url template')),
                ('method', models.CharField(choices=[('GET', 'GET'), ('POST', 'POST')], max_length=128)),
                ('basic_auth', models.CharField(blank=True, max_length=256, null=True, verbose_name='Basic Auth')),
                ('content_type', models.CharField(choices=[('application/json', 'JSON'), ('application/x-www-form-urlencoded', 'WWW')], max_length=128, verbose_name='Content-Type:')),
                ('headers', models.TextField(blank=True, null=True, verbose_name='Request headers template')),
                ('body', models.TextField(blank=True, null=True, verbose_name='Request body template')),
            ],
            options={
                'abstract': False,
            },
            bases=(ilot.core.models.ModelDiffMixin, models.Model),
        ),
        migrations.CreateModel(
            name='WebhookRequest',
            fields=[
                ('id', models.CharField(default=ilot.core.manager.AppManager.get_new_uuid, editable=False, max_length=128, primary_key=True, serialize=False)),
                ('version', models.IntegerField(default=0, editable=False)),
                ('ref_time', models.BigIntegerField(default=ilot.core.manager.AppManager.get_ref_time, editable=False)),
                ('created_date', models.DateTimeField(default=ilot.core.manager.AppManager.get_valid_time, editable=False, verbose_name='created on')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='modified on')),
                ('method', models.TextField(verbose_name='Method')),
                ('content_type', models.TextField(verbose_name='Content-Type')),
                ('url', models.TextField(verbose_name='Url')),
                ('basic_auth', models.TextField(blank=True, null=True, verbose_name='Basic Auth')),
                ('headers', models.TextField(blank=True, null=True, verbose_name='Headers')),
                ('content', models.TextField(verbose_name='Body')),
                ('done', models.BooleanField(default=False)),
                ('response', models.TextField(blank=True, null=True, verbose_name='Response')),
                ('response_code', models.TextField(blank=True, null=True, verbose_name='Response code')),
            ],
            options={
                'abstract': False,
            },
            bases=(ilot.core.models.ModelDiffMixin, models.Model),
        ),
    ]
