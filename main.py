# Required Imports
import os
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app

# Initialize Flask App
app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
todo_ref = db.collection('voting')


# Register a student as a voter
@app.route('/register/', methods=['POST'])
def register_voter():
    record = json.loads(request.data)
    voters_ref = db.collection('voters')
    student_id = record.get('student_id')
    query = voters_ref.where('student_id', '==', student_id).get()
    if len(query) > 0:
        return jsonify({'error':'Student ID already exists'}), 400
    voters_ref.document(student_id).set(record)
    return jsonify(record)

# De-register a student as a voter
@app.route('/deregister/<string:student_id>/', methods=['DELETE'])
def deregister_voter(student_id):
    voters_ref = db.collection('voters').document(student_id)
    if not voters_ref.get().exists:
        return jsonify({'error': 'Student ID does not exist'}), 404
    voters_ref.delete()
    return jsonify({'message':f'Student with ID {student_id} has been deleted successfully'})

# Updating a voter's information
@app.route('/update-voter/', methods=['PATCH'])
def update_record():
    record = json.loads(request.data)
    student_id = record.get('student_id')
    voters_ref = db.collection('voters').document(student_id)
    if not voters_ref.get().exists:
        return jsonify({'error': 'Student ID does not exist'}), 404
    voters_ref.update(record)
    return jsonify(record)

# Retrieving a voter's information
@app.route('/voters/<string:student_id>/', methods=['GET'])
def get_voter(student_id):
    voters_ref = db.collection('voters').document(student_id)
    if not voters_ref.get().exists:
        return jsonify({'error': 'Student ID does not exist'}), 404
    record = voters_ref.get().to_dict()
    return jsonify(record)

# Creating an election
@app.route('/election/', methods=['POST'])
def create_election():
    record = json.loads(request.data)
    elections_ref = db.collection('elections')
    election_id = record.get('election_id')
    query = elections_ref.where('election_id', '==', election_id).get()
    if len(query) > 0:
        return jsonify({'error':'Election ID already exists.'}), 400 
    elections_ref.document(election_id).set(record)
    return jsonify(record)

# Retrieving an election by id
@app.route('/election/<string:election_id>/', methods=['GET'])
def get_election(election_id):
    elections_ref = db.collection('elections').document(election_id)
    if not elections_ref.get().exists:
        return jsonify({'error': 'The election id has not been found.'}), 404
    record = elections_ref.get().to_dict()
    return jsonify(record)

# Deleting an election by id
@app.route('/election/<string:election_id>/delete', methods=['DELETE'])
def delete_election(election_id):
    election_ref = db.collection('elections').document(election_id)
    if not election_ref.get().exists:
        return jsonify({'error':'Election ID not found'}), 404
    election_ref.delete()
    return jsonify({'message':f'An election with ID {election_id} has been deleted successfully.'})

# Voting in an election
@app.route('/election/<string:election_id>/vote', methods=['POST'])
def vote(election_id):
    request_data = json.loads(request.data)
    student_id = request_data.get('student_id')
    election_ref = db.collection('elections').document(election_id)
    if not election_ref.get().exists:
        return jsonify({'error': 'The election id has not been found'})

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)