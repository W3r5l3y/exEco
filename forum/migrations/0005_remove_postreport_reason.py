# Generated by Django 4.2.19 on 2025-03-16 16:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("forum", "0004_postreport"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="postreport",
            name="reason",
        ),
    ]
