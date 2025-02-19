# Generated by Django 5.1 on 2024-11-12 17:03

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_platform', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='id',
        ),
        migrations.AddField(
            model_name='video',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='video',
            name='video_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
