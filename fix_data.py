from db import Book
from sqlalchemy.orm import *
from sqlalchemy import create_engine, and_
from datetime import datetime
import os

connection_string = os.getenv("CONNECTION_STR")


def main():
    engine = create_engine(connection_string)
    i = 0
    session = Session(engine, autoflush=True)
    for e in session.query(Book).filter(and_(Book.publisher_name == None, Book.rank > 0)).with_for_update().all():

        if e.publisher:
            p = e.publisher.rfind("(")
            parts = [e.publisher[:p], e.publisher[p + 1:]]
            if len(parts) > 1:
                date_str = parts[1].strip()[:-1]
                try:
                    d = datetime.strptime(date_str, '%B %d, %Y')
                except:
                    try:
                        d = datetime.strptime(date_str, '%B %Y')
                    except:
                        try:
                            d = datetime.strptime(date_str, '%Y')
                        except:
                            d = None
                e.publish_date = d
                pub_name = parts[0].split(";")[0].strip()
                if len(pub_name) < 100:
                    e.publisher_name = pub_name

        if e.weight_str:
            parts = e.weight_str.split(" ")
            if len(parts) > 1:
                if parts[1] == "ounces":
                    e.weigth_grams = float(parts[0]) * 28.3495231
                elif parts[1] == "pounds":
                    e.weigth_grams = float(parts[0]) * 453.59237
                else:
                    raise Exception("unsupported weight {}".format(parts[1]))

        if e.dimensions_str:
            parts = e.dimensions_str.split(" ")
            if len(parts) > 5:
                a = float(parts[0])
                b = float(parts[2])
                c = float(parts[4])
                if parts[5] == "inches":
                    e.volume_cm3 = (a * 2.54) * (b * 2.54) * (c * 2.54)
                else:
                    raise Exception("unsupported length {}".format(parts[5]))

        session.add(e)
        session.commit()

        print("asin {} done i = {}".format(e.asin, i))
        i += 1

if __name__ == "__main__":
    main()


