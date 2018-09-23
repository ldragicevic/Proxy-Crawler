import sys

sys.path.append('../')

from worker import Worker
from db_worker import DbWorker
from actions import ActionQueue
from helper.proxy_helper import ProxyHelper, PROXY_LIST
import constants as cn


def main():
    actions = ActionQueue()
    db_actions = ActionQueue()
    request_helper = ProxyHelper(PROXY_LIST)

    actions.put({
        'url': cn.CRAWL_START_URL,
        'action': cn.TYPE_LISTING
    })

    mask = request_helper.get(hide=False)
    worker = Worker(actions, db_actions, mask)
    worker.start()

    for i in range(cn.PROXY_THREADS_COUNT):
        mask = request_helper.get(hide=True)
        worker = Worker(actions, db_actions, mask)
        worker.start()

    for i in range(cn.DB_THREADS_COUNT):
        db_worker = DbWorker(db_actions, cn.DB_HOST, cn.DB_USER, cn.DB_PASS, cn.DB_DATABASE)
        db_worker.start()

    while True:
        continue


if __name__ == "__main__":
    main()
