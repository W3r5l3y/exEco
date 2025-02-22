# Generated by Django 4.2.19 on 2025-02-21 19:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bins',
            fields=[
                ('bin_id', models.AutoField(primary_key=True, serialize=False)),
                ('bin_name', models.CharField(max_length=100)),
                ('bin_image', models.ImageField(upload_to='static/img/bins/')),
            ],
        ),
        migrations.CreateModel(
            name='Items',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('item_name', models.CharField(max_length=100)),
                ('item_image', models.ImageField(upload_to='static/img/items/')),
                ('bin_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bingame.bins')),
            ],
        ),
        migrations.CreateModel(
            name='BinLeaderboardEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_score', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='leaderboard_entry', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
