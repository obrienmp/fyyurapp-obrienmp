"""Add Artist Website

Revision ID: ea162a0c3ce1
Revises: 8d66d0f6ea80
Create Date: 2020-05-02 00:59:39.577136

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea162a0c3ce1'
down_revision = '8d66d0f6ea80'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'website')
    # ### end Alembic commands ###
