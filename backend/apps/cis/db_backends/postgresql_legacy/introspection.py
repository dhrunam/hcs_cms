from django.db.backends.postgresql.introspection import (
    DatabaseIntrospection as PostgreSQLDatabaseIntrospection,
    FieldInfo,
    TableInfo,
)


class DatabaseIntrospection(PostgreSQLDatabaseIntrospection):
    """PostgreSQL 9.2 compatible introspection used only for CIS legacy DB."""

    def get_table_list(self, cursor):
        cursor.execute(
            """
            SELECT c.relname,
                   CASE
                       WHEN c.relkind IN ('v', 'm') THEN 'v'
                       ELSE 't'
                   END,
                   obj_description(c.oid, 'pg_class')
            FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind IN ('r', 'v', 'm', 'f')
              AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
              AND pg_catalog.pg_table_is_visible(c.oid)
            """
        )
        return [TableInfo(*row) for row in cursor.fetchall()]


    def get_table_description(self, cursor, table_name):
        """Return table description compatible with PostgreSQL 9.2."""

        cursor.execute(
            """
            SELECT
                a.attname AS column_name,
                NOT (a.attnotnull OR (t.typtype = 'd' AND t.typnotnull)) AS is_nullable,
                pg_get_expr(ad.adbin, ad.adrelid) AS column_default,
                CASE WHEN co.collname = 'default' THEN NULL ELSE co.collname END AS collation,
                FALSE AS is_autofield,
                col_description(a.attrelid, a.attnum) AS column_comment
            FROM pg_attribute a
            LEFT JOIN pg_attrdef ad ON a.attrelid = ad.adrelid AND a.attnum = ad.adnum
            LEFT JOIN pg_collation co ON a.attcollation = co.oid
            JOIN pg_type t ON a.atttypid = t.oid
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relkind IN ('f', 'm', 'r', 'v')
              AND c.relname = %s
              AND a.attnum > 0
              AND NOT a.attisdropped
              AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
              AND pg_catalog.pg_table_is_visible(c.oid)
            ORDER BY a.attnum
            """,
            [table_name],
        )
        field_map = {line[0]: line[1:] for line in cursor.fetchall()}

        cursor.execute(
            "SELECT * FROM %s LIMIT 1" % self.connection.ops.quote_name(table_name)
        )
        return [
            FieldInfo(
                line.name,
                line.type_code,
                line.internal_size if line.display_size is None else line.display_size,
                line.internal_size,
                line.precision,
                line.scale,
                *field_map[line.name],
            )
            for line in cursor.description
        ]

    def get_constraints(self, cursor, table_name):
        """Fallback constraint introspection compatible with PostgreSQL 9.2."""

        constraints = {}

        cursor.execute(
            """
            SELECT
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                kcu.ordinal_position
            FROM information_schema.table_constraints tc
            LEFT JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
             AND tc.table_name = kcu.table_name
            WHERE tc.table_name = %s
              AND tc.table_schema = current_schema()
            ORDER BY tc.constraint_name, kcu.ordinal_position
            """,
            [table_name],
        )

        for name, constraint_type, column_name, _ in cursor.fetchall():
            data = constraints.setdefault(
                name,
                {
                    "columns": [],
                    "primary_key": constraint_type == "PRIMARY KEY",
                    "unique": constraint_type in ("PRIMARY KEY", "UNIQUE"),
                    "foreign_key": None,
                    "check": constraint_type == "CHECK",
                    "index": False,
                    "definition": None,
                    "options": None,
                },
            )
            if column_name:
                data["columns"].append(column_name)

        cursor.execute(
            """
            SELECT
                tc.constraint_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
             AND tc.table_schema = ccu.table_schema
            WHERE tc.table_name = %s
              AND tc.table_schema = current_schema()
              AND tc.constraint_type = 'FOREIGN KEY'
            """,
            [table_name],
        )

        for name, foreign_table, foreign_column in cursor.fetchall():
            if name in constraints:
                constraints[name]["foreign_key"] = (foreign_table, foreign_column)

        return constraints
