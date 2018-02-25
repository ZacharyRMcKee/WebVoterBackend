#!flask/bin/python
from flask import Flask, jsonify, make_response, abort, request
import psycopg2
from flask_cors import CORS
app = Flask(__name__)
conn = psycopg2.connect(dbname="postgres",user="postgres",password="1234567890");
conn.set_session(isolation_level="SERIALIZABLE")
CORS(app)


@app.errorhandler(404)
def not_found(error):
    print("404 sent")
    return make_response(jsonify({'error': 'Not found'}),404)
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks':tasks})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

@app.route('/<int:userid>/<query>', methods=['GET'])
def get_queryset(userid,query):
	cur = conn.cursor();
	cmd = "SELECT url, rating, vote FROM queryLink NATURAL JOIN queryLink_user where queryLink.query=%s AND userid=%s;"
	print("GET REQUESTED")
	print(query)
	print(userid)
	cur.execute(cmd,(query,userid))
	raw = cur.fetchall()
	#cmd = "SELECT vote FROM queryLink_user where query=%s AND userid=%d;"
	#cur.execute(cmd,(query,userid))
	links = []
	print(raw)
	for i in range(len(raw)):
		print(raw[i])
		list_dict = {}
		list_dict['url'] = raw[i][0]
		list_dict['rating'] = raw[i][1]
		list_dict['vote'] = raw[i][2]
		links.append(list_dict)
	cmd = "SELECT url, rating FROM queryLink WHERE query=%s AND url NOT IN (SELECT url FROM queryLink NATURAL JOIN queryLink_user WHERE queryLink.query=%s AND userid=%s);"
	cur.execute(cmd,(query,query,userid))
	raw = cur.fetchall()
	for i in range(len(raw)):
		list_dict = {}
		list_dict['url'] = raw[i][0]
		list_dict['rating'] = raw[i][1]
		list_dict['vote'] = 0
		links.append(list_dict)
	print(links)
	return jsonify({'links':links})		

@app.route('/<int:userid>/<query>', methods=['POST'])
def post_queryset(userid,query):
	print("POST RECEIVED")
	cur = conn.cursor();
	if not request.json or not 'query' in request.json:
		abort(400)
	inp = request.get_json()
	print(type(inp))
	print(inp)
	query = inp['query']
	links = inp['links']
	print(links)
	for i in links:
		cmd = "INSERT INTO queryLink (url,query,rating) VALUES (%s,%s,0) ON CONFLICT DO NOTHING;"
		cur.execute(cmd,(i,query))
	conn.commit()	
	return "POST RECEIVED"

@app.route('/<int:userid>/<query>/', methods=['PUT'])
def vote_link(userid,query):
	if not request.json:
		abort(400)
	cur = conn.cursor()
	inp = request.get_json()
	vote = int(inp['vote'])
	url = inp['url']	
	if(not userid or not (vote==0 or vote==-1 or vote==1)):
		abort(403)
	
	cmd = "INSERT INTO queryLink_user (url,query,userid,vote) VALUES (%s,%s,%s,%s) ON CONFLICT (url,query,userid) DO UPDATE SET vote=%s;"
	try:	
		cur.execute(cmd,(url,query,userid,vote,vote))
	except psycopg2.IntegrityError:
		conn.rollback()
		abort(403)	
		
	conn.commit()
	#'query': request.json['query'],
    	#'description': request.json.get('description',""),
	#'done': False
	#return jsonify({'task': task}), 201
	return "Vote counted"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
