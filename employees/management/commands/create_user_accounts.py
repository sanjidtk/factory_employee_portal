import sys
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Employee, Department

class Command(BaseCommand):
    help = 'Create user accounts for employees and assign managers automatically'

    def handle(self, *args, **kwargs):
        # 1. Map manager for all departments
        departments = Department.objects.all()
        for dept in departments:
            if not dept.manager:
                manager_emp = Employee.objects.filter(department=dept, designation__icontains='manager').first()
                if not manager_emp:
                    manager_emp = Employee.objects.filter(department=dept).first()
                
                if manager_emp:
                    dept.manager = manager_emp
                    dept.save()
                    self.stdout.write(self.style.SUCCESS(f'Set {manager_emp} as manager for {dept.name}'))

        # 2. Assign accounts and map managers
        employees = Employee.objects.all()
        created_count = 0
        
        for emp in employees:
            if emp.department and emp.department.manager and emp != emp.department.manager:
                emp.manager = emp.department.manager
            
            # Map robust roles based on designation heuristics
            designation = emp.designation.lower() if emp.designation else ''
            if 'admin' in designation or 'hr' in designation or 'human resource' in designation:
                emp.role = 'admin'
            elif 'manager' in designation or 'lead' in designation or 'head' in designation:
                emp.role = 'manager'
            else:
                emp.role = 'employee'
                
            # Create User if not present
            if not emp.user:
                username = emp.employee_id
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.WARNING(f'User {username} already exists, skipping creation.'))
                else:
                    user = User.objects.create_user(
                        username=username,
                        password='factory@1234'
                    )
                    emp.user = user
                    created_count += 1
            
            emp.save()
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} user accounts and mapped managers.'))
