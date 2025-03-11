from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta

 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch Donkey Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    """Return the list of todo items"""
    
    todos = Todo.query.all()
    completed = request.args.get('completed')
    window = request.args.get('window', type=int)
    
    if completed is not None:
        completed = completed.lower() == 'true'
        
    cutoff_date = None
    if window is not None:
        cutoff_date = datetime.now() + timedelta(days=window)
        
    result = []
    for todo in todos:
        if completed is not None and todo.completed != completed:
            continue
        if cutoff_date and todo.deadline_at > cutoff_date:
            continue
        result.append(todo.to_dict())
        
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Return the details of a todo item"""
    
    todo = db.session.get(Todo, todo_id)

    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo item and return the created item"""
    
    if not request.is_json or 'title' not in request.json:
        return jsonify({"error": 'Not valid format'}), 400
    
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    
    allowed_keys = ['title', 'description', 'completed', 'deadline_at']
    incorrect_keys = [key for key in request.get_json() if key not in allowed_keys]
    
    if incorrect_keys:
        return jsonify({'error': 'Extra field'}), 400
    
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
        
    db.session.add(todo)
    db.session.commit()
    
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo item and return the updated item"""

    if not request.is_json:
        return jsonify({"error": 'Not valid format'}), 404
    
    todo = db.session.get(Todo, todo_id)    
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    allowed_keys = ['title', 'description', 'completed', 'deadline_at']
    incorrect_keys = [key for key in request.get_json() if key not in allowed_keys]
    
    if incorrect_keys:
        return jsonify({'error': 'Extra field'}), 400
        
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    
    db.session.commit()
    
    return jsonify(todo.to_dict()), 200

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo item and return the deleted item"""
    
    todo = db.session.get(Todo, todo_id)
    
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify(todo.to_dict()), 200
 
