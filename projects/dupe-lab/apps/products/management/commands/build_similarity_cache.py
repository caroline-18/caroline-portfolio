"""
Management command: build_similarity_cache
==========================================
Computes pairwise cosine similarity for all products and stores
results in the SimilarityCache table.

This is an O(n²) operation — run after any bulk product import.

Usage:
    python manage.py build_similarity_cache
"""
import time
from django.core.management.base import BaseCommand
from apps.products.models import Product
from apps.recommendations.similarity_engine import SimilarityEngine


class Command(BaseCommand):
    help = 'Compute and cache ingredient similarity scores for all products'

    def handle(self, *args, **options):
        product_count = Product.objects.count()
        if product_count == 0:
            self.stdout.write(self.style.ERROR("No products found. Run 'load_products' first."))
            return

        self.stdout.write(f"Computing similarities for {product_count} products...")
        self.stdout.write("This may take a moment for large datasets.\n")

        start = time.time()
        engine = SimilarityEngine()

        try:
            cached = engine.build_and_cache_all()
            elapsed = time.time() - start
            self.stdout.write(self.style.SUCCESS(
                f"Done! Cached {cached} similarity pairs in {elapsed:.1f}s"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            raise
