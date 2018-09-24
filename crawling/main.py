import constants as cn

from helper.scraper_helper import ScraperHelper
from helper.action_helper import ActionQueue
from helper.proxy_helper import ProxyHelper, PROXY_LIST

from thread.worker import Worker
from thread.db_worker import DbWorker


def main():
    action_queue = ActionQueue()
    db_queue = ActionQueue()
    proxy = ProxyHelper(PROXY_LIST)
    scraper = ScraperHelper(action_queue, db_queue)

    action_queue.put({'url': cn.CRAWL_START_URL, 'action': cn.TYPE_LISTING})

    mask = proxy.get(hide=False)
    worker = Worker(action_queue, mask, scraper)
    worker.start()

    for i in range(cn.PROXY_THREADS_COUNT):
        mask = proxy.get(hide=True)
        worker = Worker(action_queue, mask, scraper)
        worker.start()

    for i in range(cn.DB_THREADS_COUNT):
        db_worker = DbWorker(db_queue, cn.DB_HOST, cn.DB_USER, cn.DB_PASS, cn.DB_DATABASE)
        db_worker.start()

    while True:
        continue


if __name__ == "__main__":
    main()
