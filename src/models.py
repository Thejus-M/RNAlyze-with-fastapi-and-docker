from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


# The class "User" defines a database table with columns 
# for user ID, email, and hashed password.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    seqs = relationship("Sequences", back_populates="owner")


# This is a SQLAlchemy model class for a table called "Seqs" with columns for ID,
#  name, sequence,description, and owner ID, and a relationship to a User class.
class Sequences(Base):
    __tablename__ = "Seqs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    seq = Column(String, index=True, nullable=True)
    description = Column(String, index=True)
    result=Column(String,index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="seqs")