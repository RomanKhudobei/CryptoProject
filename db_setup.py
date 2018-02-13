import os
import sys

from sqlalchemy import Column, String, SmallInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

import datetime as dt

import config

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

engine = create_engine('mysql://{user}:{password}@{host}:{port}/crypto_project?charset=utf8'.format(user=config.USER,
																									password=config.PASSWORD,
																									host=config.HOST,
																									port=config.PORT))

Base.metadata.create_all(engine)