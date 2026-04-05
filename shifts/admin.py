from django.contrib import admin
from .models import Shift

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')
    search_fields = ('name',)
    
    fieldsets = (
        ('Shift Details', {
            'fields': ('name', 'start_time', 'end_time')
        }),
    )
