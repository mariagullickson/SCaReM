# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-05-31 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SCaReM', '0002_auto_20170525_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='recurrence_id',
            field=models.IntegerField(null=True),
        ),
    ]