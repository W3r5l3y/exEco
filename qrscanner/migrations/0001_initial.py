# Generated by Django 4.2.19 on 2025-03-22 16:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def populate_qr_locations(apps, schema_editor):
    Location = apps.get_model("qrscanner", "Location")
    locations = [
        {
            "location_code": "0001",
            "location_name": "Forum",
            "location_fact": "The Forum at the University of Exeter is a modern, sustainably designed hub at the heart of the Streatham Campus. Its landscape features a series of interconnected ponds that collect and filter rainwater, enhancing both aesthetics and environmental sustainability. Surrounded by native planting and a wildflower meadow, the ponds create a biodiverse habitat that attracts dragonflies, birds, and other wildlife. The water features, combined with contemporary architecture and green spaces, make the Forum a vibrant and inviting area for students and visitors, blending natural beauty with sustainable innovation.",
            "cooldown_length": 3600,
            "location_value": 10,
            "is_active": True,
            "image": "qrscanner/locations/0001.png",
            "latitude": 50.7352134,
            "longitude": -3.5335332,
        },
        {
            "location_code": "0002",
            "location_name": "Reed Pond",
            "location_fact": "Reed Pond, located on the University of Exeter's Streatham Campus, is an ornamental pond with historical significance. Originally part of the Veitch-designed landscape surrounding Streatham Hall (now Reed Hall), it remains a key feature of the campus gardens. The pond is characterized by its serene setting, lush vegetation, and reflective waters, contributing to the area's tranquil atmosphere. It serves as both a scenic attraction and a habitat for local wildlife, supporting aquatic plants and various species of birds and amphibians. Reed Pond continues to be a cherished element of the university's green spaces, offering a peaceful retreat within the campus.",
            "cooldown_length": 7200,
            "location_value": 15,
            "is_active": True,
            "image": "qrscanner/locations/0002.png",
            "latitude": 50.7341376,
            "longitude": -3.5378137,
        },
    ]
    for location in locations:
        Location.objects.create(**location)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "location_code",
                    models.CharField(max_length=4, primary_key=True, serialize=False),
                ),
                ("location_name", models.CharField(max_length=255)),
                ("location_fact", models.TextField()),
                ("cooldown_length", models.IntegerField()),
                ("times_visited", models.IntegerField(default=0)),
                ("location_value", models.IntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="qrscanner/locations/"
                    ),
                ),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="ScanRecord",
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
                ("last_scanned", models.DateTimeField(auto_now=True)),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="qrscanner.location",
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
            options={
                "unique_together": {("user", "location")},
            },
        ),
        migrations.RunPython(populate_qr_locations),
    ]
