"""
Connector class to faciliate mysql interactions
"""
import MySQLdb


class MysqlConnector:
    """
    connector to mysql
    """

    def __init__(self, host, user, passwd, db, port=3306):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.port = port
        self.connection = None
        self.connect()

    def connect(self):
        """
        connect to mysql
        """
        try:
            self.connection = MySQLdb.connect(host=self.host,
                                              user=self.user,
                                              passwd=self.passwd,
                                              db=self.db,
                                              port=self.port)
            self.connection.autocommit(False)
        except Exception, err:
            raise

    def query(self, query, params=()):
        """
        query mysql (no transaction)
            embedded single retry logic
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute(query, params)
            rows = cursor.fetchall()
        except MySQLdb.Error, err:
            # reconnect and query again before giving up
            try:
                self.connect()
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
            except Exception, err:
                raise
        cursor.close()
        return rows

    def trans_query(self, query, params=()):
        """
        transaction mysql query
            embedded single retry logic
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            rows = cursor.fetchall()
        except MySQLdb.Error, err:
            self.connection.rollback()
            # reconnect and query again before giving up
            try:
                self.connect()
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                self.connection.commit()
                rows = cursor.fetchall()
            except Exception, err:
                self.connection.rollback()
                raise
        cursor.close()
        return rows
