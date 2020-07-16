
from shelper import pgconnstring
from sqlalchemy.sql.expression import func,select
from sqlalchemy import MetaData
from sqlalchemy import Column,String,Table
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from itertools import cycle

#code start
#https://stackoverflow.com/questions/21770829/sqlalchemy-copy-schema-and-data-of-subquery-to-another-database
#connection strings for both remote and local
conn_string_remote = pgconnstring()
conn_string_local = 'sqlite:///ualocal.db'


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

class UserAgentLocal(Base):
    __tablename__ ='useragent'
    user_agent = Column(String,primary_key = True)

def copy_remote_ua_to_local(os_list=None):

    if os_list is None:
        os_list = ['Linux','Windows','Android','OpenBSD','Mac OS X','macOS']



    #remote engine and session
    remote_engine = create_engine(conn_string_remote)
    remote_session = sessionmaker(remote_engine)

    #local engine and session
    local_engine = create_engine(conn_string_local)
    local_session = sessionmaker(local_engine)

    #create only one table
    table_objects = [Base.metadata.tables["user_agent_table"]]
    Base.metadata.create_all(remote_engine,tables=table_objects)
    remotesession = remote_session()

    #query the remote db to get the data
    query = remotesession.query(UserAgent.user_agent).filter(UserAgent.os_name.in_(os_list),
                                                            UserAgent.popularity.in_(['Very common','common','Common'])
                                                        )
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

    #dispose engines
    local_engine.dispose()
    remote_engine.dispose()



def return_one_random_ua():
    #local engine and session
    local_engine = create_engine(conn_string_local)
    local_session = sessionmaker(local_engine)

    #crate model
    table_objects = [Base.metadata.tables["useragent"]]
    Base.metadata.create_all(local_engine,tables=table_objects)

    #create local sessio
    localsession = local_session()
    query = localsession.query(UserAgentLocal.user_agent).order_by(func.random()).limit(1).all()

    localsession.close()
    local_engine.dispose()
    result = query[0]

    ua = list(result)[0]
    return ua

import random
def return_all_ua():
    #local engine and session

    local_engine = create_engine(conn_string_local)
    local_session = sessionmaker(local_engine)

    #crate model
    table_objects = [Base.metadata.tables["useragent"]]
    Base.metadata.create_all(local_engine,tables=table_objects)

    #create local sessio
    localsession = local_session()
    query = localsession.query(UserAgentLocal.user_agent).order_by(func.random()).all()

    localsession.close()
    local_engine.dispose()

    list_ua = [ua[0] for ua in list(query)]
    random.shuffle(list_ua)
    ua = cycle(list_ua)
    return ua




if __name__ == "__main__":
    copy_remote_ua_to_local()
    ad = return_all_ua()
    print(next(ad))
#now a function to query local db and return a random user_agent
