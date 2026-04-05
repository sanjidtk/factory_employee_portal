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


class Designation(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations')

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    ROLE_CHOICES = [
        ('superadmin', 'Superadmin'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    
    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subordinates'
    )
    
    emp_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True
    )
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_hr(self):
        return self.role in ['admin', 'superadmin']

    def __str__(self):
        return f"{self.emp_id} - {self.full_name}"
