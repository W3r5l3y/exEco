# Generated by Django 4.2.19 on 2025-03-20 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contact", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactmessage",
            name="response",
            field=models.TextField(blank=True, null=True),
        ),
    ]
