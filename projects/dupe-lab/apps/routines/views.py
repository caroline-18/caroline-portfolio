from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.products.models import Product
from .models import Routine, RoutineStep
from .routine_engine import sort_products_into_routine, detect_conflicts

@login_required
def build_routine(request):
    if request.method == 'POST':
        product_ids  = request.POST.getlist('product_ids')
        routine_type = request.POST.get('routine_type', 'am')
        products     = list(Product.objects.filter(id__in=product_ids))

        routine = Routine.objects.create(
            user=request.user,
            name=f"My {routine_type.upper()} routine",
            routine_type=routine_type
        )

        steps = sort_products_into_routine(products, routine_type)
        for step in steps:
            RoutineStep.objects.create(
                routine=routine,
                product=step['product'],
                step_num=step['step_num']
            )

        conflicts = detect_conflicts(products)
        return render(request, 'routines/result.html', {
            'routine':   routine,
            'steps':     steps,
            'conflicts': conflicts,
        })

    products = Product.objects.all().order_by('category', 'name')
    return render(request, 'routines/builder.html', {'products': products})

@login_required
def my_routines(request):
    routines = Routine.objects.filter(user=request.user).prefetch_related('steps__product')
    return render(request, 'routines/my_routines.html', {'routines': routines})


@login_required
def delete_routine(request, routine_id):
    routine = Routine.objects.filter(id=routine_id, user=request.user).first()
    if routine:
        routine.delete()
    return redirect('my_routines')