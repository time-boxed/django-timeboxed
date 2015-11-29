# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pomodoro', '0002_favorite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pomodoro',
            name='created',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
