# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 09:02
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserAccount', '0016_auto_20170723_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 24, 9, 2, 5, 439776)),
        ),
    ]
