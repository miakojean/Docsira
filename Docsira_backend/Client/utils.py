from .models import CustomUser

def get_firm_users(user):

    if user.account_type == CustomUser.AccountType.COLLABORATOR:
        try:
            main_account = user.collaborator_profile.main_account
        except Exception:
            main_account = user
    else:
        main_account = user

    collaborators = CustomUser.objects.filter(collaborator_profile__main_account=main_account)
    return [main_account] + list(collaborators)