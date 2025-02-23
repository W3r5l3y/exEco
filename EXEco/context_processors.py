from accounts.models import CustomUser


def user_context(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(id=request.user.id)
        return {
            "fullUser": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "initials": (user.first_name[:1] + user.last_name[:1]).upper(),
            }
        }
    return {}
