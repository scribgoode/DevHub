# Generated by Django 4.2.17 on 2025-01-23 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('text_chat', '0005_alter_room_room_id_alter_room_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='token',
            field=models.CharField(default='m5cm3Cxn0MPH8RfJi4Mu', max_length=255),
        ),
    ]
