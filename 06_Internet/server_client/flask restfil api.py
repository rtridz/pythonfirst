from flask import Flask, jsonify
from flask import abort
app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Купить продукты',
        'description': u'Молоко, чипсы, картофель', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Изучить Python API',
        'description': u'Нужно больше практики', 
        'done': False
    }
]



@app.route('/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if not task == 0:
        abort(404)
    return jsonify({'task': task[0]})

@app.route('/')
def index():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True)