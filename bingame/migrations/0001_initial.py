# Generated by Django 4.2.19 on 2025-03-04 23:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Bins",
            fields=[
                ("bin_id", models.AutoField(primary_key=True, serialize=False)),
                ("bin_name", models.CharField(max_length=100)),
                ("bin_image", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Items",
            fields=[
                ("item_id", models.AutoField(primary_key=True, serialize=False)),
                ("item_name", models.CharField(max_length=100)),
                ("item_image", models.CharField(max_length=255)),
                (
                    "bin_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bingame.bins"
                    ),
                ),
            ],
        ),
    ]
