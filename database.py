"""
Database Utility
"""

import psycopg2
from logger import get_logger

_LOG = get_logger("database")


class Db:
    """
    Mini wrapper for database interaction
    """

    def __init__(self):
        self._conn = None
        self._cursor = None

    def connect(self, url):
        """
        Establishes connection with psql server
        """
        self._conn = psycopg2.connect(url)
        self._cursor = self._conn.cursor()

    def select(self, query, data=None):
        """ execution suitable for read queries, returning the rows returned from given query.
        """
        _LOG.debug(f"exectuting:{query}")
        self._cursor.execute(query, data)
        return self._cursor.fetchall()

    def commit(self, query, data=None):
        """ execution suitable for update queries
        """
        _LOG.debug("exectuting:{query}")
        self._cursor.execute(query, data)
        self._conn.commit()

    def close(self):
        """Closes database connection
        """
        self._conn.close()

