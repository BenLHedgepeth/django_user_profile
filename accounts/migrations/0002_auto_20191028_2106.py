# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2019-10-29 04:06
from __future__ import unicode_literals

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(upload_to=accounts.models.image_file_path),
        ),
    ]
