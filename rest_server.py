from flask import Flask
from flask import jsonify
from flask import make_response
from flask import abort
from flask import request
from flask import url_for
from flask import send_from_directory
from flask.ext.httpauth import HTTPBasicAuth
from mongo_crud_easier import MongoCrudEasier

app = Flask(__name__)
auth = HTTPBasicAuth()
mce = MongoCrudEasier()

def make_public_task(task):
	new_task= {}
	for field in task:
		if field == 'id':
			new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
		else:
			new_task[field] = task[field]
	return new_task

@app.route('/')
def index():
	return send_from_directory(".", "index.html")

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
	task = [task for task in mce.read() if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	return jsonify({ 'tasks': make_public_task({k: v for k, v in task[0].items() if k != '_id'}) } )

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
	tasks = [make_public_task(task) for task in mce.read()]
	tasks_tmp = []
	for task in tasks:
		tmp_task = {}
		for k, v in task.items():
			if k != '_id':
				tmp_task[k] = v
		tasks_tmp.append(tmp_task)
	return jsonify({'tasks': tasks_tmp})

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
	if not request.json or not 'title' in request.json:
		abort(400)
	task = {
		'id': mce.next_entry_id(),
		'title': request.json['title'],
		'description': request.json.get('description', ""),
		'done': False
	}
	mce.create(task['id'], task['title'], task['description'], task['done'])
	return jsonify({'task': make_public_task(task)}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
	task = [task for task in mce.read() if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	if not request.json:
		abort(400)
	if 'title' in request.json and type(request.json['title']) != str:
		abort(400)
	if 'description' in request.json and type(request.json['description']) != str:
		abort(400)
	if 'done' in request.json and type(request.json['done']) is not bool:
		abort(400)

	task[0]['title'] = request.json.get('title', task[0]['title'])
	task[0]['description'] = request.json.get('description', task[0]['description'])
	task[0]['done'] = request.json.get('done', task[0]['done'])

	mce.update(task[0]['id'], task[0]['title'], task[0]['description'], task[0]['done'])
	return jsonify({ 'task': make_public_task({k: v for k, v in task[0].items() if k != '_id'}) } )

@app.route('/todo/api/v1.0/tasks/<int:task_id>' ,methods=['DELETE'])
def delete_task(task_id):
	task = [task for task in mce.read() if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	mce.remove(task[0]['id'])
	return jsonify({'result': True})

@auth.get_password
def get_password(username):
	if username == 'heros':
		return 'python'

@auth.error_handler
def unauthorized():
	return make_response(jsonify({'error': 'Unauthorized access'}), 401)


if __name__ == '__main__':
	app.run(debug=True)