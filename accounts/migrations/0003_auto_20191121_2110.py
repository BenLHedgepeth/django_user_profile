# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2019-11-22 05:10
from __future__ import unicode_literals

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20191028_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, upload_to=accounts.models.image_file_path),
        ),
    ]
