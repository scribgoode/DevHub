# Generated by Django 4.2.17 on 2024-12-31 19:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_engineer_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engineer',
            name='dob',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
