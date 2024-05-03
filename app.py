from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
# Import the Config class from your config.py file
from config import Config

# Initialize Google API key
google_api_key = Config.GOOGLE_API_KEY

# Initialize Google Gemini
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key)

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

# Function to delete a person from the database
def delete_person(person_id):
    conn = sqlite3.connect('people.db')
    c = conn.cursor()
    c.execute('DELETE FROM people WHERE id = ?', (person_id,))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return 'Welcome to Peoplepedia! <a href="/people">View People</a>'

@app.route('/people')
def list_people():
    return jsonify(get_people())

def generate_summary(description):
    # Construct HumanMessage object
    message = HumanMessage(content=f"Summarize the following description: {description}")

    # Call the model's prediction method
    output_data = llm([message], stop=['prompt'])

    # Check the structure of the output data
    print(output_data)

    # Extract the summary from the output data
    if isinstance(output_data, list):
        summary = output_data[0]['text'].strip()  # Assuming only one summary is returned
    elif hasattr(output_data, 'choices') and output_data.choices:
        summary = output_data.choices[0]['text'].strip()
    else:
        summary = output_data.content.strip()

    return summary


@app.route('/person/<int:person_id>')
def view_person(person_id):
    person = next((p for p in get_people() if p['id'] == person_id), None)
    if person:
        summary = generate_summary(str(person['description']))
        person['summary'] = summary
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

@app.route('/delete_person/<int:person_id>', methods=['DELETE'])
def delete_person_route(person_id):
    # Check if the person exists
    person = next((p for p in get_people() if p['id'] == person_id), None)
    if person:
        delete_person(person_id)
        return jsonify({'message': f'Person with ID {person_id} deleted successfully'})
    else:
        return jsonify({'error': 'Person not found'}), 404

if __name__ == "__main__":
    create_database()  # Create the database and table if not exist
    app.run(debug=True)
