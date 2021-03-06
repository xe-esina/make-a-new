"""user info

Revision ID: 816b2853c2b0
Revises: 391f869eaeb2
Create Date: 2020-12-28 21:45:40.822622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '816b2853c2b0'
down_revision = '391f869eaeb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column('users', sa.Column('last_seen', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_seen')
    op.drop_column('users', 'about_me')
    # ### end Alembic commands ###
