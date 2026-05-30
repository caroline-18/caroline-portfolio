from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import SkinProfile, SkinConcern
from .quiz_engine import classify_skin_type, extract_concerns

@login_required
def quiz_view(request):
    if request.method == 'POST':
        numeric_fields = ['shine', 'breakouts', 'tightness', 'redness',
                          'pores', 'flakiness', 'reaction', 'dark_spots', 'fine_lines']

        answers = {}
        for field in numeric_fields:
            val = request.POST.get(field, '0')
            if val.isdigit():
                answers[field] = int(val)

        skin_type     = classify_skin_type(answers)
        concern_slugs = extract_concerns(answers)

        profile, _        = SkinProfile.objects.get_or_create(user=request.user)
        profile.skin_type = skin_type
        profile.climate   = request.POST.get('climate', 'temperate')
        profile.age_range = request.POST.get('age_range', '25-34')
        profile.save()

        concerns = SkinConcern.objects.filter(slug__in=concern_slugs)
        profile.concerns.set(concerns)

        return redirect('profile_result')

    return render(request, 'profiles/quiz.html')

@login_required
def profile_result(request):
    profile = SkinProfile.objects.filter(user=request.user).first()
    if not profile:
        return redirect('quiz')
    return render(request, 'profiles/profile_result.html', {'profile': profile})

@login_required
def profile_detail(request):
    profile = SkinProfile.objects.filter(user=request.user).first()
    return render(request, 'profiles/profile_result.html', {'profile': profile})