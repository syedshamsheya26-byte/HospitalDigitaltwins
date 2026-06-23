from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not hasattr(request.user, 'userrole') or request.user.userrole.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def patient_session_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'patient_name' not in request.session:
            if request.user.is_authenticated:
                return redirect('accounts:login')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
