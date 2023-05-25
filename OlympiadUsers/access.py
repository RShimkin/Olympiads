from django.contrib.auth.decorators import user_passes_test

def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) or u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups, login_url='403')

def has_groups(user, *group_names):
    if user.is_authenticated:
        if bool(user.groups.filter(name__in=group_names)) or user.is_superuser:
                return True
    return False