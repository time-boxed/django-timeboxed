# Generated by Django 3.2.16 on 2023-11-29 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='key',
            field=models.CharField(max_length=256),
        ),
    ]