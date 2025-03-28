# Generated by Django 4.2.19 on 2025-03-10 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="inventoryitem",
            name="aesthetic_appeal",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inventoryitem",
            name="carbon_uptake",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inventoryitem",
            name="habitat",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inventoryitem",
            name="health_of_garden",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inventoryitem",
            name="innovation",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inventoryitem",
            name="waste_reduction",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="lootboxitem",
            name="aesthetic_appeal",
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name="lootboxitem",
            name="carbon_uptake",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="lootboxitem",
            name="habitat",
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name="lootboxitem",
            name="health_of_garden",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="lootboxitem",
            name="innovation",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="lootboxitem",
            name="waste_reduction",
            field=models.IntegerField(default=0),
        ),
    ]
