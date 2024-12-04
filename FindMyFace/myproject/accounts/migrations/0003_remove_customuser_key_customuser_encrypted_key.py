# Generated by Django 5.1.3 on 2024-11-12 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='key',
        ),
        migrations.AddField(
            model_name='customuser',
            name='encrypted_key',
            field=models.BinaryField(default=b'null'),
            preserve_default=False,
        ),
    ]