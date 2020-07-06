"""Add played status

Revision ID: 92f7d0653a09
Revises: b1820e1947b5
Create Date: 2020-07-05 20:20:41.037167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92f7d0653a09'
down_revision = 'b1820e1947b5'
branch_labels = None
depends_on = None


table_name = 'Play'
column_name = 'status'
enum_name = 'status'
old_options = (
    'default',
    'interested',
    'playing',
    'placeholder',
    'completed',
    'hundred',
    'abandoned'
)
new_options = (
    'default',
    'interested',
    'playing',
    'played',
    'completed',
    'hundred',
    'abandoned'
)


# If you have data conversions that need to happen, you'll need something a
# little more complex in your upgrade and downgrade functions! Something like:

# table = sa.sql.table(table_name, sa.Column(column_name, sa.Enum(*old_options, name=enum_name), nullable=False))
# op.execute(table.update().where(getattr(table.c, column_name) == 'OLD_NAME').values(**{column_name: 'NEW_NAME'}))


def upgrade():
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            column_name,
            type_=sa.Enum(*new_options, name=enum_name),
            existing_type=sa.Enum(*old_options, name=enum_name)
        )


def downgrade():
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            column_name,
            type_=sa.Enum(*old_options, name=enum_name),
            existing_type=sa.Enum(*new_options, name=enum_name)
        )
