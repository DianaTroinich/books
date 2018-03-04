from db import Book, Base
from sqlalchemy.orm import *
import csv
from sqlalchemy import create_engine
import os

connection_string = os.getenv("CONNECTION_STR")

def main():

    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    s = Session(engine, autoflush=True)

    with open("/root/book30-listing-train.csv") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        i = 0
        total = 0
        books_bulk = list()
        for row in reader:
            books_bulk.append(Book(
                asin=str(row[0]),
                title=str(row[3]),
                author=str(row[4]),
                category=str(row[6]),
                image_url=str(row[2]),
                filename=str(row[1])))
            i += 1
            total += 1
            if i % 1000 == 0:
                i = 0
                print("try save, total = ", total)
                s.bulk_save_objects(books_bulk)
                books_bulk.clear()
                print("saved, total = ", total)

    s.commit()

if __name__ == "__main__":
    main()

