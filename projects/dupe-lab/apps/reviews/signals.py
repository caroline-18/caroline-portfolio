import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction


@receiver(post_save, sender='reviews.ProductReview')
def analyse_review_on_save(sender, instance, created, **kwargs):
    """Schedule NLP analysis in a background thread after the DB transaction commits."""
    if instance.analysed:
        return

    product_id = instance.product_id
    review_pk  = instance.pk

    def run():
        from apps.reviews.models import ProductReview
        from apps.reviews.sentiment_engine import analyse_review

        try:
            review  = ProductReview.objects.get(pk=review_pk)
            results = analyse_review(review.body)
            ProductReview.objects.filter(pk=review_pk).update(**results)
            _rebuild_aggregate(product_id)
        except Exception as e:
            print(f"[reviews] Analysis failed for review {review_pk}: {e}")

    # Wait until the current transaction is committed, then fire in a thread
    transaction.on_commit(lambda: threading.Thread(target=run, daemon=True).start())


def _rebuild_aggregate(product_id: int):
    from .models import ProductReview, ProductReviewAggregate
    from django.db.models import Avg, Count

    qs = ProductReview.objects.filter(product_id=product_id, analysed=True)
    stats = qs.aggregate(
        total=Count('id'),
        avg_rating=Avg('rating'),
        avg_hydration=Avg('aspect_hydration'),
        avg_texture=Avg('aspect_texture'),
        avg_scent=Avg('aspect_scent'),
        avg_irritation=Avg('aspect_irritation'),
        avg_efficacy=Avg('aspect_efficacy'),
    )

    total = stats['total'] or 0
    if total > 0:
        pos_pct  = round(qs.filter(sentiment_label='positive').count() / total * 100, 1)
        neu_pct  = round(qs.filter(sentiment_label='neutral').count()  / total * 100, 1)
        neg_pct  = round(qs.filter(sentiment_label='negative').count() / total * 100, 1)
    else:
        pos_pct = neu_pct = neg_pct = None

    ProductReviewAggregate.objects.update_or_create(
        product_id=product_id,
        defaults={
            'total_reviews':  total,
            'avg_rating':     stats['avg_rating'],
            'positive_pct':   pos_pct,
            'neutral_pct':    neu_pct,
            'negative_pct':   neg_pct,
            'avg_hydration':  stats['avg_hydration'],
            'avg_texture':    stats['avg_texture'],
            'avg_scent':      stats['avg_scent'],
            'avg_irritation': stats['avg_irritation'],
            'avg_efficacy':   stats['avg_efficacy'],
        }
    )