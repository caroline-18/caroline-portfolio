from django.core.management.base import BaseCommand
from apps.products.models import Product
from apps.recommendations.embedding_service import embed_product

class Command(BaseCommand):
    help = 'Generate embeddings for all products'

    def handle(self, *args, **kwargs):
        products = Product.objects.filter(embedding__isnull=True)
        total = products.count()
        self.stdout.write(f"Embedding {total} products...")

        for i, product in enumerate(products, 1):
            try:
                product.embedding = embed_product(product)
                product.save(update_fields=['embedding'])
                if i % 50 == 0:
                    self.stdout.write(f"  {i}/{total} done...")
            except Exception as e:
                self.stdout.write(f"  Failed: {product.name} — {e}")

        self.stdout.write(self.style.SUCCESS(f'Done. {total} products embedded.'))