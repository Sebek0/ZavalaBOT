from ast import stmt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from db_config import create_database_uri
from models import Base, Event
from datetime import datetime
from contextlib import contextmanager

DATABASE_URI = create_database_uri()
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
def create_database():
    Base.metadata.create_all(engine)

def destroy_database():
    Base.metadata.drop_all(engine)
    
def create_new_event():
    pass

def delete_event():
    pass

def change_event():
    pass

def search_event(event_id):
    with session_scope() as s:
        stmt = select(Event).where(Event.event_id == str(event_id))
        result = s.execute(stmt)
        event = result.fetchone()
        print(event.Event.name)
        
    
def main():
    with session_scope() as s:
        create_database()
        event = Event(
            name='Vow of the Disciple',
            description='Szybki raid 3x',
            author_id='612124151241',
            event_type='PvE',
            slots=6,
            date=datetime(1998, 10, 12),
            members='sebek.#2136, Pycio#5123, Kriteros#1234',
            message_id='609120731893131',
            event_id='3512'
        )
        s.add(event)
        
if __name__ == '__main__':
    search_event(3512)
    