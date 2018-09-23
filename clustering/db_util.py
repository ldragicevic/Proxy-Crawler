import sys

sys.path.append('../')

from mysql import connector


class DbUtil:

    def __init__(self, host, user, password, database):
        self.my_db = connector.connect(host=host, user=user, password=password, database=database)

    def execute(self, query):
        cursor = self.my_db.cursor()
        cursor.execute(query)

        result = []
        columns = [d[0] for d in cursor.description]

        for row in cursor.fetchall():
            result.append(dict(zip(columns, list(row))))

        return result
