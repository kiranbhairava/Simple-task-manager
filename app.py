from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

DATA_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    tasks = load_tasks()
    
    new_task = {
        'id': max([t['id'] for t in tasks], default=0) + 1,
        'title': data['title'],
        'description': data.get('description', ''),
        'priority': data.get('priority', 'medium'),
        'status': data.get('status', 'pending'),
        'dueDate': data.get('dueDate', ''),
        'dueTime': data.get('dueTime', ''),
        'assignee': data.get('assignee', ''),
        'category': data.get('category', ''),
        'createdAt': datetime.now().isoformat(),
        'completedAt': None
    }
    
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    tasks = load_tasks()
    
    for task in tasks:
        if task['id'] == task_id:
            task['title'] = data.get('title', task['title'])
            task['description'] = data.get('description', task['description'])
            task['priority'] = data.get('priority', task['priority'])
            task['status'] = data.get('status', task['status'])
            task['dueDate'] = data.get('dueDate', task['dueDate'])
            task['dueTime'] = data.get('dueTime', task.get('dueTime', ''))
            task['assignee'] = data.get('assignee', task.get('assignee', ''))
            task['category'] = data.get('category', task.get('category', ''))
            
            if data.get('status') == 'completed' and task['completedAt'] is None:
                task['completedAt'] = datetime.now().isoformat()
            elif data.get('status') != 'completed':
                task['completedAt'] = None
            
            save_tasks(tasks)
            return jsonify(task)
    
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    return '', 204

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(debug=True, port=5000)