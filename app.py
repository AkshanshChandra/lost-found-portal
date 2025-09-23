from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = "lost_and_found_wp"  

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["lost_found_db"]
users = db["users"]
items = db["items"]

# Upload folder configuration
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HOME 
@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login"))

    filter_type = request.args.get("filter")
    search_query = request.args.get("q", "")

    query = {}
    if filter_type in ["lost", "found"]:
        query["type"] = filter_type

    if search_query:
        query["$or"] = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"description": {"$regex": search_query, "$options": "i"}}
        ]

    item_list = list(items.find(query).sort("_id", -1))
    return render_template("landing.html", items=item_list, filter=filter_type)


# USER AUTH
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.find_one({"username": username, "password": password, "role": "user"})
        if user:
            session["username"] = username
            session["role"] = "user"
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = users.find_one({"username": username})
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        users.insert_one({"username": username, "password": password, "role": "user"})
        flash("Registration successful. Please login.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# POST ITEM
@app.route("/post", methods=["GET", "POST"])
def post_item():
    if "username" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        item_type = request.form["type"]
        file = request.files["image"]

        filename = None
        if file and file.filename.strip() != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        contact = request.form.get("contact", "")

        items.insert_one({
            "title": title,
            "description": description,
            "type": item_type,
            "image": filename,
            "posted_by": session["username"],
            "contact": contact
        })
        flash("Item posted successfully")
        return redirect(url_for("home"))

    # If GET request → just render the form
    return render_template("post_item.html")


# ADMIN AUTH
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin = users.find_one({"username": username, "password": password, "role": "admin"})
        if admin:
            session["username"] = username
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials")
    return render_template("admin_login.html")

# ADMIN DASHBOARD
@app.route("/admin/dashboard")
def admin_dashboard():
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("admin_login"))

    all_items = list(items.find().sort("_id", -1))
    return render_template("admin_dashboard.html", items=all_items)

@app.route("/admin/delete/<item_id>")
def admin_delete(item_id):
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("admin_login"))

    items.delete_one({"_id": ObjectId(item_id)})
    flash("Item deleted successfully")
    return redirect(url_for("admin_dashboard"))

# INITIALIZE DEFAULT ADMIN
def create_default_admin():
    existing_admin = users.find_one({"role": "admin"})
    if not existing_admin:
        users.insert_one({"username": "admin", "password": "admin123", "role": "admin"})
        print("Default admin created: username=admin, password=admin123")


#ITEM DETAIL
@app.route("/item/<item_id>")
def item_detail(item_id):
    if "username" not in session:
        return redirect(url_for("login"))

    item = items.find_one({"_id": ObjectId(item_id)})
    if not item:
        flash("Item not found")
        return redirect(url_for("home"))

    return render_template("item_detail.html", item=item)


if __name__ == "__main__":
    create_default_admin()
    app.run(debug=True)
