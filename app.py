import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Function to create the database and table
def create_database():
    conn = sqlite3.connect('people.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS people
                 (id INTEGER PRIMARY KEY, name TEXT, description TEXT)''')
    conn.commit()
    conn.close()

# Function to retrieve all people from the database
def get_people():
    conn = sqlite3.connect('people.db')
    c = conn.cursor()
    c.execute('SELECT id, name, description FROM people')
    people = [{'id': row[0], 'name': row[1], 'description': row[2]} for row in c.fetchall()]
    conn.close()
    return people

# Function to insert a person into the database
def insert_person(name, description):
    conn = sqlite3.connect('people.db')
    c = conn.cursor()
    c.execute('INSERT INTO people (name, description) VALUES (?, ?)', (name, description))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return 'Welcome to Peoplepedia! <a href="/people">View People</a>'

@app.route('/people')
def list_people():
    return jsonify(get_people())

@app.route('/person/<int:person_id>')
def view_person(person_id):
    person = next((p for p in get_people() if p['id'] == person_id), None)
    if person:
        return jsonify(person)
    else:
        return jsonify({'error': 'Person not found'}), 404

@app.route('/add_person', methods=['POST'])
def add_person():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    if name and description:
        insert_person(name, description)
        return jsonify({'message': 'Person added successfully'}), 201
    else:
        return jsonify({'error': 'Name and description are required'}), 400

if __name__ == "__main__":
    create_database()  # Create the database and table if not exist
    app.run(debug=True)
