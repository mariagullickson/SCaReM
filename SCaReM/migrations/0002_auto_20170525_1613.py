# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-05-25 16:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SCaReM', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='repeat_until',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='allow_conflicts',
            field=models.NullBooleanField(),
        ),
    ]
