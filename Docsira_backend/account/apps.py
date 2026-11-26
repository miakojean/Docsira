from django.apps import AppConfig
from django.db.backends.signals import connection_created


def _configure_sqlite_pragmas(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA journal_mode=WAL;')
            cursor.execute('PRAGMA synchronous=NORMAL;')
            cursor.execute('PRAGMA busy_timeout=20000;')


class AccountConfig(AppConfig):
    name = 'account'

    def ready(self):
        connection_created.connect(_configure_sqlite_pragmas, dispatch_uid='docsira_sqlite_wal')
