from django.contrib.auth.decorators import user_passes_test

def is_gamekeeper(view_func=None, login_url='login', redirect_field_name='next'):
    """
    Decorator for views that checks that the user is a staff member,
    i.e., a gamekeeper, redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator