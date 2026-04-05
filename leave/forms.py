from django import forms
from .models import LeaveApplication, LeaveBalance, LeaveType
from employees.models import Employee

class LeaveApplicationForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Employee"
    )
    leave_type = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Leave Type"
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Start Date"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="End Date"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Reason"
    )

    class Meta:
        model = LeaveApplication
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason']


class LeaveAllocationForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    leave_type = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    allocated_days = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = LeaveBalance
        fields = ['employee', 'leave_type', 'year', 'allocated_days']

class EmployeeLeaveApplicationForm(forms.ModelForm):
    leave_type = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Leave Type"
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Start Date"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="End Date"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Reason"
    )

    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
