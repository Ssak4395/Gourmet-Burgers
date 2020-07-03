import re
import sqlite3


class Database():
    def __init__(self, db_file=None):
        # Load given database path, or use a default
        if db_file is None:
            db_file = "database.sqlite3"
        self._db_file = db_file

        # Connect to the database
        self._conn = sqlite3.connect(db_file, check_same_thread=False)

    @property
    def db_file(self):
        return self._db_file

    # Create SQL table
    def create_table(self, create_table_sql):
        create_table_sql = re.sub("\n|\s{2,}", "", create_table_sql)
        create_table_sql = re.sub(",(?=\S)", ", ", create_table_sql)

        c = self._conn.cursor()
        c.execute(create_table_sql)

    # SQL SELECT [0]
    def fetchOne(self, *args, **kwargs):
        c = self._conn.cursor()
        c.execute(*args)
        result = c.fetchone()
        return result

    # SQL SELECT
    def fetchAll(self, *args, **kwargs):
        c = self._conn.cursor()
        c.execute(*args)
        result = c.fetchall()
        return result

    # SQL INSERT
    def insert(self, *args, commit=True, **kwargs):
        c = self._conn.cursor()
        c.execute(*args)
        if commit:
            self._conn.commit()
        return c.lastrowid

    # SQL UPDATE
    def update(self, *args, commit=True, **kwargs):
        c = self._conn.cursor()
        c.execute(*args)
        if commit:
            self._conn.commit()
        return c.rowcount
