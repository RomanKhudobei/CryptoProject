import os
import sys

from sqlalchemy import Column, String, SmallInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

import datetime as dt

Base = declarative_base()

class Coin(Base):
	__tablename__ = 'coins'

	coin_id = Column(String(15), primary_key=True)
	entire_key = Column(String(255))
	valid = Column(String(1), default='X')

class IP(Base):
	__tablename__ = 'ips'

	ip = Column(String(15), primary_key=True)
	count = Column(SmallInteger, default=1)
	date_time = Column(DateTime, default=dt.datetime.now(), onupdate=dt.datetime.now())

engine = create_engine('mysql://root:1619982014automan@localhost:3306/coins?charset=utf8')

Base.metadata.create_all(engine)