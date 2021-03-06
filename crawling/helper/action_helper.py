import queue


class ActionQueue:

    def __init__(self):
        self.actions = queue.Queue()

    def get_next(self):
        try:
            return self.actions.get_nowait()
        except queue.Empty as e:
            return None

    def put(self, action):
        self.actions.put(action)
