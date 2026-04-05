from django.db import models
from employees.models import Employee


from django.contrib.auth.models import User

class Overtime(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    attendance = models.OneToOneField(
        "attendance.Attendance",
        on_delete=models.CASCADE,
        related_name="overtime_record"
    )
    date = models.DateField()
    hours = models.FloatField(default=0.0)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_overtimes'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    decision_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.hours} hrs on {self.date}"
