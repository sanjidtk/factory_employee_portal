from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login

def admin_required(function=None, redirect_field_name='next', login_url='login'):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), login_url, redirect_field_name)
            if request.user.is_superuser or (hasattr(request.user, 'employee') and request.user.employee.role == 'admin'):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator

def manager_required(function=None, redirect_field_name='next', login_url='login'):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), login_url, redirect_field_name)
            if request.user.is_superuser or (hasattr(request.user, 'employee') and request.user.employee.role in ['admin', 'manager']):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator

def employee_required(function=None, redirect_field_name='next', login_url='login'):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), login_url, redirect_field_name)
            if request.user.is_superuser or hasattr(request.user, 'employee'):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator
