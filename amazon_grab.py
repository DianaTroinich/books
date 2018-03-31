import requests
import random
from lxml.html.soupparser import fromstring
import re

from db import Book
from sqlalchemy.orm import *
from sqlalchemy import create_engine, and_
import time
import os

connection_string = os.getenv("CONNECTION_STR")

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

        s = re.sub("[^0-9]", "", s)
        try:
             rank = int(s)
        except:
            rank = -1
        result["Amazon Best Sellers Rank"] = rank


    return result

class PageNotFound(Exception):
    pass


def get_body(asin):
    asin = asin.rjust(10, '0')
    c = """session-id=136-2411424-9493010; session-id-time=2082787201l; ubid-main=130-0160568-2012845; session-token="RWQNeXzMsYRhEyPWNMwwTNk7vngCu/c7qsAxfUPYsb24yHalzXbkalUzQ5EgEVCfv0f0fj2jw1zvKZtgj4Nub1BOxZparQAc19yJ5rPy4FzlUn1QmI9fOcJ3oImPweV1jEPy/pEFGu1favo6LhDPy2M0v0jRiAGCVLR33DhvWZ7LtU+6KT1RLiy2+X4Ru9IW2oHJ0VGOfSl1/r3QDWcN/Smlm35xeKUfPuXFuAhlPVZXrvavRNYmtWs3mbOR4ONqdfZzcJiD7ctFjVdIWCrHUQ=="; ca=ALEAAAAAAAACAgAAQAAAAAQ=; x-wl-uid=13JBzos9puvgl7rbyR0gaqyn4AYvo8acfecV8NtUF5JjYwwXraUtUSE/qf7sra40GTEbsLtvASI6mSnwDfcU7Z+EpnIkvi1i/e6kzu0Jeyf5kHuaXikjFY6Q1L0+pKfTw8P1PKc2U8BI=; x-main="Rp85ZqMOG76U?ONm4hpiB?9HIqYOc4yhIYPKBVhp8onmqXJEYTJCXe4WQYAJu0iZ"; at-main=Atza|IwEBIOyy5nnYXOdqbDEm5-FdYsLoR6pjDVv5CIPnABPwaei39KGZ6moy2wUUSUnkKyHGbeTAyvacHF0X6_QjyocoI-IbHjiYiFfqWDDIUADv4vKQSN0EfAuspWA36bPKRY8xFHJX28Zd966x1E5dh82ypPgiTJWNIdrYTGKvHUhTbF8VxYdnzy6HsqcuMtRP6RcXrGvQi6n8vUG1TTA24dTKuMehfWzJKab5x__t-YBQP-WMyX5agHuDY4mANzAzbAlEUMwrnEKfqjo0Lcu0hTIs8OqaVr8KNgyzX88ZhpSr6JrrgzYGeXOzSSL7_9qdtzlIUCZoXTR7shUvx2x01q-FMeR2hleM0_rpmhh1sgbsxJUwjeniqvEcnUavgiqfszZXvbf2absccQbuPmoM0kZzBSZ2; sst-main=Sst1|PQHEVpZwLQXW5MNHSloNn9RSCCvwodMM1xbM8bpX742m6WyGroOvUZqxgasgPIO2Q0k_OtWfTvst0xPK0w6hrFmcSCW2OgfAz6EdRbH-zdIHcPZkHtUVFiyQL23G3tYMPPZscdo0JOuUNqcr0ZfAgaeiZULbD7obKN2N9TKZHniyiHvT3dkZXWgTNKy87TXoMoHdNGLgSXrPdIUzMz8vL69rCUaxyyp1CfQkdt88Kv5etIWTcwkEEpp6pgSxTcctsXg9Xm9CYkD72ZumBXjqjswKZg; lc-main=en_US; aws-target-static-id=1513759389717-975619; aws-target-visitor-id=1513759389720-51633.22_1; aws-target-data=%7B%22support%22%3A%221%22%7D; s_fid=4809A978A9DF8EB0-0FED8EA2964F87B4; s_dslv=1521400188611; s_vn=1545295389795%26vn%3D6; s_nr=1521400188613-Repeat; regStatus=registered; aws-ubid-main=122-5418636-5677483; aws-business-metrics-last-visit=1518207231236; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A600619203979%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22vlad%22%2C%22keybase%22%3A%22HoNFuM1tU%2Br%2FEmZw1LWU%2F%2BYV3mv3LbkHdpIQBOutr4M%5Cu003d%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%7D; __utma=194891197.1306151603.1518210256.1518210256.1518210256.1; __utmz=194891197.1518210256.1.1.utmccn=(direct)|utmcsr=(direct)|utmcmd=(none); csm-hit=tb:DGY64EPT6FXC0G3W3XDE+s-7GP0JQAJWJ30NGHNRNBE|1521409324462&adb:adblk_yes"""
    headers = {
        "Accept": """text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8""",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Cookie": c,
        "DNT": "1",
        "Host": "www.amazon.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": r"Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0",
    }
    rsp = requests.get("https://www.amazon.com/dp/{}".format(asin), headers=headers)
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
            t = 1 + random.uniform(1, 10) / 10
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


def check_file():
    with open("../body4.html") as f:
        data = f.read()
        r = parse(data)
        print(r)

if __name__ == "__main__":
    main()


