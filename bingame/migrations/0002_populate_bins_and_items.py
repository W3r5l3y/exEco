# Generated by Django 4.2.19 on 2025-02-21 14:49

from django.db import migrations

def populate_bins_and_items(apps, schema_editor):
    Bins = apps.get_model('bingame', 'Bins')
    Items = apps.get_model('bingame', 'Items')


    bin_data = [
        {'bin_id': 1, 'bin_name': 'Plastic', 'bin_image': 'static/img/bins/plastic.png'},
        {'bin_id': 2, 'bin_name': 'Glass', 'bin_image': 'static/img/bins/glass.png'},
        {'bin_id': 3, 'bin_name': 'Card and Paper', 'bin_image': 'static/img/bins/card_paper.png'},
        {'bin_id': 4, 'bin_name': 'Tins and Cans', 'bin_image': 'static/img/bins/tins_cans.png'},
        {'bin_id': 5, 'bin_name': 'General Waste', 'bin_image': 'static/img/bins/general_waste.png'},
    ]

    for bin_entry in bin_data:
        Bins.objects.update_or_create(
            bin_id=bin_entry['bin_id'],
            defaults={
                'bin_name': bin_entry['bin_name'],
                'bin_image': bin_entry['bin_image'],
            }
        )

    item_data = [
        {'item_name': 'Plastic Bottle', 'item_image': 'static/img/items/plastic_bottle.png', 'bin_id': 1},
        {'item_name': 'Cardboard', 'item_image': 'static/img/items/cardboard.png', 'bin_id': 3},
        {'item_name': 'Glass Bottle', 'item_image': 'static/img/items/glass_bottle.png', 'bin_id': 2},
        {'item_name': 'Chip Packet', 'item_image': 'static/img/items/chip_packet.png', 'bin_id': 5},
        {'item_name': 'Drink Can', 'item_image': 'static/img/items/drink_can.png', 'bin_id': 4},
        {'item_name': 'Banana Peel', 'item_image': 'static/img/items/banana_peel.png', 'bin_id': 5},
        {'item_name': 'Newspaper', 'item_image': 'static/img/items/newspaper.png', 'bin_id': 3},
        {'item_name': 'Pizza box', 'item_image': 'static/img/items/pizza_box.png', 'bin_id': 5},
        {'item_name': 'Milk carton', 'item_image': 'static/img/items/milk_carton.png', 'bin_id': 3},
        {'item_name': 'Soap dispenser', 'item_image': 'static/img/items/soap_dispenser.png', 'bin_id': 1},
        {'item_name': 'Envelope', 'item_image': 'static/img/items/envelope.png', 'bin_id': 3},
        {'item_name': 'Broken mirror', 'item_image': 'static/img/items/broken_mirror.png', 'bin_id': 2},
        {'item_name': 'Coffee cup', 'item_image': 'static/img/items/coffee_cup.png', 'bin_id': 5},

    ]

    for item_entry in item_data:
        bin_instance = Bins.objects.get(bin_id=item_entry['bin_id'])
        Items.objects.update_or_create(
            item_name=item_entry['item_name'],
            defaults={
                'item_image': item_entry['item_image'],
                'bin_id': bin_instance,
            }
        )

def remove_bins_and_items(apps,schema_editor):
    Bins = apps.get_model('bingame', 'Bins')
    Items = apps.get_model('bingame', 'Items')
    
    Items.objects.all().delete()
    Bins.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('bingame', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_bins_and_items, reverse_code=remove_bins_and_items),
    ]