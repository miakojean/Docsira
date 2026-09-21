from django.contrib import admin
from .models import (CustomUser, Collaborator, CollaboratorInvitation, ActivationCode)

admin.site.register(CustomUser)
admin.site.register(Collaborator)
admin.site.register(CollaboratorInvitation)
admin.site.register(ActivationCode)
