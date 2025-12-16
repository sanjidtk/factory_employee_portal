from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Employee(models.Model):
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

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"
