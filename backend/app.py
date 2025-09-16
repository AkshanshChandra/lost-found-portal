from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)  # allow frontend JS to call backend

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["lostfound"]
items_collection = db["items"]

# ------------------------------
# ROUTES
# ------------------------------

# ✅ 1. Report new item (Lost/Found)
@app.route("/items", methods=["POST"])
def add_item():
    data = request.json
    new_item = {
        "title": data.get("title"),
        "description": data.get("description"),
        "category": data.get("category"),
        "status": data.get("status"),  # "lost" or "found"
        "location": data.get("location")
    }
    result = items_collection.insert_one(new_item)
    new_item["_id"] = str(result.inserted_id)
    return jsonify(new_item), 201


# ✅ 2. Get all items (with optional filters)
@app.route("/items", methods=["GET"])
def get_items():
    query = {}
    category = request.args.get("category")
    status = request.args.get("status")
    location = request.args.get("location")

    if category:
        query["category"] = category
    if status:
        query["status"] = status
    if location:
        query["location"] = location

    items = []
    for item in items_collection.find(query):
        item["_id"] = str(item["_id"])
        items.append(item)

    return jsonify(items)


# ✅ 3. Get single item by ID
@app.route("/items/<id>", methods=["GET"])
def get_item(id):
    item = items_collection.find_one({"_id": ObjectId(id)})
    if item:
        item["_id"] = str(item["_id"])
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404


# ✅ 4. Update item status (e.g., from lost → returned)
@app.route("/items/<id>", methods=["PUT"])
def update_item(id):
    data = request.json
    update_data = {}
    if "status" in data:
        update_data["status"] = data["status"]

    result = items_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )

    if result.matched_count > 0:
        return jsonify({"message": "Item updated"})
    return jsonify({"error": "Item not found"}), 404


# ✅ 5. Delete an item
@app.route("/items/<id>", methods=["DELETE"])
def delete_item(id):
    result = items_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"message": "Item deleted"})
    return jsonify({"error": "Item not found"}), 404


# Run
if __name__ == "__main__":
    app.run(debug=True)
