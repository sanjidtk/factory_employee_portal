from datetime import datetime, date, timedelta

from django.db import models
from django.core.exceptions import ValidationError

from employees.models import Employee
from shifts.models import Shift


class Attendance(models.Model):

    STATUS_CHOICES = (
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Leave'),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='P'
    )

    shift = models.ForeignKey(
        Shift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    # System-calculated field (NOT editable in admin form)
    on_time_checkin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee} - {self.date}"

    # --------------------------------------------------
    # WORKED HOURS (CROSS-MIDNIGHT SAFE)
    # --------------------------------------------------
    def worked_hours(self):
        if self.status != 'P':
            return 0.0

        if not self.check_in_time or not self.check_out_time:
            return 0.0

        start = datetime.combine(date.today(), self.check_in_time)
        end = datetime.combine(date.today(), self.check_out_time)

        # Handle night / cross-midnight shift
        if end <= start:
            end += timedelta(days=1)

        return round((end - start).total_seconds() / 3600, 2)

    # --------------------------------------------------
    # ON-TIME CHECK-IN (SHIFT BASED)
    # --------------------------------------------------
    def calculate_on_time_checkin(self):
        self.on_time_checkin = False

        if self.status != 'P':
            return

        if not self.shift or not self.check_in_time:
            return

        shift_start = datetime.combine(date.today(), self.shift.start_time)

        # 10 minutes grace period
        allowed_time = shift_start + timedelta(minutes=10)
        actual_checkin = datetime.combine(date.today(), self.check_in_time)

        if actual_checkin <= allowed_time:
            self.on_time_checkin = True

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------
    def clean(self):
        if self.status != 'P':
            return

        if not self.shift or not self.check_in_time or not self.check_out_time:
            return

        shift_cross_midnight = self.shift.end_time <= self.shift.start_time
        time_cross_midnight = self.check_out_time <= self.check_in_time

        # Prevent invalid overnight times for non-night shifts
        if not shift_cross_midnight and time_cross_midnight:
            raise ValidationError(
                "Selected shift does not allow overnight check-in / check-out times."
            )

    # --------------------------------------------------
    # SAVE OVERRIDE (ON-TIME + OVERTIME)
    # --------------------------------------------------
    def save(self, *args, **kwargs):
        # Calculate on-time before saving
        self.calculate_on_time_checkin()

        super().save(*args, **kwargs)

        # Lazy import to avoid circular dependency
        from overtime.models import Overtime

        if self.status == 'P' and self.shift:
            worked = self.worked_hours()
            shift_hours = self.shift.duration_hours()

            overtime_hours = round(worked - shift_hours, 2)

            if overtime_hours > 0:
                Overtime.objects.update_or_create(
                    attendance=self,
                    defaults={
                        'employee': self.employee,
                        'overtime_hours': overtime_hours,
                        'approval_status': 'P',  # Pending
                    }
                )
            else:
                Overtime.objects.filter(attendance=self).delete()
        else:
            Overtime.objects.filter(attendance=self).delete()
