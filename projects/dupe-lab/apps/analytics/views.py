from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta


@staff_member_required
def analytics_dashboard(request):
    from apps.products.models import Product
    from apps.profiles.models import SkinProfile
    from apps.reviews.models import ProductReview, ProductReviewAggregate
    from apps.routines.models import Routine

    # ── Platform stats ────────────────────────────────────────
    total_products  = Product.objects.count()
    total_profiles  = SkinProfile.objects.count()
    total_reviews   = ProductReview.objects.count()
    total_routines  = Routine.objects.count()
    analysed_reviews = ProductReview.objects.filter(analysed=True).count()

    avg_rating = ProductReview.objects.filter(
        rating__isnull=False
    ).aggregate(avg=Avg('rating'))['avg']

    positive_count = ProductReview.objects.filter(sentiment_label='positive').count()
    negative_count = ProductReview.objects.filter(sentiment_label='negative').count()
    neutral_count  = ProductReview.objects.filter(sentiment_label='neutral').count()

    positive_pct = round(positive_count / analysed_reviews * 100, 1) if analysed_reviews else 0
    negative_pct = round(negative_count / analysed_reviews * 100, 1) if analysed_reviews else 0
    neutral_pct  = round(neutral_count  / analysed_reviews * 100, 1) if analysed_reviews else 0

    # ── Skin type distribution ────────────────────────────────
    skin_types = ['oily', 'dry', 'combination', 'sensitive', 'normal']
    skin_distribution = []
    for st in skin_types:
        count = SkinProfile.objects.filter(skin_type=st).count()
        skin_distribution.append({
            'type':  st.capitalize(),
            'count': count,
            'pct':   round(count / total_profiles * 100, 1) if total_profiles else 0,
        })
    skin_distribution.sort(key=lambda x: x['count'], reverse=True)

    # ── Category distribution ─────────────────────────────────
    category_counts = (
        Product.objects
        .values('category')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )

    # ── Top rated products ────────────────────────────────────
    top_rated = (
        Product.objects
        .filter(rank__isnull=False)
        .order_by('-rank')[:8]
    )

    # ── Most reviewed products ────────────────────────────────
    most_reviewed = (
        ProductReviewAggregate.objects
        .select_related('product')
        .filter(total_reviews__gt=0)
        .order_by('-total_reviews')[:8]
    )

    # ── Recent reviews ────────────────────────────────────────
    recent_reviews = (
        ProductReview.objects
        .select_related('product')
        .order_by('-created_at')[:10]
    )

    # ── Reviews over time (last 14 days) ─────────────────────
    today = timezone.now().date()
    review_timeline = []
    for i in range(13, -1, -1):
        day   = today - timedelta(days=i)
        count = ProductReview.objects.filter(created_at__date=day).count()
        review_timeline.append({'day': day.strftime('%d %b'), 'count': count})

    # ── Price range distribution ──────────────────────────────
    price_ranges = [
        {'label': 'Under ₹200',    'min': 0,    'max': 200},
        {'label': '₹200–₹500',     'min': 200,  'max': 500},
        {'label': '₹500–₹1000',    'min': 500,  'max': 1000},
        {'label': '₹1000–₹2000',   'min': 1000, 'max': 2000},
        {'label': 'Over ₹2000',    'min': 2000, 'max': 999999},
    ]
    for pr in price_ranges:
        pr['count'] = Product.objects.filter(
            price__gte=pr['min'], price__lt=pr['max']
        ).count()

    return render(request, 'analytics/dashboard.html', {
        # Stats
        'total_products':   total_products,
        'total_profiles':   total_profiles,
        'total_reviews':    total_reviews,
        'total_routines':   total_routines,
        'analysed_reviews': analysed_reviews,
        'avg_rating':       round(avg_rating, 2) if avg_rating else None,
        # Sentiment
        'positive_pct':     positive_pct,
        'neutral_pct':      neutral_pct,
        'negative_pct':     negative_pct,
        'positive_count':   positive_count,
        'neutral_count':    neutral_count,
        'negative_count':   negative_count,
        # Distributions
        'skin_distribution':  skin_distribution,
        'category_counts':    category_counts,
        'price_ranges':       price_ranges,
        # Products
        'top_rated':          top_rated,
        'most_reviewed':      most_reviewed,
        # Reviews
        'recent_reviews':     recent_reviews,
        'review_timeline':    review_timeline,
    })