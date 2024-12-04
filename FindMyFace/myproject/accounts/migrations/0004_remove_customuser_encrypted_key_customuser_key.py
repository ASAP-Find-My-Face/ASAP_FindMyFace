# Generated by Django 5.1.3 on 2024-11-12 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_customuser_key_customuser_encrypted_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='encrypted_key',
        ),
        migrations.AddField(
            model_name='customuser',
            name='key',
            field=models.CharField(default='', editable=False, max_length=16),
        ),
    ]