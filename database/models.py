from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()



class Meme(Base):
    __tablename__ = 'meme'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    file_id = Column(String, unique=True)
    mime_type = Column(String)

    user_id = Column(String, ForeignKey('user.user_id'))

    is_private = Column(Boolean, default=False)

    user = relationship('User', back_populates='memes')

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True)
    is_admin = Column(Boolean)


    memes = relationship('Meme', back_populates='user')