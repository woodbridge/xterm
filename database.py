from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///database.db', echo=True)

Base = declarative_base()

class Person(Base):
  __tablename__ = 'people'
  __tableargs__ = {'extend_existing': True}

  id = Column(Integer, primary_key=True)
  name = Column(String)
  email = Column(String)
  stripe_charge_id = Column(String)
  amount = Column(Integer)

def init():
  Session = sessionmaker(bind=engine)
  Base.metadata.create_all(engine)
  return Session()


session = init()