from flask import Flask, request, jsonify
from datetime import datetime, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask_cors import CORS #pour try sur swagger
import requests
import uuid
import json

app = Flask(__name__)
CORS(app)

def get_file(path):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
def save_file(path, data):
    with open(path, "w") as file:
        json.dump(data, file)

def load_users():
    return get_file("./data/users.json")

def save_users(events):
    save_file("./data/users.json", events)

def load_passwords():
    return get_file("./data/pwd.json")

def save_passwords(pwds):
    save_file("./data/pwd.json", pwds)

def load_tokens():
    return get_file("./data/tokens.json")

def save_tokens(tokens):
    save_file("./data/tokens.json", tokens)
    
hasher = PasswordHasher() #instance qui hash avec salt

@app.route("/auth/verify", methods=["POST"])
def verify_token():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    tokens = load_tokens()
    if token not in tokens.values():
        return jsonify({"error": "Invalid token"}), 401

    return jsonify({"valid": True}), 200
    
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json

    required = ["username", "password"]
    for elem in required:
        if elem not in data:
            return jsonify({"error": "Missing fields"}), 400

    users = load_users()
    passwords = load_passwords()

    user_data = None
    user_id = None

    for uid, value in users.items():
        if value["username"] == data["username"]:
            user_data = value
            user_id = uid
            break

    if not user_data:
        return jsonify({"error": "Invalid credentials"}), 401

    hashed_password = passwords[user_id]

    try:
        hasher.verify(hashed_password, data["password"])
    except VerifyMismatchError:
        return jsonify({"error": "Invalid credentials"}), 401

    if not user_data["active"]:
        return jsonify({"error": "User disabled"}), 403
    
    tokens = load_tokens()
    if not user_id in tokens:
        tokens[user_id] = "token"+user_id
        save_tokens(tokens)

    return jsonify({"accessToken": tokens[user_id],"user": user_data}), 200

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
    
    users = load_users()
    return jsonify(list(users.values())), 200

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
        if not elem in data or not data[elem]: #inexistant ou null
             return jsonify({"error": "Please fill all required fields."}), 400
    
    users = load_users()

    for user in users.values():
        if user["username"] == data["username"]:
            return jsonify({"error": "Username already exists"}), 400

    passwords = load_passwords()
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "username": data["username"],
        "email": data["email"],
        "role": data.get("role", "USER"),
        "active": data.get("active", True),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }

    passwords[user_id] = hasher.hash(data["password"])
    users[user_id] = new_user
    save_passwords(passwords)
    save_users(users)
    return jsonify(new_user), 201

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

    users = load_users()
    user = users.get(user_id) #ne provoque pas de key error si inexistant, semblable a userid in users
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    
    return jsonify(user), 200

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

    users = load_users()
    user = users.get(user_id)

    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    
    elems = ["username", "email", "role", "active"]
    for elem in elems:
        if elem in data:
            user[elem] = data[elem]
    user["updatedAt"] = datetime.now(timezone.utc).isoformat()

    passwords = load_passwords()
    if data.get("password"):
        passwords[user_id] = hasher.hash(data["password"])
        save_passwords(passwords)
    
    users[user_id] = user
    save_users(users)
    return jsonify(user), 200

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

    users = load_users()
    
    if not user_id in users:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    
    users.pop(user_id, None) #delete
    save_users(users)

    return jsonify({"success": True, "message": "User deleted", "id": user_id}), 200
    

users = load_users() # temp, autocreate admin
passwords = load_passwords()
tokens = load_tokens()
    
default_username = "admin"
default_password = "admin123"

if not any(u["username"] == default_username for u in users.values()):
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "username": default_username,
        "email": "admin@example.com",
        "role": "ADMIN",
        "active": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }
    users[user_id] = new_user
    passwords[user_id] = hasher.hash(default_password)
    tokens[user_id] = "token"+user_id
        
    save_users(users)
    save_passwords(passwords)
    save_tokens(tokens)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)