"""create department table

Revision ID: 012d77d0a435
Revises: c89098b46e1b
Create Date: 2023-09-20 15:08:14.070501

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '012d77d0a435'
down_revision = 'c89098b46e1b'
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
    op.drop_table('department')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('department',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('code', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='department_pkey')
    )
    op.drop_table('departments')
    # ### end Alembic commands ###