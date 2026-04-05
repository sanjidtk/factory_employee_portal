import random
from datetime import datetime, date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from employees.models import Department, Designation, Employee
from shifts.models import Shift
from attendance.models import Attendance
from overtime.models import Overtime
from leave.models import LeaveType, LeaveBalance, LeaveApplication, LeaveAuditLog
from workassignment.models import ProductionLine, Workstation, WorkAssignment, ShiftRoster, RosterEntry

class Command(BaseCommand):
    help = 'Generates realistic mock data for all models.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Wipe all data before generating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("Clearing existing data...")
            models_to_clear = [
                RosterEntry, ShiftRoster, WorkAssignment, Workstation, ProductionLine,
                LeaveAuditLog, LeaveApplication, LeaveBalance, LeaveType,
                Overtime, Attendance, Shift, Employee, Designation, Department
            ]
            for model in models_to_clear:
                try:
                    model.objects.all().delete()
                except Exception:
                   self.stdout.write(f"  (Skipping {model.__name__} - table not found)")
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write("✓ Cleanup complete.")

        try:
            with transaction.atomic():
                self.generate_data()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during generation: {e}"))
            raise e

    def generate_data(self):
        # 1. Shifts
        shifts_data = [
            ('Morning', time(6, 0), time(14, 0)),
            ('Evening', time(14, 0), time(22, 0)),
            ('Night', time(22, 0), time(6, 0)),
        ]
        shifts = {}
        for name, start, end in shifts_data:
            s, _ = Shift.objects.get_or_create(name=name, defaults={'start_time': start, 'end_time': end})
            shifts[name] = s
        self.stdout.write(f"✓ Created {len(shifts)} shifts")

        # 2. Departments & Designations
        dept_data = {
            'Production Line A': ['Line Operator', 'Senior Operator', 'Line Supervisor'],
            'Production Line B': ['Line Operator', 'Senior Operator', 'Line Supervisor'],
            'Warehouse': ['Store Keeper', 'Forklift Operator', 'Warehouse Supervisor'],
            'Quality Control': ['QC Inspector', 'QC Analyst'],
            'Maintenance': ['Technician', 'Senior Technician'],
        }
        departments = {}
        designations = {}
        for d_name, desigs in dept_data.items():
            dept, _ = Department.objects.get_or_create(name=d_name)
            departments[d_name] = dept
            for ds_name in desigs:
                desig, _ = Designation.objects.get_or_create(name=ds_name, department=dept)
                designations[f"{d_name}-{ds_name}"] = desig
        self.stdout.write(f"✓ Created departments and designations")

        # 3. Users & Employees
        password = 'Test@1234'
        sa_user, _ = User.objects.get_or_create(username='director', defaults={'email': 'director@factory.com', 'is_staff': True, 'is_superuser': True})
        sa_user.set_password(password)
        sa_user.save()
        sa_emp, _ = Employee.objects.get_or_create(emp_id='EMP001', defaults={'user': sa_user, 'first_name': 'Ahmed', 'last_name': 'Rashidi', 'role': 'superadmin', 'department': departments['Production Line A'], 'designation': designations['Production Line A-Line Supervisor'], 'date_joined': date.today() - timedelta(days=1000)})

        hr_user, _ = User.objects.get_or_create(username='hr.admin', defaults={'email': 'hr@factory.com', 'is_staff': True})
        hr_user.set_password(password)
        hr_user.save()
        hr_emp, _ = Employee.objects.get_or_create(emp_id='EMP002', defaults={'user': hr_user, 'first_name': 'Priya', 'last_name': 'Menon', 'role': 'admin', 'department': departments['Quality Control'], 'designation': designations['Quality Control-QC Analyst'], 'date_joined': date.today() - timedelta(days=800)})

        managers = []
        manager_info = [
            ('manager.line_a', 'Ravi', 'Kumar', 'Production Line A', 'Line Supervisor'),
            ('manager.line_b', 'Mohammed', 'Al Farsi', 'Production Line B', 'Line Supervisor'),
            ('manager.warehouse', 'Sarah', 'Thomas', 'Warehouse', 'Warehouse Supervisor'),
        ]
        for idx, (uname, fname, lname, dname, dsname) in enumerate(manager_info):
            m_user, _ = User.objects.get_or_create(username=uname, defaults={'email': f'{uname}@factory.com', 'is_staff': True})
            m_user.set_password(password)
            m_user.save()
            m_emp, _ = Employee.objects.get_or_create(emp_id=f'EMP00{3+idx}', defaults={'user': m_user, 'first_name': fname, 'last_name': lname, 'role': 'manager', 'department': departments[dname], 'designation': designations[f"{dname}-{dsname}"], 'date_joined': date.today() - timedelta(days=500), 'manager': hr_emp})
            managers.append(m_emp)

        employees = []
        for i in range(15):
            fname, lname = random.choice(['John', 'Maria', 'Senthil', 'Fatima', 'Rajesh']), random.choice(['Doe', 'Santos', 'Raman', 'Begum', 'Kapoor'])
            uname = f"emp.{fname.lower()}.{i}"
            e_user, _ = User.objects.get_or_create(username=uname, defaults={'email': f'{uname}@factory.com'})
            e_user.set_password(password)
            e_user.save()
            d_name = random.choice(list(dept_data.keys()))
            ds_name = random.choice(dept_data[d_name])
            e_emp, _ = Employee.objects.get_or_create(emp_id=f'EMP{100+i:03}', defaults={'user': e_user, 'first_name': fname, 'last_name': lname, 'role': 'employee', 'department': departments[d_name], 'designation': designations[f"{d_name}-{ds_name}"], 'date_joined': date.today() - timedelta(days=random.randint(30, 400)), 'manager': random.choice(managers)})
            employees.append(e_emp)
        all_staff = [sa_emp, hr_emp] + managers + employees
        self.stdout.write(f"✓ Created 20 employees")

        # 4. Leave Types & Applications
        l_types = {name: LeaveType.objects.get_or_create(name=name, defaults={'max_days_per_year': m_days, 'is_paid': paid, 'carry_forward': cf})[0] 
                   for name, m_days, paid, cf in [('Annual Leave', 15, True, True), ('Sick Leave', 10, True, False), ('Emergency Leave', 3, True, False)]}
        for emp in all_staff:
            for lt in l_types.values(): LeaveBalance.objects.get_or_create(employee=emp, leave_type=lt, year=date.today().year, defaults={'allocated_days': lt.max_days_per_year, 'used_days': 0})

        leave_apps = []
        for emp in employees[:5]:
            la = LeaveApplication.objects.create(employee=emp, leave_type=l_types['Annual Leave'], start_date=date.today()-timedelta(days=10), end_date=date.today()-timedelta(days=7), reason="Mock", status='Approved', approver=emp.manager)
            leave_apps.append(la)
        self.stdout.write(f"✓ Created Leave types and applications")

        # 5. Attendance & Overtime (BULK OPTIMIZED)
        self.stdout.write("Optimizing Attendance creation...")
        attendance_batch = []
        overtime_batch = []
        
        for emp in all_staff:
            for day_offset in range(30):
                target_date = date.today() - timedelta(days=day_offset)
                if target_date.weekday() == 4: continue # skip Fridays
                
                status_roll = random.random()
                if status_roll < 0.90: # Present or Late
                    shift = random.choice(list(shifts.values()))
                    is_late = random.random() < 0.1
                    ci_offset = random.randint(10, 40) if is_late else random.randint(-10, 5)
                    ci = (datetime.combine(target_date, shift.start_time) + timedelta(minutes=ci_offset)).time()
                    co = (datetime.combine(target_date, shift.end_time) + timedelta(minutes=random.randint(-5, 120))).time()
                    
                    att = Attendance(
                        employee=emp, date=target_date, shift=shift, status='Late' if is_late else 'Present',
                        check_in=ci, check_out=co, is_late=is_late, late_minutes=ci_offset if is_late else 0
                    )
                    attendance_batch.append(att)
                    
                    # Mock Overtime if they stayed late
                    if random.random() < 0.2:
                        overtime_batch.append(Overtime(employee=emp, date=target_date, hours=random.uniform(1, 3), reason="Extra help", status='Approved', attendance=None)) # Link after bulk

        Attendance.objects.bulk_create(attendance_batch, ignore_conflicts=True)
        # Note: Linking Overtime to Attendance in bulk is complex, so we create them separately for mock data purposes
        Overtime.objects.bulk_create(overtime_batch, ignore_conflicts=True)
        self.stdout.write(f"✓ Created {len(attendance_batch)} attendance and {len(overtime_batch)} overtime records")

        # 6. Production Lines & Workstations
        pl_a, _ = ProductionLine.objects.get_or_create(name='Line A', defaults={'location': 'Zone 1', 'supervisor': managers[0]})
        workstations = [Workstation.objects.get_or_create(name=f'Station {i}', production_line=pl_a, defaults={'capacity': 4})[0] for i in range(5)]
        
        wa_batch = []
        for emp in employees:
            for day_offset in range(-7, 8):
                wa_batch.append(WorkAssignment(employee=emp, date=date.today() + timedelta(days=day_offset), workstation=random.choice(workstations), shift=random.choice(list(shifts.values())), assigned_by=sa_user))
        WorkAssignment.objects.bulk_create(wa_batch, ignore_conflicts=True)
        self.stdout.write(f"✓ Created Work Assignments")

        self.stdout.write("\n" + "="*40 + "\n  MOCK DATA GENERATION COMPLETE\n" + "="*40)
