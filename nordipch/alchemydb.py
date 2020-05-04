
from sqlalchemy import MetaData
from sqlalchemy import Column,String
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#source engine, and source table
source_engine = create_engine()
