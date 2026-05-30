"""
Management command: load_products
==================================
Loads skincare product data from a CSV file into the database.

Usage:
    python manage.py load_products
    python manage.py load_products --csv path/to/custom.csv
    python manage.py load_products --clear   (delete existing before loading)
"""
import csv
import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from apps.products.models import Product


SKIN_TYPE_MAP = {
    'dry': 'skin_dry',
    'oily': 'skin_oily',
    'normal': 'skin_normal',
    'combination': 'skin_combination',
    'sensitive': 'skin_sensitive',
}

DEFAULT_CSV = Path(__file__).resolve().parents[5] / 'data' / 'skincare_products.csv'


class Command(BaseCommand):
    help = 'Load skincare products from CSV into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default=str(DEFAULT_CSV),
            help='Path to the CSV file (default: data/skincare_products.csv)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing products before loading',
        )

    def handle(self, *args, **options):
        csv_path = options['csv']

        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        if options['clear']:
            count = Product.objects.count()
            Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {count} existing products."))

        created = 0
        updated = 0
        errors = 0

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                try:
                    brand = row.get('brand', '').strip()
                    name = row.get('product_name', '').strip()
                    category = row.get('product_category', 'other').strip().lower()
                    ingredients = row.get('ingredients', '').strip()

                    if not brand or not name or not ingredients:
                        self.stdout.write(self.style.WARNING(
                            f"Row {row_num}: skipping — missing brand, name, or ingredients"
                        ))
                        continue

                    # Parse price
                    price = None
                    raw_price = row.get('price', '').strip()
                    if raw_price:
                        try:
                            price = float(raw_price.replace('$', '').replace(',', ''))
                        except ValueError:
                            pass

                    # Parse rank/rating
                    rank = None
                    raw_rank = row.get('rank', '').strip()
                    if raw_rank:
                        try:
                            rank = float(raw_rank)
                        except ValueError:
                            pass

                    # Parse skin types (pipe or comma separated in one column)
                    skin_type_str = row.get('skin_type', '').strip().lower()
                    skin_flags = {}
                    for st in SKIN_TYPE_MAP:
                        skin_flags[SKIN_TYPE_MAP[st]] = st in skin_type_str

                    defaults = {
                        'category': category,
                        'price': price,
                        'rank': rank,
                        'ingredients': ingredients,
                        **skin_flags,
                    }

                    product, was_created = Product.objects.update_or_create(
                        brand=brand,
                        name=name,
                        defaults=defaults,
                    )

                    if was_created:
                        created += 1
                    else:
                        updated += 1

                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(f"Row {row_num}: error — {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Created: {created}  |  Updated: {updated}  |  Errors: {errors}"
        ))

        if created + updated > 0:
            self.stdout.write(
                "\nNext step: run 'python manage.py build_similarity_cache' to compute similarities."
            )
