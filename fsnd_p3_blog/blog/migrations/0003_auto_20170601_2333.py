# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-02 04:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20170523_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='publish_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]