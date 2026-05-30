"""
Usage:
    python manage.py analyse_reviews
    python manage.py analyse_reviews --force        # re-analyse already-done reviews
    python manage.py analyse_reviews --limit 100
"""

from django.core.management.base import BaseCommand
from apps.reviews.models import ProductReview
from apps.reviews.sentiment_engine import analyse_review
from apps.reviews.signals import _rebuild_aggregate


class Command(BaseCommand):
    help = 'Run sentiment + aspect analysis on unanalysed reviews'

    def add_arguments(self, parser):
        parser.add_argument('--force',  action='store_true',
                            help='Re-analyse reviews that are already marked analysed')
        parser.add_argument('--limit', type=int, default=None,
                            help='Max number of reviews to process')

    def handle(self, *args, **options):
        qs = ProductReview.objects.all()
        if not options['force']:
            qs = qs.filter(analysed=False)
        if options['limit']:
            qs = qs[:options['limit']]

        total   = qs.count()
        updated = 0
        product_ids = set()

        self.stdout.write(f"Analysing {total} reviews…")

        for review in qs.iterator():
            try:
                results = analyse_review(review.body)
                ProductReview.objects.filter(pk=review.pk).update(**results)
                product_ids.add(review.product_id)
                updated += 1
                if updated % 10 == 0:
                    self.stdout.write(f"  {updated}/{total}")
            except Exception as e:
                self.stderr.write(f"  Failed review {review.pk}: {e}")

        self.stdout.write(f"Rebuilt aggregates for {len(product_ids)} products…")
        for pid in product_ids:
            _rebuild_aggregate(pid)

        self.stdout.write(self.style.SUCCESS(
            f"Done — {updated}/{total} reviews analysed."
        ))