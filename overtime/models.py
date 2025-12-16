from django.db import models
from employees.models import Employee


class Overtime(models.Model):

    APPROVAL_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('H', 'On Hold'),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    attendance = models.OneToOneField(
        "attendance.Attendance",
        on_delete=models.CASCADE,
        related_name="overtime"
    )

    overtime_hours = models.FloatField(default=0.0)

    approval_status = models.CharField(
        max_length=1,
        choices=APPROVAL_CHOICES,
        default='P'
    )

    # ✅ ADD THIS (OPTIONAL)
    decision_reason = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.overtime_hours} hrs"
