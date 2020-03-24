"""empty message

Revision ID: acb7e2d2001e
Revises: d7ad6c6dffab
Create Date: 2018-04-24 09:49:10.142687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acb7e2d2001e'
down_revision = 'd7ad6c6dffab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stories', sa.Column('author_id', sa.Integer(), nullable=True))
    op.add_column('stories', sa.Column('created_on', sa.DateTime(), nullable=False))
    op.add_column('stories', sa.Column('date_of_completion', sa.DateTime(), nullable=True))
    op.create_foreign_key(None, 'stories', 'users', ['author_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'stories', type_='foreignkey')
    op.drop_column('stories', 'date_of_completion')
    op.drop_column('stories', 'created_on')
    op.drop_column('stories', 'author_id')
    # ### end Alembic commands ###