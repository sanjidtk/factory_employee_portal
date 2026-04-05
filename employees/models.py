from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    ROLE_CHOICES = [
        ('admin', 'Admin / HR'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    
    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subordinates'
    )
    
    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True
    )
    designation = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField()

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_hr(self):
        return self.role == 'admin'

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"
