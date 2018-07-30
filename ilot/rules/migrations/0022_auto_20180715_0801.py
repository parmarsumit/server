# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-15 08:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0021_auto_20180715_0759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trigger',
            name='actor_type',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='triggers_as_actor', to='rules.Type', verbose_name='Trigger as ...'),
        ),
        migrations.AlterField(
            model_name='trigger',
            name='behavior',
            field=models.ForeignKey(db_constraint=False, help_text='Action to be triggered', on_delete=django.db.models.deletion.PROTECT, related_name='triggered', to='rules.Action'),
        ),
        migrations.AlterField(
            model_name='trigger',
            name='condition',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='Condition to be true to do the trigger', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='triggers', to='rules.Condition', verbose_name='if'),
        ),
        migrations.AlterField(
            model_name='trigger',
            name='target_type',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='triggers_as_target', to='rules.Type', verbose_name='Trigger to ...'),
        ),
        migrations.AlterField(
            model_name='trigger',
            name='type',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='triggers', to='rules.Type', verbose_name='on '),
        ),
        migrations.AlterField(
            model_name='type',
            name='overrides',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='overriding', to='rules.Type', verbose_name='Overrides type'),
        ),
    ]
