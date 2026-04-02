from flask import Flask, request, jsonify
from datetime import datetime, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import requests
import jwt
import os

app = Flask(__name__)
CORS(app)

SECRET_KEY = "bonjour"
TOKEN_EXPIRATION = 3600

client = MongoClient(os.environ["MONGO_URI"])
db = client["authdb"]
users_collection = db["users"]
passwords_collection = db["passwords"]

hasher = PasswordHasher()

roles = ["ADMIN","USER"]

def format_user(user):
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "active": user["active"],
        "createdAt": user["createdAt"],
        "updatedAt": user["updatedAt"]
    }

@app.route("/auth/verify", methods=["POST"])
def verify_token():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"valid": True,"user_id": decoded["user_id"]}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json

    required = ["username", "password"]
    for elem in required:
        if elem not in data:
            return jsonify({"error": "Missing fields"}), 400

    user = users_collection.find_one({"username": data["username"]})

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    pwd = passwords_collection.find_one({"user_id": user["_id"]})
    if not pwd:
        return jsonify({"error": "Invalid credentials"}), 401

    try:
        hasher.verify(pwd["password"], data["password"])
    except VerifyMismatchError:
        return jsonify({"error": "Invalid credentials"}), 401

    if not user["active"]:
        return jsonify({"error": "User disabled"}), 403
    
    token = jwt.encode({
        "user_id": str(user["_id"]),
        "exp": datetime.now(timezone.utc).timestamp() + TOKEN_EXPIRATION
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"accessToken": token,"user": format_user(user)}), 200


@app.route("/users", methods=["GET"])
def list_users():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post("http://proxy/auth/verify", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Not authorized"}), 401
    except requests.RequestException:
        return jsonify({"error": "Unable to check token, check /auth API"}), 401
    
    users = []
    for user in users_collection.find():
        users.append(format_user(user))
        
    return jsonify(users), 200


@app.route("/users", methods=["POST"])
def create_user():
    data = request.json

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post("http://proxy/auth/verify", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Not authorized"}), 401
    except requests.RequestException:
        return jsonify({"error": "Unable to check token, check /auth API"}), 401

    required = ["username", "email", "password"]

    for elem in required:
        if not elem in data or not data[elem]:
             return jsonify({"error": "Please fill all required fields."}), 400

    role = data.get("role")  
    if role and not role in roles:
        return jsonify({"error": "Please provide a valid role."}), 400
    
    if users_collection.find_one({"username": data["username"]}):
        return jsonify({"error": "Username already exists"}), 400

    now = datetime.now(timezone.utc).isoformat()

    new_user = {
        "username": data["username"],
        "email": data["email"],
        "role": data.get("role", "USER"),
        "active": data.get("active", True),
        "createdAt": now,
        "updatedAt": now
    }

    result = users_collection.insert_one(new_user)

    passwords_collection.insert_one({
        "user_id": result.inserted_id,
        "password": hasher.hash(data["password"])
    })

    user = users_collection.find_one({"_id": result.inserted_id})
    return jsonify(format_user(user)), 201

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post("http://proxy/auth/verify", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Not authorized"}), 401
    except requests.RequestException:
        return jsonify({"error": "Unable to check token, check /auth API"}), 401

    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return jsonify({"error": "Invalid ID"}), 400

    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    
    return jsonify(format_user(user)), 200

@app.route("/users/<user_id>", methods=["PATCH"])
def update_user(user_id):
    data = request.json

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post("http://proxy/auth/verify", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Not authorized"}), 401
    except requests.RequestException:
        return jsonify({"error": "Unable to check token, check /auth API"}), 401

    try:
        real_id = ObjectId(user_id)
    except:
        return jsonify({"error": "Invalid ID"}), 400

    user = users_collection.find_one({"_id": real_id})

    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    
    role = data.get("role")  
    if role and not role in roles:
        return jsonify({"error": "Please provide a valid role."}), 400
    
    update_fields = {}
    for elem in ["username", "email", "role", "active"]:
        if elem in data:
            update_fields[elem] = data[elem]

    if update_fields:
        update_fields["updatedAt"] = datetime.now(timezone.utc).isoformat()
        users_collection.update_one({"_id": real_id}, {"$set": update_fields})

    if data.get("password"):
        passwords_collection.update_one(
            {"user_id": real_id},
            {"$set": {"password": hasher.hash(data["password"])}})

    updated_user = users_collection.find_one({"_id": real_id})
    return jsonify(format_user(updated_user)), 200

@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post("http://proxy/auth/verify", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Not authorized"}), 401
    except requests.RequestException:
        return jsonify({"error": "Unable to check token, check /auth API"}), 401

    try:
        real_id = ObjectId(user_id)
    except:
        return jsonify({"error": "Invalid ID"}), 400

    result = users_collection.delete_one({"_id": real_id})

    if result.deleted_count == 0:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    passwords_collection.delete_one({"user_id": real_id})

    return jsonify({"success": True, "message": "User deleted", "id": user_id}), 200

@app.route("/users/health", methods=["GET"])
def get_health_users():
    response = {
        "status": "ok",
        "service": "Users",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return jsonify(response), 200
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)