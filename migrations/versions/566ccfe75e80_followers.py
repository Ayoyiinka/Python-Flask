"""followers

Revision ID: 566ccfe75e80
Revises: 2cda21489fe8
Create Date: 2019-07-03 07:52:49.362346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '566ccfe75e80'
down_revision = '2cda21489fe8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('followers')
    # ### end Alembic commands ###
