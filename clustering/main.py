import sys

sys.path.append('../')

import sklearn as sk
import numpy as np
from db_util import DbUtil
from kmeans import KMeans
import constants as cn
from mysql import connector


def main():
    db_util = DbUtil()
    # k = input("KMeans K argument: ")
    # input_kind = input("KMeans cluster by: (1) year realised: ")

    print(db_util.execute("select  from artist limit 5"))


if __name__ == '__main__':
    main()
