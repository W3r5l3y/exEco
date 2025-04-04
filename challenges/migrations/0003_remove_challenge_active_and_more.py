# Generated by Django 4.2.19 on 2025-03-07 01:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("challenges", "0002_remove_challenge_points_challenge_active_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="challenge",
            name="active",
        ),
        migrations.RemoveField(
            model_name="challenge",
            name="last_assigned",
        ),
        migrations.AlterField(
            model_name="challenge",
            name="reward",
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.CreateModel(
            name="UserChallenge",
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
                ("completed", models.BooleanField(default=False)),
                ("assigned_at", models.DateTimeField(auto_now_add=True)),
                (
                    "challenge",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="challenges.challenge",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
