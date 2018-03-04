import requests
import random
from lxml.html.soupparser import fromstring

from db import Book
from sqlalchemy.orm import *
from sqlalchemy import create_engine, and_
import time
import os

connection_string = os.getenv("CONNECTION_STR")

# save done for asin 545700272
# save done for asin 553508784
# save done for asin 147514940
# save done for asin 1780548273
# se 2.8; in order to keep installing from binary please use "pip install psycopg2-binary" instead. For details see: <http://initd.org/psycopg/docs/install.html#binary-install-from-pypi>.
#   """)
# error with asin 1511917946 error: skipping asin 1511917946 because of status code 404
# error with asin B00ATC9HXK error: invalid literal for int() with base 10: '3760438 Paid in Kindle Store'
# error with asin 1516819985 error: skipping asin 1516819985 because of status code 404
# error with asin B00I5VB6C2 error: invalid literal for int() with base 10: '777678 Paid in Kindle Store'
# error with asin B0141831FW error: invalid literal for int() with base 10: ''
# error with asin B00GMR2FGC error: invalid literal for int() with base 10: '3269117 Paid in Kindle Store'
# error with asin B013PKHF9A error: invalid literal for int() with base 10: ''
# error with asin B00BQG7W8K error: invalid literal for int() with base 10: '1236075 Paid in Kindle Store'
# error with asin B00W0CCAMM error: invalid literal for int() with base 10: '1107846 Paid in Kindle Store'
# error with asin 1943849366 error: skipping asin 1943849366 because of status code 404
# error with asin 1517466466 error: skipping asin 1517466466 because of status code 404
# error with asin B00005RYZH error: invalid literal for int() with base 10: ''
# 1432799541

class PageNotFound(Exception):
    pass


def parse(body):
    result = dict()
    header_found = False
    ul_start = False
    parts = []
    buy_used_found = False
    lines = body.split("\n")
    for l in lines:
        if "More Buying Choices" in l or "Buy Used" in l or "Buy New" in l:
            buy_used_found = True

        if ">$" in l:
            if not buy_used_found:
                continue
            i1 = l.find(">$")
            i2 = l[i1 + 2:].find("<")
            price = l[i1 + 2: i1 + i2 + 1]
            price = price.replace(',', '')
            result["price"] = float(price)
            break

    for l in lines:
        if "Product details" in l:
            header_found = True
            ul_start = False
            continue
        if "<ul>" in l:
            ul_start = True

        if header_found and ul_start:
            parts.append(l.strip())
            if "</ul>" in l:
                break

    parts = [x for x in parts if x != '']
    s = "".join(parts)
    s = s.replace('<b>', '')
    s = s.replace('</b>', '')
    tree = fromstring(s)
    for e in tree.xpath("//ul/li/text()"):
        l = e.split(":")
        if len(l) == 2:
            result[l[0].strip()] = l[1].strip()

    if "Amazon Best Sellers Rank" in result:
        s = result["Amazon Best Sellers Rank"]
        i1 = s.find("#")
        i2 = s.find("in Books")
        s = s[i1 + 1: i2 - 1].replace(",", "")
        result["Amazon Best Sellers Rank"] = int(s)

    return result


def get_body(asin):
    asin = asin.rjust(10, '0')
    rsp = requests.get("https://www.amazon.com/dp/{}".format(asin))
    if rsp.status_code != 200:
        m = "skipping asin {} because of status code {}".format(asin, rsp.status_code)
        if rsp.status_code != 404:
            raise PageNotFound(m)
        raise Exception(m)
    return rsp.text


def main():
    engine = create_engine(connection_string)

    asin = ""
    try:
        session = Session(engine, autoflush=True)
        for e in session.query(Book).filter(and_(Book.price == None, Book.rank == None)).with_for_update().all():
            t = random.uniform(1, 100) / 10
            time.sleep(t)
            asin = e.asin
            try:
                fields = parse(get_body(asin))

                if "Language" in fields:
                    e.language = fields["Language"]
                if "ISBN-13" in fields:
                    e.isbn_13 = fields["ISBN-13"]
                if "ISBN-10" in fields:
                    e.isbn_10 = fields["ISBN-10"]
                if "Publisher" in fields:
                    e.publisher = fields["Publisher"]
                if "Shipping Weight" in fields:
                    e.weight_str = fields["Shipping Weight"]
                if "Product Dimensions" in fields:
                    e.dimensions_str = fields["Product Dimensions"]
                if "Amazon Best Sellers Rank" in fields:
                    e.rank = fields["Amazon Best Sellers Rank"]
                if "price" in fields:
                    e.price = fields["price"]

                if "price" not in fields and "Amazon Best Sellers Rank" not in fields:
                    print("trash asin {} because of price and rank".format(asin))
                    e.rank = -1
                    # continue

                session.add(e)
                session.commit()
                print("save done for asin {} after sleep {}".format(asin, t))

            except PageNotFound as e:
                m = "asin {} not found, error: {}".format(asin, e)
                print(m)
                e.rank = -1
                session.add(e)
                session.commit()
            except Exception as e:
                m = "error with asin {} error: {}".format(asin, e)
                print(m)

    except Exception as e:
        print("general exception {}".format(e))
    #https://www.amazon.com/dp/3800732424
    #https: // www.amazon.com / OPC - englischsprachige - Ausgabe / dp / 3800732424 / ref = sr_1_1?ie = UTF8 & qid = 1519414377 & sr = 8 - 1 & keywords = 9783800732425

    # 3800732424

if __name__ == "__main__":
    main()


