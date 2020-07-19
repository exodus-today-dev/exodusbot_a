from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config

db = create_engine(config.DATABASE_URL)
base = declarative_base()
base.metadata.create_all(db)
Session = sessionmaker(db)
session = Session()
