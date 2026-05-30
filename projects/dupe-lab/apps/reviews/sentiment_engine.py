"""
Sentiment + aspect extraction for ProductReview.

Models used:
  - distilbert-base-uncased-finetuned-sst-2-english  (sentiment)
  - zero-shot-classification via facebook/bart-large-mnli  (aspects)

Both are loaded once at module level (lazy on first call) so they don't
slow down Django startup.
"""

from __future__ import annotations
import re
from typing import Optional

_sentiment_pipe = None
_zeroshot_pipe  = None

ASPECTS = {
    'hydration':  ['hydrating', 'moisturising', 'moisturizing', 'dry', 'dewy',
                   'quenching', 'hydration', 'moisture'],
    'texture':    ['texture', 'consistency', 'thick', 'thin', 'lightweight',
                   'heavy', 'greasy', 'silky', 'smooth', 'gritty'],
    'scent':      ['scent', 'smell', 'fragrance', 'odour', 'odor',
                   'perfume', 'unscented', 'fragrance-free'],
    'irritation': ['irritating', 'irritation', 'stinging', 'burning',
                   'breakout', 'purging', 'redness', 'sensitive', 'reaction'],
    'efficacy':   ['works', 'effective', 'results', 'improved', 'cleared',
                   'faded', 'brightened', 'reduced', 'no difference', 'useless'],
}

# Maps SST-2 labels → our labels
_LABEL_MAP = {'POSITIVE': 'positive', 'NEGATIVE': 'negative'}


def _get_sentiment_pipe():
    global _sentiment_pipe
    if _sentiment_pipe is None:
        from transformers import pipeline
        _sentiment_pipe = pipeline(
            'sentiment-analysis',
            model='distilbert-base-uncased-finetuned-sst-2-english',
            truncation=True,
            max_length=512,
        )
    return _sentiment_pipe


def _get_zeroshot_pipe():
    global _zeroshot_pipe
    if _zeroshot_pipe is None:
        from transformers import pipeline
        _zeroshot_pipe = pipeline(
            'zero-shot-classification',
            model='facebook/bart-large-mnli',
        )
    return _zeroshot_pipe


def analyse_sentiment(text: str) -> dict:
    """
    Returns:
        {'label': 'positive'|'neutral'|'negative', 'score': float}
    """
    pipe   = _get_sentiment_pipe()
    result = pipe(text[:512])[0]
    label  = _LABEL_MAP.get(result['label'], 'neutral')
    score  = round(result['score'], 4)

    # Downgrade to neutral when confidence is low
    if score < 0.65:
        label = 'neutral'

    return {'label': label, 'score': score}


def _keyword_present(text_lower: str, keywords: list[str]) -> bool:
    return any(kw in text_lower for kw in keywords)


def extract_aspects(text: str) -> dict[str, Optional[float]]:
    """
    Keyword-gated zero-shot aspect scoring.

    For each aspect, first check if any keyword appears in the text.
    If not, return None (aspect not mentioned).
    If yes, use zero-shot classification to score positive sentiment
    toward that aspect (0.0–1.0).

    Returns:
        {
          'hydration':  float|None,
          'texture':    float|None,
          'scent':      float|None,
          'irritation': float|None,
          'efficacy':   float|None,
        }
    """
    text_lower = text.lower()
    results    = {}

    # Collect aspects that are actually mentioned
    mentioned = {
        aspect: keywords
        for aspect, keywords in ASPECTS.items()
        if _keyword_present(text_lower, keywords)
    }

    if not mentioned:
        return {aspect: None for aspect in ASPECTS}

    # Run zero-shot once for all mentioned aspects (batched candidate labels)
    candidate_labels = [
        f"good {aspect}" for aspect in mentioned
    ] + [
        f"bad {aspect}"  for aspect in mentioned
    ]

    pipe   = _get_zeroshot_pipe()
    output = pipe(text[:1024], candidate_labels=candidate_labels, multi_label=True)

    score_map = dict(zip(output['labels'], output['scores']))

    for aspect in ASPECTS:
        if aspect not in mentioned:
            results[aspect] = None
        else:
            pos = score_map.get(f"good {aspect}", 0.5)
            neg = score_map.get(f"bad {aspect}",  0.5)
            # Normalise to 0–1 where 1 = very positive sentiment for this aspect
            total = pos + neg
            results[aspect] = round(pos / total, 4) if total > 0 else 0.5

    return results


def analyse_review(text: str) -> dict:
    """
    Full pipeline: sentiment + aspects.

    Returns dict ready to unpack onto a ProductReview instance:
        {
          'sentiment_label': str,
          'sentiment_score': float,
          'aspect_hydration':  float|None,
          'aspect_texture':    float|None,
          'aspect_scent':      float|None,
          'aspect_irritation': float|None,
          'aspect_efficacy':   float|None,
          'analysed': True,
        }
    """
    sentiment = analyse_sentiment(text)
    aspects   = extract_aspects(text)

    return {
        'sentiment_label':    sentiment['label'],
        'sentiment_score':    sentiment['score'],
        'aspect_hydration':   aspects['hydration'],
        'aspect_texture':     aspects['texture'],
        'aspect_scent':       aspects['scent'],
        'aspect_irritation':  aspects['irritation'],
        'aspect_efficacy':    aspects['efficacy'],
        'analysed':           True,
    }