# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-03 00:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outputfile',
            name='text',
            field=models.CharField(max_length=10000, verbose_name='CSV Text'),
        ),
    ]
