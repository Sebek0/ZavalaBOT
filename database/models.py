from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table

Base = declarative_base()


event_member = Table(
    "event_member",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("event.id"), primary_key=True),
    Column("right_id", Integer, ForeignKey("member.id"), primary_key=True),
)


class Event(Base):
    __tablename__ = 'event'
    
    id = Column(Integer, primary_key=True)
    interaction_id = Column(String)
    author_id = Column(String)
    name = Column(String)
    description = Column(String)
    event_type = Column(String)
    slots = Column(Integer)
    date = Column(Date)
    members = relationship(
        'Member', secondary=event_member, back_populates='events'
    )
    
    def __repr__(self):
        return "<Event(name='{}', event_type='{}', slots={}, date={}, members={}," \
            "author_id={}, event_id={}" \
                .format(self.name, self.event_type, self.slots, self.date,
                        self.members, self.interaction_id, self.author_id)


class Member(Base):
    __tablename__ = 'member'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    discord_id = Column(String)
    events = relationship(
        'Event', secondary=event_member, back_populates='members'
    )
    
    def __repr__(self):
        return "<Member(name={}, discord_id={}" \
            .format(self.name, self.discord_id)
            


