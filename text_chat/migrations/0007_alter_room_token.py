# Generated by Django 4.2.17 on 2025-02-02 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('text_chat', '0006_alter_room_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='token',
            field=models.CharField(default='CMG4kxfJvveF5Py1W41u', max_length=255),
        ),
    ]
