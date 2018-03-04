import os
import psycopg2
import sys
import pprint


connection_string = os.getenv("CONNECTION_STR")

query_1 = """SELECT *
FROM books
LIMIT 2"""


def get_func_1(conn):
    cursor = conn.cursor()
    cursor.execute(query_1)
    records = cursor.fetchall()
    pprint.pprint(records)


def main():
    conn = psycopg2.connect(connection_string)
    get_func_1(conn)


if __name__ == "__main__":
    main()

