import sys

sys.path.append('../')

import matplotlib.pyplot as plt
import constants as cn

from mysql import connector
from db_queries import *

plot_sql_query = MASTER_GENRE_DISTRIBUTION_PERCENTAGE


def create_db_connector():
    return connector.connect(
        host=cn.DB_HOST,
        user=cn.DB_USER,
        passwd=cn.DB_PASS,
        database=cn.DB_DATABASE
    )


def main(query):
    try:
        my_db = create_db_connector()
        my_cursor = my_db.cursor()
        my_cursor.execute(query)
        result = my_cursor.fetchall()

        labels, values = zip(*result)

        fig = plt.figure()
        ax = fig.add_subplot(111)

        plt.plot(range(len(labels)), values, 'bo')
        plt.xticks(range(len(labels)), labels)

        for i, v in enumerate(values):
            ax.text(i, v + 10, "%.2f" % v)

        plt.show()

    except Exception as e:
        print('Error code: {err_code}'.format(err_code=str(e)))


if __name__ == "__main__":
    main(plot_sql_query)
