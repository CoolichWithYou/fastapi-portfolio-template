"""

Revision ID: 7b7f20cf8099
Revises: bbc021b10509
Create Date: 2025-07-26 18:31:30.554092

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b7f20cf8099"
down_revision: Union[str, Sequence[str], None] = "bbc021b10509"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
               CREATE OR REPLACE FUNCTION data_raw_on_insert() RETURNS TRIGGER AS
               $$
               BEGIN
                   PERFORM (WITH payload("type", "id") AS (SELECT 'insert', NEW.id)
                            SELECT pg_notify('category', row_to_json(payload)::TEXT)
                            FROM payload);
                   RETURN NULL;
               END
               $$ LANGUAGE 'plpgsql';

               CREATE TRIGGER on_schedule_insert
                   AFTER INSERT
                   ON category
                   FOR EACH ROW
               EXECUTE PROCEDURE data_raw_on_insert();

               ALTER TABLE category
                   ENABLE ALWAYS TRIGGER on_schedule_insert;
               """
    )
    op.execute(
        """
               CREATE OR REPLACE FUNCTION data_raw_on_edit() RETURNS TRIGGER AS
               $$
               BEGIN
                   PERFORM (WITH payload("type", "id") AS (SELECT 'edit', NEW.id)
                            SELECT pg_notify('category', row_to_json(payload)::TEXT)
                            FROM payload);
                   RETURN NULL;
               END
               $$ LANGUAGE 'plpgsql';

               CREATE TRIGGER on_schedule_edit
                   after UPDATE
                   ON category
                   FOR EACH ROW
               EXECUTE PROCEDURE data_raw_on_edit();


               ALTER TABLE category
                   ENABLE ALWAYS TRIGGER on_schedule_edit;
               """
    )
    op.execute(
        """
               CREATE OR REPLACE FUNCTION data_raw_on_delete() RETURNS TRIGGER AS
               $$
               BEGIN
                   PERFORM (WITH payload("type", "id") AS (SELECT 'delete', old.id)
                            SELECT pg_notify('category', row_to_json(payload)::TEXT)
                            FROM payload);
                   RETURN NULL;
               END
               $$ LANGUAGE 'plpgsql';

               CREATE TRIGGER on_schedule_delete
                   AFTER DELETE
                   ON category
                   FOR EACH ROW
               EXECUTE PROCEDURE data_raw_on_delete();


               ALTER TABLE category
                   ENABLE ALWAYS TRIGGER on_schedule_delete;
               """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP TRIGGER IF EXISTS on_schedule_insert ON category;
        DROP TRIGGER IF EXISTS on_schedule_edit ON category;
        DROP TRIGGER IF EXISTS on_schedule_delete ON category;

        DROP FUNCTION IF EXISTS data_raw_on_insert();
        DROP FUNCTION IF EXISTS data_raw_on_edit();
        DROP FUNCTION IF EXISTS data_raw_on_delete();
    """
    )
