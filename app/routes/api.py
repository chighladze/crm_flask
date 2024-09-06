import os
import json
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))

@api.route('/api/test', methods=['POST'])
def save_data():
    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'})


        file_path = os.path.join(UPLOAD_FOLDER, 'data.json')


        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')

        return jsonify({'message': 'Data saved successfully', 'file_path': file_path})

    return jsonify({'error': 'Invalid request method'})
