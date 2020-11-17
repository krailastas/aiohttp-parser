from sqlalchemy import Column, DateTime, String

from db.compat import utcnow
from models import Base


class AuthToken(Base):
    __tablename__ = 'authtoken'

    key = Column(String(40), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=utcnow())
