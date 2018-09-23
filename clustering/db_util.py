import sys

sys.path.append('../')

import constants as cn
from mysql import connector


class DbUtil:

    def __init__(self, ):
        try:
            self.my_db = connector.connect(host=cn.DB_HOST, user=cn.DB_USER, passwd=cn.DB_PASS, database=cn.DB_DATABASE)
        except Exception as e:
            print('> KMeans/DbUtil: database connection fail: {err_msg}'.format(err_msg=str(e)))

    def execute(self, query):
        cursor = self.my_db.cursor()
        cursor.execute(query)
        result = list(map(lambda x: x[0], cursor.fetchall()))
        return result
