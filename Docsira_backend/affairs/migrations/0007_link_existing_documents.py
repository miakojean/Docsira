from django.db import migrations


def link_existing_documents(apps, schema_editor):
    """Relie les documents existants de chaque dossier dans l'ordre chronologique."""
    Document = apps.get_model('affairs', 'Document')

    previous_by_affair = {}
    for doc in Document.objects.order_by('uploaded_at'):
        previous = previous_by_affair.get(doc.affair_id)
        if previous is not None:
            doc.parent_id = previous.id
            doc.relation = 'ADDED'
            doc.save(update_fields=['parent', 'relation'])
        previous_by_affair[doc.affair_id] = doc


class Migration(migrations.Migration):

    dependencies = [
        ('affairs', '0006_document_evolution'),
    ]

    operations = [
        migrations.RunPython(link_existing_documents, migrations.RunPython.noop),
    ]
