from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config


DEFAULT_DB_ALIAS = 'default'

engine = create_engine(
    config.DATABASE[DEFAULT_DB_ALIAS], pool_recycle=60 * 15
)
session_factory = sessionmaker(bind=engine)
