
from shelper import pgconnstring


from sqlalchemy import MetaData
from sqlalchemy import Column,String,Table
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#code start
#https://stackoverflow.com/questions/21770829/sqlalchemy-copy-schema-and-data-of-subquery-to-another-database
#connection strings for both remote and local
conn_string_remote = pgconnstring()
conn_string_local = 'sqlite:///ualocal.db'

#remote engine and session
remote_engine = create_engine(conn_string_remote)
remote_session = sessionmaker(remote_engine)

#local engine and session
local_engine = create_engine(conn_string_local)
local_session = sessionmaker(local_engine)

#define model to match database model
#https://stackoverflow.com/questions/39955521/sqlalchemy-existing-database-query
Base = declarative_base()
class UserAgent(Base):
    __tablename__ = 'user_agent_table'
    user_agent = Column(String, primary_key=True)
    browser_name = Column(String)
    browser_version = Column(String)
    os_name = Column(String)
    os_version = Column(String)
    device_name = Column(String)
    device_brand = Column(String)
    device_model = Column(String)
    remarks = Column(String)
    popularity = Column(String)

Base.metadata.create_all(remote_engine)
remotesession = remote_session()

#query the remote db to get the data
query = remotesession.query(UserAgent.user_agent)


#create local db
metadata = MetaData(bind=local_engine)
# columns = [Column(desc['name'],desc['type']) for desc in query.column_descriptions ]
columns = list()
for desc in query.column_descriptions:
    col_name = desc['name']
    col_type = desc['type']

    if col_name  == 'user_agent':
        columns.append(Column(col_name,col_type,primary_key=True))
    else:
        columns.append(Column(col_name,col_type))


table = Table('useragent',metadata,*columns)
table.create(local_engine,checkfirst=True)

#do the insertion
localsession = local_session()

for i,row in enumerate(query):
    localsession.execute(table.insert(values=row,prefixes=['OR IGNORE']))
    if i % 1000 == 0:
        localsession.flush()
localsession.commit()
