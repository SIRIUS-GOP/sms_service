import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from users import *

engine = create_engine('sqlite:///db/users.db', echo=True)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

user = User(username="admin",password="admin")
session.add(user)

user = User(username="guest",password="guest")
session.add(user)

user = User(username="jump",password="python")
session.add(user)

# commit the record the database
session.commit()
