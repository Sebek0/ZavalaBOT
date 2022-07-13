from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table

Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String)
    author_id = Column(String)
    event_id = Column(String)
    name = Column(String)
    description = Column(String)
    event_type = Column(String)
    slots = Column(Integer)
    date = Column(Date)
    members = Column(String)
    
    
    def __repr__(self):
        return "<Event(name='{}', event_type='{}', slots={}, date={}, members={}, message_id={}," \
            "author_id={}, event_id={}" \
                .format(self.name, self.event_type, self.slots, self.date,
                        self.members, self.message_id, self.author_id, self.event_id)
                    
            


