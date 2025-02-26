# Generated by Django 4.2.17 on 2025-02-22 23:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('video_chat', '0003_remove_meeting_room_alter_meeting_room_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='room_token',
            field=models.CharField(default='ldpjFbZMvxSqKgXOTAoq', max_length=255),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='status',
            field=models.CharField(default='upcoming', max_length=50),
        ),
        migrations.CreateModel(
            name='MeetingRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('topic', models.TextField()),
                ('sent_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='pending', max_length=50)),
                ('type', models.CharField(choices=[('in-person', 'in-person'), ('video', 'video'), ('text', 'text')], default='in-person', max_length=50)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_recipient', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
