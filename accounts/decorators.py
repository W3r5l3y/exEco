from django.contrib.auth.decorators import user_passes_test


def is_gamekeeper(view_func=None, login_url="dashboard", redirect_field_name="next"):
    # Check if they are a staff member (gamekeeper), if not send them to the dashboard
    actual_decorator = user_passes_test(
        lambda u: u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
