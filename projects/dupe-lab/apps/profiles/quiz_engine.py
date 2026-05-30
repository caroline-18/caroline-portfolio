SKIN_TYPE_RULES = {
    'oily':        lambda a: a['shine'] >= 4 and a['pores'] >= 3,
    'dry':         lambda a: a['tightness'] >= 4 and a['flakiness'] >= 3,
    'combination': lambda a: a['shine'] >= 3 and a['tightness'] >= 2,
    'sensitive':   lambda a: a['redness'] >= 3 or a['reaction'] >= 4,
    'normal':      lambda a: True,  # fallback
}

def classify_skin_type(answers: dict) -> str:
    """
    answers = {
      'shine': 1-5, 'pores': 1-5, 'tightness': 1-5,
      'flakiness': 1-5, 'redness': 1-5, 'reaction': 1-5
    }
    """
    for skin_type, rule in SKIN_TYPE_RULES.items():
        if rule(answers):
            return skin_type
    return 'normal'

def extract_concerns(answers: dict) -> list[str]:
    concern_map = {
        'acne':             answers.get('breakouts', 0) >= 3,
        'hyperpigmentation':answers.get('dark_spots', 0) >= 3,
        'aging':            answers.get('fine_lines', 0) >= 3,
        'redness':          answers.get('redness', 0) >= 3,
        'dryness':          answers.get('tightness', 0) >= 3,
    }
    return [k for k, v in concern_map.items() if v]