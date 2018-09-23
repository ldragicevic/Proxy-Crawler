import threading
import mysql.connector
from time import sleep
import constants as cn


class DbWorker(threading.Thread):

    def __init__(self, db_actions, host, user, passwd, database):
        super(DbWorker, self).__init__()
        self.db_actions = db_actions
        self.setDaemon(True)
        try:
            self.my_db = mysql.connector.connect(host=host, user=user, password=passwd, database=database)
        except Exception as e:
            print('> DB Worker could not connect to Database. {err_msg}'.format(err_msg=str(e)))

    def run(self):

        print("> DB Worker is active")

        while True:

            action = self.db_actions.get_next()
            if action is None:
                print("DB Worker sleeping no job found.")
                sleep(cn.DB_THREAD_NO_JOB_WAIT_SEC)
                continue

            db_table = action['db_table']
            db_cols = cn.SQL_INSERT_DESC[db_table]
            db_values = action['db_values']
            db_pk = db_cols.split(',')[0]

            if db_values is '':
                continue

            sql_query = cn.SQL_INSERT_TEMPLATE.format(db_table=db_table, db_cols=db_cols, db_values=db_values,
                                                      db_pk=db_pk)
            sql_query = sql_query.replace('None', 'NULL')

            try:
                cursor = self.my_db.cursor()
                cursor.execute(sql_query)
                self.my_db.commit()
            except Exception as e:
                print('$' * 50)
                print('$' * 50)
                print('db error: {error}'.format(error=str(e)))
                print('sql query: {query}'.format(query=sql_query))
                print('$' * 50)
                print('$' * 50)
