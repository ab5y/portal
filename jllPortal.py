# all imports
import os
import sqlite3
import json
from flask import Flask, request, session, g, redirect, url_for, \
	 abort, render_template, flash
from flask_mail import Mail, Message
from contextlib import closing
from werkzeug import secure_filename

# create application
app = Flask(__name__)

# configuration
DATABASE = os.path.join(app.root_path, 'jll.db')
UPLOAD_FOLDER = os.path.join(app.root_path, 'static\Images')
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'jllportal@gmail.com'
MAIL_PASSWORD = 'Mygo@999'

app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mail = Mail(app)

# Helper functions

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def make_dicts(cursor, row):
	return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
	db = connect_db()
	cur = db.execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def send_mail(message):
	msg = Message("New portal created for you!",
					sender="master@portal.com",
					recipients = [request.form['email']])
	msg.body = message
	mail.send(msg)

# Web app functions

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

@app.route('/')
def show_portals():
	cur = g.db.execute('select client.name, clientContact.firstName, clientContact.lastName, clientContact.email, client.id, client.imgFilename from client, clientContact where client.id = clientContact.clientId order by client.id desc')
	portals = [dict(name=row[0], firstName=row[1], lastName=row[2], email=row[3], id=row[4], imgFilename=row[5]) for row in cur.fetchall()]
	return render_template('show_portals.html', portals=portals)

@app.route('/new_portal', methods=['GET', 'POST'])
def new_portal():
	error = None
	if not session.get('logged_in'):
		abort(401)
	if request.method == 'POST':
		
		# Upload Image
		filename = ''
		file = request.files['clientPic']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

		g.db.execute('insert into client (name, imgFilename) values (?, ?)',
					 [request.form['clientName'], filename])
		cur = g.db.execute('select max(id) FROM client')
		clientId = cur.fetchone()[0]
		address = request.form['street'] + ', ' + request.form['suburb'] + ', ' + request.form['state'] + ' ' + request.form['postcode']
		g.db.execute('insert into clientContact values (?, ?, ?, ?, ?, ?)',
					 [request.form['firstName'], request.form['lastName'], request.form['email'], request.form['phone'],
					  address, clientId])
		
		cur = g.db.execute('select * from property')
		properties = [make_dicts(cur, row) for row in cur.fetchall()]
		for prop in properties:
			g.db.execute('insert into client_property values (?, ?, ?, ?, ?)',
							(clientId, prop['id'], 'null', 'null', 0))

		g.db.commit()

		flash('New portal was successfully posted')
		message = "Dear "+request.form['firstName']+", \nA portal has been created for you."
		send_mail(message)
		return redirect(url_for('show_portals'))
	return render_template('new_portal.html', error=error)

@app.route('/portal', methods=['GET', 'POST'])
def portal():
	error = None
	id = request.args.get('id')
	if request.method == 'GET':
		cur = g.db.execute('select * from client, clientContact where client.id = '+id+' AND clientContact.clientId = '+id)
		portal = make_dicts(cur, cur.fetchone())
		cur = g.db.execute('select * from property')
		properties = [make_dicts(cur, row) for row in cur.fetchall()]
		cur = g.db.execute('select * from client_property where clientId='+id)
		propvals = [make_dicts(cur, row) for row in cur.fetchall()]
		return render_template('portal.html', portal=portal, properties=properties, propvals=propvals)

@app.route('/table_ajax', methods=['POST'])
def table_ajax():
	if request.method == 'POST':
		dump = json.dumps(request.json)
		data = json.loads(dump)
		dbArg=''
		jsonArg=''
		if 'like' in data:
			dbArg = 'rating=?'
			jsonArg = 'like'
		elif 'request' in data:
			dbArg = 'showing=?'
			jsonArg = 'request'
		elif 'comment' in data:
			dbArg = 'comment=?'
			jsonArg = 'comment'

		g.db.execute('update client_property set '+dbArg+' where clientId=? AND propertyId=?', 
						(data[jsonArg], data['clientId'], data['propId']))
		g.db.commit()
	return render_template('testing.html')

@app.route('/edit_portal', methods=['GET', 'POST'])
def edit_portal():
	error = None
	id = request.args.get('id')
	if request.method == 'GET':
		cur = g.db.execute('select * from client, clientContact where client.id = '+id+' AND clientContact.clientId = '+id)
		portal = make_dicts(cur, cur.fetchone())
		return render_template('edit_portal.html', portal=portal)
	elif request.method == 'POST':
		# Upload Image
		filename = ''
		file = request.files['clientPic']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		if filename != '':
			g.db.execute('update client set name=?, imgFilename=? where id =?', (request.form['clientName'], filename, id))
		else:
			g.db.execute('update client set name=? where id =?', (request.form['clientName'], id))
		g.db.execute('update clientContact set firstName=?, lastName=?, email=?, phone=?, address=? where clientId=?', 
					(request.form['firstName'], request.form['lastName'], request.form['email'], 
						request.form['phone'], request.form['address'], id))
		g.db.commit()
		message = "Dear "+request.form['firstName']+", \nYour portal has been edited."
		send_mail(message)
		return redirect(url_for('portal', id=id))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_portals'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_portals'))

if(__name__) == '__main__':
	app.run()