import os
import json
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))


@api.route('/api/test', methods=['POST', 'GET', 'PUT'])
def save_data():
    if request.method == 'POST':
        # Получаем данные в формате JSON
        data = request.get_json()

        # Проверяем, что данные переданы
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Указываем путь к файлу, куда будем сохранять данные
        file_path = os.path.join(UPLOAD_FOLDER, 'data.json')

        # Сохраняем данные в файл
        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')

        # Возвращаем успешный ответ
        return jsonify({'message': 'Data saved successfully', 'file_path': file_path}), 200

    return jsonify({'error': 'Invalid request method'}), 405
