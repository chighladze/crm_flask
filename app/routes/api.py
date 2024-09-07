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

        # Проверяем, что это массив объектов
        if not isinstance(data, list):
            return jsonify({'error': 'Data should be a list of objects'}), 400

        # Указываем путь к файлу, куда будем сохранять данные
        file_path = os.path.join(UPLOAD_FOLDER, 'data.json')

        # Переменная для хранения ошибок, если они есть
        errors = []

        # Проходим по каждому объекту в массиве
        for item in data:
            if 'error_code' in item:
                # Если есть ошибка, добавляем её в список ошибок
                errors.append({
                    'id': item.get('id'),
                    'error_code': item.get('error_code'),
                    'error_message': item.get('error_message', 'No error message provided')
                })

            # Сохраняем данные в файл, даже если есть ошибки
            with open(file_path, 'a') as f:
                f.write(json.dumps(item) + '\n')

        # Если были ошибки, возвращаем их вместе с успешным ответом
        if errors:
            return jsonify({
                'message': 'Data processed with errors',
                'errors': errors,
                'file_path': file_path
            }), 200

        # Возвращаем успешный ответ, если ошибок нет
        return jsonify({'message': 'Data saved successfully', 'file_path': file_path}), 200

    return jsonify({'error': 'Invalid request method'}), 405
