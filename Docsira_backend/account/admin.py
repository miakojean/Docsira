from django.contrib import admin
from .models import (CustomUser, Collaborator, ActivationCode)

admin.site.register(CustomUser)
admin.site.register(Collaborator)
admin.site.register(ActivationCode)
