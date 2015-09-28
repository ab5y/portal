# all imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
	 abort, render_template, flash
from contextlib import closing

# create application
app = Flask(__name__)

# configuration
DATABASE = os.path.join(app.root_path, 'jll.db')
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def stuff():
	for client in query_db('select * from client'):
		print client[1], 'has the id', client[0]

def make_dicts(cursor, row):
	return dict((cur.description[idx][0], value) for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
	db = connect_db()
	cur = db.execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

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
	cur = g.db.execute('select client.name, clientContact.firstName, clientContact.lastName, clientContact.email from client, clientContact where client.id = clientContact.clientId order by id desc')
	portals = [dict(name=row[0], firstName=row[1], lastName=row[2], email=row[3]) for row in cur.fetchall()]
	return render_template('show_portals.html', portals=portals)

@app.route('/new_portal', methods=['GET', 'POST'])
def new_portal():
	error = None
	if not session.get('logged_in'):
		abort(401)
	if request.method == 'POST':
		g.db.execute('insert into client (name) values (?)',
					 [request.form['clientName']])
		# g.db.commit()
		cur = g.db.execute('select max(id) FROM client')
		clientId = cur.fetchone()[0]
		# clientContact = (request.form['firstName'], request.form['lastName'], request.form['email'], request.form['phone'], request.form['address'], clientId)
		g.db.execute('insert into clientContact values (?, ?, ?, ?, ?, ?)',
					 [request.form['firstName'], request.form['lastName'], request.form['email'], request.form['phone'],
					  request.form['address'], clientId])
		g.db.commit()
		flash('New portal was successfully posted')
		return redirect(url_for('show_portals'))
	return render_template('new_portal.html', error=error)

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