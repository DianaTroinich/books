from sqlalchemy import Column, String, Integer, Sequence, Float
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

BOOKS_ID = Sequence('books_id_seq', start=1)


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, BOOKS_ID, primary_key=True, server_default=BOOKS_ID.next_value())
    asin = Column(String(10), index=True, unique=True)
    title = Column(String(500))
    author = Column(String(250))
    category = Column(String(250))
    filename = Column(String(100))
    image_url = Column(String(100))
    language = Column(String(100))
    isbn_10 = Column(String(20))
    isbn_13 = Column(String(20))
    rank = Column(Integer)
    publisher = Column(String(200))
    weight_str = Column(String(50))
    dimensions_str = Column(String(50))
    price = Column(Float)
