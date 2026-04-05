from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser or (hasattr(request.user, 'employee') and request.user.employee.role == 'admin'):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

class ManagerRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser or (hasattr(request.user, 'employee') and request.user.employee.role in ['admin', 'manager']):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

class EmployeeRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser or hasattr(request.user, 'employee'):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied
