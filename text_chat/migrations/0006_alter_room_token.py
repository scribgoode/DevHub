# Generated by Django 4.2.17 on 2025-02-02 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('text_chat', '0005_alter_room_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='token',
            field=models.CharField(default='8h0aShMaT04y7nFq5JKz', max_length=255),
        ),
    ]
