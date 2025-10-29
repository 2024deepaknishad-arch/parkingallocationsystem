# models/queue.py
class SimpleQueue:
    def __init__(self):
        self.q = []

    def enqueue(self, item):
        self.q.append(item)

    def dequeue(self):
        return self.q.pop(0) if self.q else None

    def peek_all(self):
        return list(self.q)

    def __len__(self):
        return len(self.q)