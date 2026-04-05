from django.shortcuts import render
from .models import Shift
from accounts.decorators import admin_required

@admin_required
def shift_list(request):
    shifts = Shift.objects.all()
    return render(request, 'shifts/shift_list.html', {'shifts': shifts})
