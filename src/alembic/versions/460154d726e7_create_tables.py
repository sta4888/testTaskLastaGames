"""create tables

Revision ID: 460154d726e7
Revises: 
Create Date: 2025-04-16 12:02:58.085098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '460154d726e7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('processed_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.String(), nullable=True),
    sa.Column('result', sa.JSON(), nullable=True),
    sa.Column('error', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('file_path', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processed_files_file_id'), 'processed_files', ['file_id'], unique=True)
    op.create_index(op.f('ix_processed_files_id'), 'processed_files', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_processed_files_id'), table_name='processed_files')
    op.drop_index(op.f('ix_processed_files_file_id'), table_name='processed_files')
    op.drop_table('processed_files')
    # ### end Alembic commands ###
