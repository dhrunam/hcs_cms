from django.db.backends.postgresql.base import DatabaseWrapper as PostgreSQLDatabaseWrapper

from .introspection import DatabaseIntrospection


class DatabaseWrapper(PostgreSQLDatabaseWrapper):
    """Legacy Postgres wrapper for read-only inspectdb against CIS 1.0."""

    introspection_class = DatabaseIntrospection

    def check_database_version_supported(self):
        # CIS 1.0 runs on PostgreSQL 9.2.x; allow connection for introspection.
        # Do not use this backend for normal app runtime or migrations.
        return
