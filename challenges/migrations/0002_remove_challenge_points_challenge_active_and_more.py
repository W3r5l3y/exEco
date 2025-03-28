# Generated by Django 4.2.19 on 2025-03-06 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("challenges", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="challenge",
            name="points",
        ),
        migrations.AddField(
            model_name="challenge",
            name="active",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="challenge",
            name="last_assigned",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="challenge",
            name="reward",
            field=models.PositiveIntegerField(default=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="challenge",
            name="description",
            field=models.CharField(max_length=255),
        ),
        migrations.DeleteModel(
            name="UserChallenge",
        ),
    ]
