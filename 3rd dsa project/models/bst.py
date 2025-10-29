# models/bst.py
from dataclasses import dataclass
from typing import Optional, List
import time

@dataclass
class SlotNode:
    slot_no: int
    occupied: bool = False
    plate: str = ""            # license plate or identifier
    parked_at: float = 0.0     # timestamp
    left: Optional['SlotNode'] = None
    right: Optional['SlotNode'] = None

class SlotBST:
    def __init__(self):
        self.root = None

    def insert_node(self, slot_no):
        def _ins(node, val):
            if not node:
                return SlotNode(val)
            if val < node.slot_no:
                node.left = _ins(node.left, val)
            elif val > node.slot_no:
                node.right = _ins(node.right, val)
            return node
        self.root = _ins(self.root, slot_no)

    def in_order_slots(self) -> List[int]:
        out=[]
        def _in(node):
            if not node: return
            _in(node.left); out.append(node.slot_no); _in(node.right)
        _in(self.root); return out

    def find_nearest_free(self):
        # traverse in-order and return lowest-numbered free slot
        free = []
        def _in(node):
            if not node: return
            _in(node.left)
            if not node.occupied:
                free.append(node)
            _in(node.right)
        _in(self.root)
        return free[0] if free else None

    def search(self, slot_no):
        n = self.root
        while n:
            if slot_no == n.slot_no: return n
            n = n.left if slot_no < n.slot_no else n.right
        return None

    def ascii_repr(self):
        # Simple ASCII tree (compact)
        lines = []
        def _rec(node, prefix=""):
            if not node: return
            lines.append(f"{prefix}{node.slot_no}{' [X]' if node.occupied else ' [ ]'}")
            _rec(node.left, prefix + "  L-")
            _rec(node.right, prefix + "  R-")
        _rec(self.root)
        return "\n".join(lines)