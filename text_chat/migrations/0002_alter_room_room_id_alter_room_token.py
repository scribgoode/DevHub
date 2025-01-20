# Generated by Django 4.2.17 on 2025-01-20 05:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('text_chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_id',
            field=models.UUIDField(default=uuid.UUID('56526f21-6157-43e7-abb4-765eb47a8b06'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='token',
            field=models.CharField(default='qaI08IfqYMopfPlLgNtW', max_length=255),
        ),
    ]
