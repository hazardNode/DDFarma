# core/context_processors.py
def user_role(request):
    """Add user role to template context"""
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role:
        role = request.user.role.role_name
    else:
        role = 'UNAUTHENTICATED'

    return {
        'user_role': role
    }