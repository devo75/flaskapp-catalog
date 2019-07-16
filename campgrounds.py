from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Campground, SiteReview, Base, User

engine = create_engine('sqlite:///campreviewwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Create a dummy user 
user1 =User(name="Bob Smith", email="bobby@gmail.com")

session.add(user1)
session.commit()

#Agate Beach Campground
campground1 = Campground(user_id=1, name ="Agate Beach")

session.add(campground1)
session.commit()

siteReview1 = SiteReview(user_id=1, experience="A beautiful place", description="Located inside the Naikoon National Park. With over 32 tent sites sitting right on the edge of the ocean",
                         category ='Will definitely come back', campground=campground1)
session.add(siteReview1)
session.commit()

siteReview2 = SiteReview(user_id=1, experience ="A great place to unwind", description="Beautiful spacious sites to pitch a tent or park your RV",
                         category="Will definitely come back", campground =campground1)
session.add(siteReview2)
session.commit()

#Bella Pacifica Campground
campground2 = Campground(user_id=1, name ="Bella Pacifica")
session.add(campground2)
session.commit()

siteReview1 =  SiteReview(user_id=1, experience = "A tenter's paradise", description= "The ultimate surf experience. Lush beaches and island lif ",
                         category = 'Will definitely come back', campground = campground2)
session.add(siteReview1)
session.commit()
                