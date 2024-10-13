import os
import json
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))


@api.route('/api/test', methods=['POST'])
def save_data():
    if request.method == 'POST':
        # get data in JSON format
        data = request.get_json()

        # check that the data has been transferred and that it is an array of objects
        if not data or not isinstance(data, list):
            return jsonify({'error': 'Invalid data format. Expected a list of objects.'}), 400

        # Specify the path to the file to save the data
        file_path = os.path.join(UPLOAD_FOLDER, 'data.json')

        # Save each object from the array to a file
        try:
            # Open the file with UTF-8 encoding specified
            with open(file_path, 'a', encoding='utf-8') as f:
                for item in data:
                    # check that each object has the required fields
                    if not isinstance(item, dict) or 'id' not in item or 'status' not in item:
                        return jsonify({'error': f'Invalid item format: {item}'}), 400
                    # write data to a file, specifying ensure_ascii=False to display characters correctly.
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        # Return a successful response
        return jsonify({'success': True}), 200

    return jsonify({'error': 'Invalid request method'}), 405
