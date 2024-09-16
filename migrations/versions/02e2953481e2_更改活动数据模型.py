"""更改活动数据模型

Revision ID: 02e2953481e2
Revises: 39e549fddf38
Create Date: 2024-09-15 18:41:02.914228

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '02e2953481e2'
down_revision = '39e549fddf38'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('registration_review_required',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               existing_comment='报名是否需要审核')
        batch_op.alter_column('registration_required',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               existing_comment='活动是否需要报名')
        batch_op.alter_column('is_public',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               existing_comment='活动是否发布/公开')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('is_public',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               existing_comment='活动是否发布/公开')
        batch_op.alter_column('registration_required',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               existing_comment='活动是否需要报名')
        batch_op.alter_column('registration_review_required',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               existing_comment='报名是否需要审核')

    # ### end Alembic commands ###
