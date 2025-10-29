# routes/parking_routes.py
from flask import Blueprint, render_template, jsonify, request
from models.bst import SlotBST
from models.queue import SimpleQueue
from models.stack import ActionStack
import time, config
import requests
import os

parking_bp = Blueprint("parking", __name__, template_folder="../templates", static_folder="../static")

# In-memory structures (runtime only)
bst = SlotBST()
for i in range(1, config.TOTAL_SLOTS + 1):
    bst.insert_node(i)

wait_q = SimpleQueue()
undo_stack = ActionStack()
redo_stack = ActionStack()

def check_duplicate_plate(plate):
    """Check if plate already exists in parking or queue"""
    if not plate:
        return False
    # Check in BST
    def _check(node):
        if not node:
            return False
        if node.occupied and node.plate == plate:
            return True
        return _check(node.left) or _check(node.right)
    if _check(bst.root):
        return True
    # Check in queue
    return plate in wait_q.q

def allocate_slot(plate):
    node = bst.find_nearest_free()
    if node:
        node.occupied = True
        node.plate = plate
        node.parked_at = time.time()
        undo_stack.push(("park", node.slot_no, plate))
        redo_stack.clear()
        return node.slot_no
    else:
        wait_q.enqueue(plate)
        undo_stack.push(("enqueue", None, plate))
        redo_stack.clear()
        return None

def free_slot(slot_no):
    node = bst.search(slot_no)
    if node and node.occupied:
        plate = node.plate
        duration_minutes = max(1, int((time.time() - node.parked_at)//60))
        fee = duration_minutes * config.RATE_PER_MINUTE
        node.occupied = False; node.plate=""; node.parked_at=0
        undo_stack.push(("remove", slot_no, plate))
        redo_stack.clear()
        # allocate next in queue
        next_plate = wait_q.dequeue()
        assigned = None
        if next_plate:
            assigned = allocate_slot(next_plate)
        return {"freed": slot_no, "plate": plate, "duration_min": duration_minutes, "fee": fee, "assigned_next": assigned}
    return None

@parking_bp.route("/")
def index():
    return render_template("index.html")

@parking_bp.route("/park", methods=["POST"])
def park():
    data = request.json or {}
    plate = data.get("plate", "").strip()
    if not plate:
        plate = f"CAR{int(time.time())%10000}"
    
    # Check for duplicates
    if check_duplicate_plate(plate):
        return jsonify({"error": "duplicate", "message": f"Vehicle {plate} is already in the system"}), 400
    
    slot = allocate_slot(plate)
    return jsonify({"allocated_slot": slot, "queue_len": len(wait_q), "plate": plate})

@parking_bp.route("/remove", methods=["POST"])
def remove():
    data = request.json or {}
    slot_no = data.get("slot_no")
    if not slot_no:
        return jsonify({"error":"slot_no required"}),400
    res = free_slot(slot_no)
    if res:
        return jsonify(res)
    return jsonify({"error":"slot not occupied or not found"}),400

@parking_bp.route("/undo", methods=["POST"])
def undo():
    act = undo_stack.pop()
    if not act:
        return jsonify({"msg":"Nothing to undo"}),200
    typ, slot, plate = act
    if typ == "park":
        n = bst.search(slot)
        if n:
            # undo park => free slot and push to redo
            n.occupied=False; n.plate=""; n.parked_at=0
            redo_stack.push(act)
            return jsonify({"undone":"park","slot":slot})
    elif typ == "enqueue":
        # undo enqueue => remove from queue
        if plate in wait_q.q:
            wait_q.q.remove(plate)
            redo_stack.push(act)
            return jsonify({"undone":"enqueue","plate":plate})
    elif typ == "remove":
        # undo remove => re-park same plate into slot (if free)
        n = bst.search(slot)
        if n and not n.occupied:
            n.occupied=True; n.plate=plate; n.parked_at=time.time()
            redo_stack.push(act)
            return jsonify({"undone":"remove","slot":slot})
    return jsonify({"msg":"Could not undo action"}),400

@parking_bp.route("/redo", methods=["POST"])
def redo():
    act = redo_stack.pop()
    if not act:
        return jsonify({"msg":"Nothing to redo"}),200
    typ, slot, plate = act
    # reapply action
    if typ == "park":
        n = bst.search(slot)
        if n and not n.occupied:
            n.occupied=True; n.plate=plate; n.parked_at=time.time()
            undo_stack.push(act); return jsonify({"redone":"park","slot":slot})
    if typ == "enqueue":
        wait_q.enqueue(plate); undo_stack.push(act); return jsonify({"redone":"enqueue","plate":plate})
    if typ == "remove":
        n = bst.search(slot)
        if n and n.occupied:
            # redo remove
            n.occupied=False; n.plate=""; n.parked_at=0
            undo_stack.push(act)
            return jsonify({"redone":"remove","slot":slot})
    return jsonify({"msg":"Could not redo action"}),400

@parking_bp.route("/status", methods=["GET"])
def status():
    slots = []
    def _traverse(node):
        if not node: return
        _traverse(node.left)
        slots.append({"slot":node.slot_no,"occupied":node.occupied,"plate":node.plate})
        _traverse(node.right)
    _traverse(bst.root)
    return jsonify({"slots":slots,"queue":wait_q.peek_all(),"undo":undo_stack.list_all(),"redo":redo_stack.list_all()})

# BST route removed as per user request

@parking_bp.route("/weather", methods=["GET"])
def get_weather():
    """Get weather information using IPINFO token"""
    try:
        # Get location data using IPINFO
        ipinfo_token = config.IPINFO_TOKEN
        location_response = requests.get(f"https://ipinfo.io/json?token={ipinfo_token}", timeout=5)
        location_data = location_response.json()
        
        # Extract city from location data
        city = location_data.get("city", "Unknown")
        
        # For a more complete weather solution, you would integrate with a weather API
        # For now, we'll return mock data with the city
        return jsonify({
            "city": city,
            "temperature": 25,  # Mock temperature
            "condition": "Sunny",  # Mock condition
            "humidity": 60  # Mock humidity
        })
    except Exception as e:
        # Return default data if weather API fails
        return jsonify({
            "city": "Unknown",
            "temperature": 25,
            "condition": "Sunny",
            "humidity": 60
        })