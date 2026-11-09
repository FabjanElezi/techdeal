"""Fill an empty database with the demo catalogue (categories + products)."""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from aplikacion.models import Category, Product

CATALOG = {
    'Smartphones': [
        ('iPhone 16', '699', 'item/iphone_16__c5bvots96jee_xlarge_2.png', 'A18 chip, 48 MP Fusion camera and the new Camera Control button.', True),
        ('iPhone 16e', '599', 'item/iphone_16e.png', 'The essentials of iPhone 16 with A18 and all-day battery life.', False),
        ('iPhone 16 Pro', '1099', 'item/iphone16pro.png', 'Titanium design, A18 Pro and a 5x telephoto camera.', True),
        ('Samsung Galaxy S25 Ultra', '1545', 'item/Samsung_25_Ultra.png', '200 MP camera, built-in S Pen and Galaxy AI.', True),
        ('Samsung Galaxy S25+', '1245', 'item/SamsungS25plus.png', 'Big 6.7" screen, fast charging and Galaxy AI.', False),
        ('Samsung Galaxy S25', '1045', 'item/Samsungs25.png', 'Compact flagship with Snapdragon 8 Elite.', False),
    ],
    'Laptops & Tablets': [
        ('MacBook Air', '999', 'item/MacBookair.png', 'M-series chip, fanless and light, up to 18 hours of battery.', True),
        ('MacBook Pro', '1299', 'item/MacBookpro.png', 'Pro performance with a Liquid Retina XDR display.', False),
        ('iMac', '1599', 'item/imac.png', 'All-in-one desktop with a 24" 4.5K display.', False),
        ('Galaxy Tab S10', '945', 'item/galaxytab.png', 'AMOLED tablet with S Pen in the box.', False),
        ('Galaxy Tab S10+', '1145', 'item/galaxytab_s10.png', 'Larger 12.4" screen for work and play.', False),
        ('Galaxy Tab S10 FE+', '1245', 'item/galaxytab_s10_fe.png', 'Big-screen tablet with long battery life.', False),
    ],
    'Audio & Accessories': [
        ('AirPods Pro 2', '230', 'item/AirPods_pro2.png', 'Active noise cancellation and adaptive audio.', True),
        ('AirPods Max', '499', 'item/AirPods-Max-black.png', 'Over-ear headphones with high-fidelity sound.', False),
        ('HomePod mini', '299', 'item/HomePod_Mini.png', 'Small smart speaker with room-filling sound.', False),
        ('Galaxy Buds 3 Pro', '199', 'item/Galaxy_Buds_3_Pro.png', 'Noise-cancelling earbuds with Galaxy AI features.', False),
        ('Galaxy Ring', '150', 'item/GalaxyRing.png', 'Health tracking in a lightweight ring.', False),
        ('SmartTag', '30', 'item/SmartTag.png', 'Find your keys and bags with your phone.', False),
    ],
    'Smartwatches': [
        ('Apple Watch Series 10', '499', 'item/AppleWatchSeries10.png', 'Thinnest Apple Watch yet with a bigger display.', False),
        ('Apple Watch SE', '299', 'item/AppleWatchSE.png', 'The essential Apple Watch for fitness and safety.', False),
        ('Apple Watch Ultra 2', '799', 'item/AppleWatchUltra2.png', 'Rugged titanium watch for outdoor adventures.', True),
        ('Galaxy Watch 6', '199', 'item/GalaxyWatch6.png', 'Sleep coaching and health insights.', False),
        ('Galaxy Watch 7', '245', 'item/GalaxyWatch7.png', 'Dual-frequency GPS and Galaxy AI on your wrist.', False),
        ('Galaxy Watch Ultra', '345', 'item/GalaxyWatchUltra.png', 'Tough, long-lasting watch for every terrain.', False),
    ],
}


class Command(BaseCommand):
    help = 'Create the demo categories and products if the shop is empty.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Replace the existing catalogue.')

    @transaction.atomic
    def handle(self, *args, force=False, **options):
        if Product.objects.exists() and not force:
            # Keep photo paths in step with the files that ship with the app
            # (e.g. after a photo is re-exported in another format).
            images = {name: image for items in CATALOG.values() for name, _, image, _, _ in items}
            for product in Product.objects.filter(name__in=images):
                if product.image.name != images[product.name]:
                    product.image = images[product.name]
                    product.save(update_fields=['image'])
            return
        Product.objects.all().delete()
        Category.objects.all().delete()
        for cat_name, items in CATALOG.items():
            cat = Category.objects.create(name=cat_name)
            for name, price, image, description, featured in items:
                Product.objects.create(category=cat, name=name, price=Decimal(price),
                                       image=image, description=description, featured=featured)
        self.stdout.write(self.style.SUCCESS(f'Seeded {Product.objects.count()} products.'))
