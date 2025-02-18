# Generated by Django 4.2.19 on 2025-02-17 22:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_is_active_customuser_is_admin_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPoints',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('points_scored', models.IntegerField(default=0)),
            ],
        ),
    ]
