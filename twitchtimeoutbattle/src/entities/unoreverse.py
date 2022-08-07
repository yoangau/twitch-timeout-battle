from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UnoReverse(Base):
    __tablename__ = 'unoreverse'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    user_name = Column(String)
    broadcaster_id = Column(String)
    count = Column(Integer)

    def __repr__(self):
        return "<UnoReverse(user_id='%s', user_name='%s', broadcaster_id='%s', nickname='%d')>" % (
            self.user_id, self.user_name, self.broadcaster_id, self.count)
