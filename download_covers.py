import requests
import random
from lxml.html.soupparser import fromstring
import os
from db import Book
from sqlalchemy.orm import *
from sqlalchemy import create_engine, and_
import time
from urllib.request import urlretrieve
import os

connection_string = os.getenv("CONNECTION_STR")


def download_image(dest_folder, image_file, image_url):
    url = image_url
    dst = os.path.join(dest_folder, image_file)
    if not os.path.exists(dst):
        urlretrieve(url, dst)
        return True
    return False


def main():
    engine = create_engine(connection_string)

    asin = ""
    try:
        session = Session(engine, autoflush=True)
        for e in session.query(Book).filter(and_(Book.price == None, Book.rank == None)).all():
            t = 3 + random.uniform(1, 100) / 10
            try:
                if download_image("/root/covers", e.filename, e.image_url):
                    print("download done for file: {} url: {}".format(e.filename, e.image_url))
                    time.sleep(t)
                else:
                    print("skip file: {} url: {}".format(e.filename, e.image_url))

            except Exception as e:
                m = "error with asin {} error: {}".format(asin, e)
                print(m)

    except Exception as e:
        print("general exception {}".format(e))


if __name__ == "__main__":
    main()


