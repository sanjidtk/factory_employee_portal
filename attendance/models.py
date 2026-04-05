from datetime import datetime, date, timedelta

from django.db import models
from django.core.exceptions import ValidationError

from employees.models import Employee
from shifts.models import Shift


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('On Leave', 'On Leave'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)
    late_minutes = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee} - {self.date}"

    def worked_hours(self):
        if self.status not in ['Present', 'Late']:
            return 0.0
        if not self.check_in or not self.check_out:
            return 0.0
        start = datetime.combine(date.today(), self.check_in)
        end = datetime.combine(date.today(), self.check_out)
        if end <= start:
            end += timedelta(days=1)
        return round((end - start).total_seconds() / 3600, 2)

    def save(self, *args, **kwargs):
        # Calculate lateness if present/late
        if self.status in ['Present', 'Late'] and self.shift and self.check_in:
            shift_start = datetime.combine(date.today(), self.shift.start_time)
            actual_checkin = datetime.combine(date.today(), self.check_in)
            if actual_checkin > shift_start:
                diff = (actual_checkin - shift_start).total_seconds() / 60
                if diff > 0:
                    self.is_late = True
                    self.late_minutes = int(diff)
                    self.status = 'Late'
                else:
                    self.is_late = False
                    self.late_minutes = 0
                    self.status = 'Present'
            else:
                self.is_late = False
                self.late_minutes = 0
                self.status = 'Present'

        super().save(*args, **kwargs)

        from overtime.models import Overtime
        if self.status in ['Present', 'Late'] and self.shift:
            worked = self.worked_hours()
            shift_hours = self.shift.duration_hours()
            over_hrs = round(worked - shift_hours, 2)
            if over_hrs > 0:
                Overtime.objects.update_or_create(
                    attendance=self,
                    defaults={
                        'employee': self.employee,
                        'date': self.date,
                        'hours': over_hrs,
                        'status': 'Pending',
                    }
                )
            else:
                Overtime.objects.filter(attendance=self).delete()
        else:
            Overtime.objects.filter(attendance=self).delete()
