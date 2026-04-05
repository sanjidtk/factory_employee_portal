from django import forms
from django.contrib.auth.models import User
from employees.models import Employee, Department

class AdminAddEmployeeForm(forms.Form):
    # User Details
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    
    # Employee Details
    employee_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emp ID (e.g. EMP-001)'}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    designation = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Designation'}))
    role = forms.ChoiceField(choices=Employee.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    manager = forms.ModelChoiceField(queryset=Employee.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    date_joined = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already taken.")
        return username

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("Employee ID already exists.")
        return employee_id

class AdminEditEmployeeForm(forms.Form):
    # User Details
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    # Employee Details
    employee_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    designation = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=Employee.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    manager = forms.ModelChoiceField(queryset=Employee.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    date_joined = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

