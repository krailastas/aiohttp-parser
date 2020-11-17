import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'bcb6d1665182'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'task',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('company_name', sa.String(length=64), nullable=False),
        sa.Column('location', sa.String(length=64), nullable=True),
        sa.Column('status', sa.INTEGER(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=True
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'job',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('task_id', sa.INTEGER(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('desc', sa.Text(), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=False),
        sa.Column('score', sa.INTEGER(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=True
        ),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('job')
    op.drop_table('task')
