from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from shifts.models import Shift

class ProductionLine(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    supervisor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='supervised_lines')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Workstation(models.Model):
    name = models.CharField(max_length=100)
    production_line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, related_name='workstations')
    capacity = models.PositiveIntegerField(default=1)
    skills_required = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.production_line.name})"

class WorkAssignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_assignments')
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE, related_name='assignments')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee} - {self.workstation} on {self.date}"

class ShiftRoster(models.Model):
    week_start = models.DateField()
    production_line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, related_name='rosters')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"Roster {self.production_line.name} - Week {self.week_start}"

class RosterEntry(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    roster = models.ForeignKey(ShiftRoster, on_delete=models.CASCADE, related_name='entries')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)

    def __str__(self):
        return f"{self.employee} - {self.get_day_of_week_display()}"
