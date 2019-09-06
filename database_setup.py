#!/usr/bin/env python3
# Author: Luis Ruiz
# Project: Fitness Supplements App
# Date: 08/27/2019
# Description: Fitness Supplements Catalog Database
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
    picture = Column(String(250))

    # Add a property decorator to serialize information from this database
    @property
    def serialize(self):
        return {
                'name': self.name,
                'email': self.email,
                'picture': self.picture,
                'id': self.id
                }


class Supplement(Base):
    __tablename__ = 'supplement'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Add a property decorator to serialize information from this database
    @property
    def serialize(self):
        return {
                'name': self.name,
                'user_id': self.user_id,
                'id': self.id
                }


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(String(8))
    manufacturer = Column(String(250))
    supplement_id = Column(Integer, ForeignKey('supplement.id'))
    supplement = relationship(Supplement)
    videoURL = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Add a property decorator to serialize information from this database
    @property
    def serialize(self):
        return {
                'name': self.name,
                'description': self.description,
                'price': self.price,
                'manufacturer': self.manufacturer,
                'supplement_id': self.supplement_id,
                'videoURL': self.videoURL,
                'user_id': self.user_id,
                'id': self.id
                }


#engine = create_engine('sqlite:///FitnessSupplements.db')
engine = create_engine('postgresql://luisr:999999@localhost/fitnesssupplements')


Base.metadata.create_all(engine)
