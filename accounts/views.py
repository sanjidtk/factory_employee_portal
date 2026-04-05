from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'employee'):
            role = user.employee.role
            if role == 'admin':
                return '/dashboard/'
            elif role == 'manager':
                return '/manager/dashboard/'
            else:
                return '/employee/dashboard/'
        return '/dashboard/'

def custom_logout(request):
    logout(request)
    return redirect('login')
