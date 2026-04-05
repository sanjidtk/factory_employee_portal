from django.shortcuts import render
from .models import Overtime
from accounts.decorators import admin_required

@admin_required
def overtime_list(request):
    overtimes = Overtime.objects.all().select_related('employee', 'attendance')
    return render(request, 'overtime/overtime_list.html', {'overtimes': overtimes})
