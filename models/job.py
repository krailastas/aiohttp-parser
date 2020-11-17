from enum import Enum

from sqlalchemy import INT, Column, DateTime, ForeignKey, String, Text

from db.compat import utcnow
from models import Base


class TaskStatus(Enum):
    IN_PROGRESS = 1
    DONE = 2


class Task(Base):
    __tablename__ = 'task'

    id = Column(INT, primary_key=True)
    company_name = Column(String(64), nullable=False)
    location = Column(String(64))
    status = Column(INT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=utcnow())


class Job(Base):
    __tablename__ = 'job'

    id = Column(INT, primary_key=True)
    task_id = Column(INT, ForeignKey('task.id'), nullable=False)
    title = Column(Text, nullable=False)
    desc = Column(Text, nullable=False)
    url = Column(String(255), nullable=False)
    score = Column(INT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=utcnow())
