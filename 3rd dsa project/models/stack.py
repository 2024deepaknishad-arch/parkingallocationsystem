# models/stack.py
class ActionStack:
    def __init__(self):
        self.s = []

    def push(self, action):
        self.s.append(action)

    def pop(self):
        return self.s.pop() if self.s else None

    def peek(self):
        return self.s[-1] if self.s else None

    def list_all(self):
        return list(self.s)

    def clear(self):
        self.s = []