from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from employees.models import Employee

class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    max_days_per_year = models.IntegerField()
    is_paid = models.BooleanField(default=True)
    carry_forward = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.IntegerField()
    allocated_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    used_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ('employee', 'leave_type', 'year')

    @property
    def remaining_days(self):
        return self.allocated_days - self.used_days

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.year})"


class LeaveApplication(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date cannot be before start date.")

    def calculate_total_days(self):
        # Exclude Fridays
        if not self.start_date or not self.end_date:
            return 0
        days = 0
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.weekday() != 4:  # 4 is Friday in python date.weekday()
                days += 1
            current_date += timedelta(days=1)
        return Decimal(days)

    def save(self, *args, **kwargs):
        # Calculate total days before saving
        if not self.total_days or (not self.pk):
            self.total_days = self.calculate_total_days()

        is_new = self.pk is None
        old_instance = None
        if not is_new:
            old_instance = LeaveApplication.objects.get(pk=self.pk)

        super().save(*args, **kwargs)

        # Lazy imports for Attendance inside save to prevent cyclic importing
        from attendance.models import Attendance
        
        # Detect status change to Approved
        if is_new and self.status == 'Approved':
            self.approve_leave(Attendance)
        elif not is_new and old_instance.status != 'Approved' and self.status == 'Approved':
            self.approve_leave(Attendance)

    def approve_leave(self, Attendance):
        # Deduct balance
        balance, created = LeaveBalance.objects.get_or_create(
            employee=self.employee,
            leave_type=self.leave_type,
            year=self.start_date.year,
            defaults={'allocated_days': self.leave_type.max_days_per_year}
        )
        balance.used_days += self.total_days
        balance.save()

        # Update Attendance Records as 'L'
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.weekday() != 4:  # Don't update over weekend/Friday if usually off
                attendance, created_att = Attendance.objects.get_or_create(
                    employee=self.employee,
                    date=current_date,
                    defaults={'status': 'L'}
                )
                if not created_att:
                    attendance.status = 'L'
                    # Reset checkin times
                    attendance.check_in_time = None
                    attendance.check_out_time = None
                    attendance.save()
            current_date += timedelta(days=1)

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.status})"
