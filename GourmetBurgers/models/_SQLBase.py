"""
SQLBase prototype to give subclasses scope to the database
"""

class SQLBase:
    _db = None
    _SQL = None