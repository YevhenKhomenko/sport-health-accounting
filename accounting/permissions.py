# permissions.py
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles=None):
    """
    Декоратор для перевірки, чи роль поточного користувача входить до списку allowed_roles.
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Спочатку увійдіть у систему.")
                return redirect('login')
            user_profile = getattr(request.user, 'userprofile', None)
            user_role = getattr(user_profile, 'role', 'viewer')
            if user_role not in allowed_roles:
                messages.error(request, "У вас немає прав для виконання цієї дії.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
