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
            RosterEntry.objects.all().delete()
            ShiftRoster.objects.all().delete()
            WorkAssignment.objects.all().delete()
            Workstation.objects.all().delete()
            ProductionLine.objects.all().delete()
            LeaveAuditLog.objects.all().delete()
            LeaveApplication.objects.all().delete()
            LeaveBalance.objects.all().delete()
            LeaveType.objects.all().delete()
            Overtime.objects.all().delete()
            Attendance.objects.all().delete()
            Shift.objects.all().delete()
            Employee.objects.all().delete()
            Designation.objects.all().delete()
            Department.objects.all().delete()
            # Delete non-superuser users except our current admin if needed
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write("✓ Data cleared.")

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
            s, created = Shift.objects.get_or_create(name=name, defaults={'start_time': start, 'end_time': end})
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
        total_desig = 0
        for d_name, desigs in dept_data.items():
            dept, _ = Department.objects.get_or_create(name=d_name)
            departments[d_name] = dept
            for ds_name in desigs:
                desig, _ = Designation.objects.get_or_create(name=ds_name, department=dept)
                designations[f"{d_name}-{ds_name}"] = desig
                total_desig += 1
        self.stdout.write(f"✓ Created {len(departments)} departments and {total_desig} designations")

        # 3. Users & Employees (Roles)
        password = 'Test@1234'
        
        # Superadmin
        sa_user, _ = User.objects.get_or_create(username='director', defaults={'email': 'director@factory.com', 'is_staff': True, 'is_superuser': True})
        sa_user.set_password(password)
        sa_user.save()
        sa_emp, _ = Employee.objects.get_or_create(
            emp_id='EMP001',
            defaults={
                'user': sa_user,
                'first_name': 'Ahmed',
                'last_name': 'Al Rashidi',
                'role': 'superadmin',
                'department': departments['Production Line A'],
                'designation': designations['Production Line A-Line Supervisor'],
                'date_joined': date.today() - timedelta(days=1000)
            }
        )

        # HR Admin
        hr_user, _ = User.objects.get_or_create(username='hr.admin', defaults={'email': 'hr@factory.com', 'is_staff': True})
        hr_user.set_password(password)
        hr_user.save()
        hr_emp, _ = Employee.objects.get_or_create(
            emp_id='EMP002',
            defaults={
                'user': hr_user,
                'first_name': 'Priya',
                'last_name': 'Menon',
                'role': 'admin',
                'department': departments['Quality Control'],
                'designation': designations['Quality Control-QC Analyst'],
                'date_joined': date.today() - timedelta(days=800)
            }
        )

        # Managers
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
            m_emp, _ = Employee.objects.get_or_create(
                emp_id=f'EMP00{3+idx}',
                defaults={
                    'user': m_user,
                    'first_name': fname,
                    'last_name': lname,
                    'role': 'manager',
                    'department': departments[dname],
                    'designation': designations[f"{dname}-{dsname}"],
                    'date_joined': date.today() - timedelta(days=500),
                    'manager': hr_emp
                }
            )
            managers.append(m_emp)

        # 15 Employees
        first_names = ['John', 'Maria', 'Senthil', 'Fatima', 'Rajesh', 'Li', 'Arjun', 'Zaid', 'Dino', 'Ayesha', 'Pradeep', 'Grace', 'Omar', 'Kiran', 'Anita']
        last_names = ['Doe', 'Santos', 'Raman', 'Begum', 'Kapoor', 'Wei', 'Singh', 'Khan', 'Cruz', 'Jan', 'Menon', 'Lee', 'Bakir', 'Joshi', 'Das']
        
        employees = []
        for i in range(15):
            fname = first_names[i]
            lname = last_names[i]
            uname = f"emp.{fname.lower()}"
            e_user, _ = User.objects.get_or_create(username=uname, defaults={'email': f'{uname}@factory.com'})
            e_user.set_password(password)
            e_user.save()
            
            # Random dept / desig
            d_name = random.choice(list(dept_data.keys()))
            ds_name = random.choice(dept_data[d_name])
            
            e_emp, _ = Employee.objects.get_or_create(
                emp_id=f'EMP{100+i:03}',
                defaults={
                    'user': e_user,
                    'first_name': fname,
                    'last_name': lname,
                    'role': 'employee',
                    'department': departments[d_name],
                    'designation': designations[f"{d_name}-{ds_name}"],
                    'date_joined': date.today() - timedelta(days=random.randint(30, 400)),
                    'manager': random.choice(managers)
                }
            )
            employees.append(e_emp)
        
        all_staff = [sa_emp, hr_emp] + managers + employees
        self.stdout.write(f"✓ Created {len(all_staff)} employees (20 total)")

        # 4. Leave Types & Balances
        leave_configs = [
            ('Annual Leave', 15, True, True),
            ('Sick Leave', 10, True, False),
            ('Emergency Leave', 3, True, False),
            ('Unpaid Leave', 30, False, False),
            ('Maternity Leave', 45, True, False),
        ]
        l_types = {}
        for name, m_days, paid, cf in leave_configs:
            lt, _ = LeaveType.objects.get_or_create(name=name, defaults={'max_days_per_year': m_days, 'is_paid': paid, 'carry_forward': cf})
            l_types[name] = lt
            
        for emp in all_staff:
            for lt in l_types.values():
                used = 0
                if lt.name == 'Annual Leave': used = random.randint(0, 8)
                elif lt.name == 'Sick Leave': used = random.randint(0, 4)
                elif lt.name == 'Emergency Leave': used = random.randint(0, 2)
                elif lt.name == 'Maternity Leave' and emp.first_name in ['Maria', 'Fatima']: used = 45 # simulate
                
                LeaveBalance.objects.get_or_create(
                    employee=emp, leave_type=lt, year=date.today().year,
                    defaults={'allocated_days': lt.max_days_per_year, 'used_days': used}
                )
        self.stdout.write(f"✓ Created 5 leave types and balances for all employees")

        # 5. Leave Applications (12 records)
        leave_apps = []
        app_data = [
            (employees[0], 'Annual Leave', 'Approved', date.today() - timedelta(days=40), 5),
            (employees[1], 'Sick Leave', 'Approved', date.today() - timedelta(days=20), 2),
            (employees[2], 'Annual Leave', 'Approved', date.today() - timedelta(days=60), 3),
            (employees[3], 'Annual Leave', 'Approved', date.today() - timedelta(days=10), 4),
            (employees[4], 'Sick Leave', 'Pending', date.today() + timedelta(days=10), 1),
            (employees[5], 'Annual Leave', 'Pending', date.today() + timedelta(days=30), 10),
            (employees[6], 'Emergency Leave', 'Pending', date.today() + timedelta(days=5), 2),
            (employees[7], 'Annual Leave', 'Rejected', date.today() - timedelta(days=50), 3),
            (employees[8], 'Sick Leave', 'Rejected', date.today() - timedelta(days=70), 1),
            (employees[9], 'Annual Leave', 'Cancelled', date.today() - timedelta(days=80), 2),
            (employees[10], 'Annual Leave', 'Cancelled', date.today() - timedelta(days=90), 2),
            (employees[11], 'Annual Leave', 'Approved', date.today() - timedelta(days=2), 5), # current
        ]
        for emp, lt_name, status, s_date, dur in app_data:
            e_date = s_date + timedelta(days=dur-1)
            la = LeaveApplication.objects.create(
                employee=emp, leave_type=l_types[lt_name],
                start_date=s_date, end_date=e_date,
                reason="Mock reason", status=status,
                approver=emp.manager
            )
            if status in ['Approved', 'Rejected']:
                la.reviewed_by = sa_user
                la.reviewed_at = timezone.now()
                if status == 'Rejected': la.rejection_reason = "Mock rejection"
                la.save()
                LeaveAuditLog.objects.create(leave_application=la, action=status, performed_by=sa_user, note="Automated sync")
            leave_apps.append(la)
        self.stdout.write(f"✓ Created 12 leave applications")

        # 6. Attendance & Overtime (Last 30 days)
        att_count = 0
        for emp in all_staff:
            for day_offset in range(30):
                target_date = date.today() - timedelta(days=day_offset)
                if target_date.weekday() == 4: continue # skip Fridays
                
                # Check if on leave
                on_leave = LeaveApplication.objects.filter(employee=emp, status='Approved', start_date__lte=target_date, end_date__gte=target_date).exists()
                
                status_roll = random.random()
                if on_leave:
                    Attendance.objects.get_or_create(employee=emp, date=target_date, defaults={'status': 'On Leave'})
                elif status_roll < 0.85: # Present
                    shift = random.choice(list(shifts.values()))
                    ci = (datetime.combine(target_date, shift.start_time) + timedelta(minutes=random.randint(-10, 5))).time()
                    co = (datetime.combine(target_date, shift.end_time) + timedelta(minutes=random.randint(-15, 15))).time()
                    Attendance.objects.get_or_create(
                        employee=emp, date=target_date, 
                        defaults={'status': 'Present', 'shift': shift, 'check_in': ci, 'check_out': co}
                    )
                elif status_roll < 0.93: # Late
                    shift = random.choice(list(shifts.values()))
                    ci = (datetime.combine(target_date, shift.start_time) + timedelta(minutes=random.randint(10, 45))).time()
                    co = (datetime.combine(target_date, shift.end_time) + timedelta(minutes=random.randint(-15, 15))).time()
                    Attendance.objects.get_or_create(
                        employee=emp, date=target_date, 
                        defaults={'status': 'Late', 'shift': shift, 'check_in': ci, 'check_out': co}
                    )
                else: # Absent
                    Attendance.objects.get_or_create(employee=emp, date=target_date, defaults={'status': 'Absent'})
                att_count += 1
        self.stdout.write(f"✓ Created ~{att_count} attendance records")

        # Overtime (8 records)
        ot_reasons = ["Production deadline", "Machine breakdown coverage", "Inventory count", "Client order rush"]
        ot_present_atts = Attendance.objects.filter(status__in=['Present', 'Late']).order_by('?')[:8]
        for att in ot_present_atts:
            Overtime.objects.update_or_create(
                attendance=att,
                defaults={
                    'employee': att.employee,
                    'date': att.date,
                    'hours': random.uniform(1.5, 4.0),
                    'reason': random.choice(ot_reasons),
                    'status': random.choice(['Pending', 'Approved', 'Rejected']) if random.random() > 0.4 else 'Approved'
                }
            )
        self.stdout.write(f"✓ Created 8 overtime records")

        # 7. Production Lines & Workstations
        pl_a, _ = ProductionLine.objects.get_or_create(name='Production Line A', defaults={'location': 'Zone 1', 'supervisor': managers[0]})
        pl_b, _ = ProductionLine.objects.get_or_create(name='Production Line B', defaults={'location': 'Zone 2', 'supervisor': managers[1]})
        wh, _ = ProductionLine.objects.get_or_create(name='Warehouse', defaults={'location': 'Zone 3', 'supervisor': managers[2]})
        
        ws_data = [
            (pl_a, 'Assembly Station 1', 4), (pl_a, 'Assembly Station 2', 4), (pl_a, 'Packaging Unit 1', 3),
            (pl_b, 'Cutting Machine 1', 2), (pl_b, 'Welding Bay', 3), (pl_b, 'QC Inspection Desk', 2),
            (wh, 'Receiving Dock', 3), (wh, 'Dispatch Bay', 3),
        ]
        workstations = []
        for pl, name, cap in ws_data:
            ws, _ = Workstation.objects.get_or_create(name=name, production_line=pl, defaults={'capacity': cap})
            workstations.append(ws)
        self.stdout.write(f"✓ Created 3 production lines and {len(workstations)} workstations")

        # 8. Work Assignments (Last 7 + Next 7 days)
        wa_count = 0
        all_active_emps = [e for e in all_staff if e.is_active and e.role == 'employee']
        for emp in all_active_emps:
            # Match dept to production line
            target_pl = None
            if emp.department.name == 'Production Line A': target_pl = pl_a
            elif emp.department.name == 'Production Line B': target_pl = pl_b
            elif emp.department.name == 'Warehouse': target_pl = wh
            else: target_pl = random.choice([pl_a, pl_b, wh])
            
            my_ws_options = [ws for ws in workstations if ws.production_line == target_pl]
            
            for day_offset in range(-7, 8):
                target_date = date.today() + timedelta(days=day_offset)
                if target_date.weekday() == 4: continue
                
                WorkAssignment.objects.get_or_create(
                    employee=emp, date=target_date,
                    defaults={
                        'workstation': random.choice(my_ws_options),
                        'shift': random.choice(list(shifts.values())),
                        'assigned_by': sa_user
                    }
                )
                wa_count += 1
        self.stdout.write(f"✓ Created ~{wa_count} work assignments")

        # 9. Rosters (Current Week)
        week_start = date.today() - timedelta(days=date.today().weekday())
        rosters = []
        for pl in [pl_a, pl_b, wh]:
            ros, _ = ShiftRoster.objects.get_or_create(week_start=week_start, production_line=pl, defaults={'created_by': sa_user, 'is_published': True})
            rosters.append(ros)
            
            pl_emps = [e for e in all_active_emps if e.department.name == pl.name or (pl.name == 'Warehouse' and e.department.name == 'Warehouse')]
            if not pl_emps: pl_emps = all_active_emps[:5]
            
            ws_options = [ws for ws in workstations if ws.production_line == pl]
            
            for emp in pl_emps:
                for day_idx in range(6): # Mon-Sat
                    RosterEntry.objects.get_or_create(
                        roster=ros, employee=emp, day_of_week=day_idx,
                        defaults={
                            'workstation': random.choice(ws_options),
                            'shift': random.choice(list(shifts.values()))
                        }
                    )
        self.stdout.write(f"✓ Created 3 rosters and related entries")

        # FINAL SUMMARY
        self.stdout.write("\n" + "="*40)
        self.stdout.write("  MOCK DATA GENERATION COMPLETE")
        self.stdout.write("="*40)
        self.stdout.write(f"  Users created        : {User.objects.count()}")
        self.stdout.write(f"  Departments          : {Department.objects.count()}")
        self.stdout.write(f"  Designations         : {Designation.objects.count()}")
        self.stdout.write(f"  Employees            : {Employee.objects.count()}")
        self.stdout.write(f"  Attendance records   : {Attendance.objects.count()}")
        self.stdout.write(f"  Overtime records     : {Overtime.objects.count()}")
        self.stdout.write(f"  Leave Types          : {LeaveType.objects.count()}")
        self.stdout.write(f"  Leave Balances       : {LeaveBalance.objects.count()}")
        self.stdout.write(f"  Leave Applications   : {LeaveApplication.objects.count()}")
        self.stdout.write(f"  Work Assignments     : {WorkAssignment.objects.count()}")
        self.stdout.write(f"  Rosters              : {ShiftRoster.objects.count()}")
        self.stdout.write(f"  Roster Entries       : {RosterEntry.objects.count()}")
        self.stdout.write("="*40)
        self.stdout.write("\nLOGIN CREDENTIALS (all passwords: Test@1234)")
        self.stdout.write("  Director    : director")
        self.stdout.write("  HR Admin    : hr.admin")
        self.stdout.write(f"  Managers    : {' / '.join([m.username for m in User.objects.filter(employee__role='manager')])}")
        emp_list = [e.username for e in User.objects.filter(employee__role='employee')]
        self.stdout.write(f"  Employees   : {' / '.join(emp_list[:5])} ...")
        self.stdout.write("="*40)
