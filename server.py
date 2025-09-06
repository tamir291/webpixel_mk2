from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Хранилище пикселей в памяти (можно заменить на базу данных)
pixels = {}
pending_commands = []

@app.route('/api/state', methods=['GET'])
def get_state():
    """Возвращает текущее состояние всех пикселей"""
    return jsonify(pixels)

@app.route('/api/command', methods=['POST'])
def handle_command():
    """Принимает команду от браузера"""
    data = request.json
    user_id = data.get('user_id')
    x = data.get('x')
    y = data.get('y')
    color = data.get('color')
    
    if all([user_id, x is not None, y is not None, color]):
        # Сохраняем пиксель
        key = f"{x}_{y}"
        pixels[key] = color
        
        # Добавляем в очередь для ESP32
        command = f"{x} {y} {color}"
        pending_commands.append(command)
        
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error'})

@app.route('/api/commands', methods=['GET'])
def get_commands():
    """ESP32 забирает команды из очереди"""
    if pending_commands:
        command = pending_commands.pop(0)
        return jsonify({'command': command})
    return jsonify({'command': None})

@app.route('/api/reset', methods=['POST'])
def reset_pixels():
    """Сброс всех пикселей (опционально)"""
    global pixels, pending_commands
    pixels = {}
    pending_commands = []
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
