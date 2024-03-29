"""Add HowLongToBeat ID to Game model

Revision ID: 5519faf93ac6
Revises: c910d6963cf3
Create Date: 2022-09-21 12:24:27.511690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5519faf93ac6'
down_revision = 'c910d6963cf3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Game', sa.Column('hltb_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Game', 'hltb_id')
    # ### end Alembic commands ###
