"""verification_configurations_table

Revision ID: 1330a916991a
Revises: 0035757c52c9
Create Date: 2023-01-05 20:07:33.163600

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1330a916991a'
down_revision = '0035757c52c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ver_conf_ver_configs',
    sa.Column('proof_request', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('ver_config_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('subject_identifier', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('ver_config_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ver_conf_ver_configs')
    # ### end Alembic commands ###
