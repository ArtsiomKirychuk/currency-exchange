"""add BYN currency

Revision ID: 46c801f514e9
Revises: 38158a655781
Create Date: 2026-11-08 11:24:21.942658

"""
from typing import Sequence, Union
from datetime import date

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46c801f514e9'
down_revision: Union[str, Sequence[str], None] = '38158a655781'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        sa.text("""
            INSERT INTO exchange_rates (
                currency_id,
                currency_code,
                date,
                currency_abbreviation,
                currency_scale,
                currency_name,
                currency_official_rate
            ) VALUES (
                1,
                933,
                :rate_date,
                'BYN',
                1,
                'Белорусский рубль',
                1.000000
            )
        """).bindparams(
            rate_date=date(2026, 11, 7)
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        sa.text("""
            DELETE FROM exchange_rates
            WHERE currency_code=933
        """)
    )
    pass
