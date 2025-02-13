from accounts.models import CustomUser


def user_context(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(id=request.user.id)
        user.initials = user.first_name[0] + user.last_name[0]
        return {"fullUser": user}
    else:
        return {"fullUser", None}
