import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '00ece4b7493d'
down_revision = 'bcb6d1665182'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'authtoken',
        sa.Column('key', sa.String(length=40), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=True
        ),
        sa.PrimaryKeyConstraint('key')
    )


def downgrade():
    op.drop_table('authtoken')
