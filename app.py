from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Set up DB connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # so we can access columns by name
    return conn


# Basic routes for user handling
@app.route('/')
def home():
    return "User Management System API is running."

@app.route('/users', methods=['GET'])
def get_all_users(): # getting all users
    conn = get_db_connection()
    users_cursor = conn.execute("SELECT id, name, email FROM users").fetchall()
    conn.close()

    users = [dict(user) for user in users_cursor]
    return jsonify(users), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id): # get user function
    conn = get_db_connection()
    user = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    if user:
        return jsonify(dict(user)), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user(): # create user function
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']
        password = data['password']
    except (TypeError, KeyError):
        return jsonify({"error": "Missing required fields: name, email, password"}), 400

    # Encrypt the password before saving
    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )
        conn.commit()
        new_user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    except sqlite3.IntegrityError:
        # Email already exists (assuming there's a UNIQUE constraint on email)
        conn.close()
        return jsonify({"error": "Email already exists"}), 409
    finally:
        conn.close()

    return jsonify({"message": "User created", "user_id": new_user_id}), 201

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id): # update user function
    try:
        data = request.get_json()
        if not data or ('name' not in data and 'email' not in data):
            return jsonify({"error": "At least one of name or email is required"}), 400
    except TypeError:
        return jsonify({"error": "Invalid JSON"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    # Use new data if provided, otherwise keep existing values
    name = data.get('name', user['name'])
    email = data.get('email', user['email'])

    conn.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "User updated"}), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id): # delete user function
    conn = get_db_connection()
    result = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    if result.rowcount > 0:
        return jsonify({"message": f"User {user_id} deleted"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/search', methods=['GET'])
def search_users(): #search user function
    name = request.args.get('name')

    if not name:
        return jsonify({"error": "Missing query parameter: name"}), 400

    conn = get_db_connection()
    users_cursor = conn.execute("SELECT id, name, email FROM users WHERE name LIKE ?", ('%' + name + '%',))
    users = [dict(user) for user in users_cursor.fetchall()]
    conn.close()

    return jsonify(users), 200

@app.route('/login', methods=['POST'])
def login(): # login
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
    except (TypeError, KeyError):
        return jsonify({"error": "Missing required fields: email and password"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    # Check if user exists and password is valid
    if user and check_password_hash(user['password'], password):
        return jsonify({"status": "success", "user_id": user['id']}), 200
    else:
        return jsonify({"status": "failed", "error": "Invalid email or password"}), 401

if __name__ == '__main__':
    # Default port is set to 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
