# Generated by Django 4.2.19 on 2025-03-09 17:00

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('inventory_id', models.AutoField(primary_key=True, serialize=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LootboxItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='inventory/items/')),
            ],
        ),
        migrations.CreateModel(
            name='LootboxTemplate',
            fields=[
                ('lootbox_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('lootbox_image', models.ImageField(blank=True, null=True, upload_to='inventory/lootboxes/')),
            ],
        ),
        migrations.CreateModel(
            name='LootboxContents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probability', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.lootboxitem')),
                ('lootbox_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='inventory.lootboxtemplate')),
            ],
        ),
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('item_type', models.CharField(choices=[('regular', 'Regular Item'), ('lootbox', 'Lootbox')], default='regular', max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='inventory/items/')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.inventory')),
                ('lootbox_template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.lootboxtemplate')),
            ],
        ),
    ]
