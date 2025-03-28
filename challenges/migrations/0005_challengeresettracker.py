# Generated by Django 5.1.7 on 2025-03-09 15:20

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("challenges", "0004_remove_userchallenge_assigned_at_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChallengeResetTracker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "last_daily_reset",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "last_weekly_reset",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
            ],
        ),
    ]
