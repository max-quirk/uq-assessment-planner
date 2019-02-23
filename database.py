"""
Database Utility
"""

import psycopg2
import os


class Db(object):
    """
    Mini wrapper for database interaction
    """

    def __init__(self, detailed):
        self._conn = None
        self._cursor = None
        self._detailed = detailed

    def connect(self, url):
        """ Establishes connection with psql server
        """
        print("connecting...")
        self._conn = psycopg2.connect(url)
        self._cursor = self._conn.cursor()
        print("connected:", self._conn, self._cursor)

    def select(self, query):
        """ execution suitable for read queries, returning the rows returned from given query.
        """
        self.log("Exectuting " + query)
        print(self._cursor)
        self._cursor.execute(query)
        return self._cursor.fetchall()

    def commit(self, query):
        """ execution suitable for update queries
        """
        self.log("Exectuting " + query)
        self._cursor.execute(query)
        self._conn.commit()

    def close(self):
        """Closes database connection
        """
        self._conn.close()

    def log(self, log):
        """stdout wrapper
        """
        if self._detailed:
            print(log)
