import os
import json
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))


@api.route('/api/test', methods=['POST'])
def save_data():
    if request.method == 'POST':
        # Получаем данные в формате JSON
        data = request.get_json()

        # Проверяем, что данные переданы и это массив объектов
        if not data or not isinstance(data, list):
            return jsonify({'error': 'Invalid data format. Expected a list of objects.'}), 400

        # Указываем путь к файлу для сохранения данных
        file_path = os.path.join(UPLOAD_FOLDER, 'data.json')

        # Сохраняем каждый объект из массива в файл
        try:
            with open(file_path, 'a') as f:
                for item in data:
                    # Проверяем, что каждый объект имеет необходимые поля
                    if not isinstance(item, dict) or 'id' not in item or 'status' not in item:
                        return jsonify({'error': f'Invalid item format: {item}'}), 400
                    # Записываем данные в файл
                    f.write(json.dumps(item) + '\n')
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        # Возвращаем успешный ответ
        return jsonify({'success': True}), 200

    return jsonify({'error': 'Invalid request method'}), 405
