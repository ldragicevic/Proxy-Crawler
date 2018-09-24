import requests
import random
import threading
import constants as cn

from time import sleep


class Worker(threading.Thread):
    _ID = 1

    def __init__(self, action_queue, mask, scraper):
        super(Worker, self).__init__()
        self.action_queue = action_queue
        self.mask = mask
        self.scraper = scraper
        self.id = Worker._ID
        Worker._ID += 1
        self.setDaemon(True)

    def run(self):

        print('Worker {tid} is active'.format(tid=self.id))
        action_data = self.action_queue.get_next()

        while True:

            sleep(random.uniform(cn.W_THREAD_SLEEP_BEGIN_SEC, cn.W_THREAD_SLEEP_END_SEC))

            while action_data is None:
                print("Worker {id} - no job available".format(id=self.id))
                sleep(cn.W_THREAD_NO_JOB_WAIT_SEC)
                action_data = self.action_queue.get_next()

            url = action_data['url']
            action = action_data['action']

            try:

                print('Worker {id} : [ {ip} ] : {url}'.format(id=self.id, url=url, ip=self.mask['ip']))
                r = requests.get(url=url, headers=self.mask['user-agent'], cookies=None, timeout=cn.REQ_TIMEOUT_SEC,
                                 proxies=self.mask['proxy'])

                # success
                if r.status_code == 200:
                    self.scraper.process(url, action, r)
                    action_data = self.action_queue.get_next()

                # too many requests
                elif r.status_code == 429:
                    print('Worker {id} - error 429 - slow down'.format(id=self.id))
                    sleep(cn.W_RESPONSE429_WAIT_SEC)

                # page not found
                elif r.status_code == 404:
                    print('Worker {id} - error 404 - could not process ({url})'.format(id=self.id, url=url))
                    action_data = self.action_queue.get_next()
                else:
                    pass

            except Exception as e:
                print('Worker {id} - fail - {err_code}.'.format(id=self.id, err_code=str(e)))
                action_data = self.action_queue.get_next()
                sleep(cn.W_RANDOM_EXCEPTION_WAIT_SEC)

            continue
