from django.core.management.base import BaseCommand
from apps.products.price_fetcher import refresh_all_prices

class Command(BaseCommand):
    help = 'Refresh prices for stale products via Serper API'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100,
                            help='Max number of products to update')

    def handle(self, *args, **options):
        limit   = options['limit']
        self.stdout.write(f'Refreshing prices for up to {limit} products...')
        updated = refresh_all_prices(limit=limit)
        self.stdout.write(
            self.style.SUCCESS(f'Done. Updated prices for {updated} products.')
        )