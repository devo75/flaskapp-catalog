import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
     __tablename__ = 'user'
     
     id = Column(Integer, primary_key=True)
     name = Column(String(250), nullable=False)
     email = Column(String(250), nullable=False)


class Campground(Base):
    __tablename__ = 'campground'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
        }

  

class SiteReview(Base):
    __tablename__ = 'site_review'

    experience = Column(String(200), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category = Column(String(250))
    campground_id = Column(Integer, ForeignKey('campground.id'))
    campground = relationship(Campground)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):

        return {
            'experience': self.experience,
            'id': self.id,
            'description': self.description,
            'category': self.category,
        }




engine = create_engine('sqlite:///campreviewwithusers.db')
Base.metadata.create_all(engine)