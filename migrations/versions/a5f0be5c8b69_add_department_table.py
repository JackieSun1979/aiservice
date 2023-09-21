"""add department table

Revision ID: a5f0be5c8b69
Revises: 853f9b9cd3b6
Create Date: 2023-09-20 22:57:41.417610

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a5f0be5c8b69'
down_revision = '853f9b9cd3b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('departments',
    sa.Column('id', postgresql.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('code', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='department_pkey')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('departments')
    # ### end Alembic commands ###