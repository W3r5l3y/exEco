# Generated by Django 4.2.19 on 2025-03-06 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_usercoins"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="profile_picture",
            field=models.ImageField(blank=True, null=True, upload_to="profile_pics/"),
        ),
    ]
