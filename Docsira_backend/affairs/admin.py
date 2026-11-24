from django.contrib import admin
from .models import Affair, AffairComment, AffairShareLink, Document, DocumentShareLink

admin.site.register(Affair)
admin.site.register(Document)
admin.site.register(DocumentShareLink)
admin.site.register(AffairShareLink)
admin.site.register(AffairComment)