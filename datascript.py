import os
from openpyxl import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.compat import range
from openpyxl.cell import get_column_letter
from jllPortal import init_db
from array import *
import sqlite3

# configuration
DATA_FOLDER = os.path.join(os.getcwd(), 'data')
DATABASE = os.path.join(os.getcwd(), 'jll.db')

def connect_db():
	return sqlite3.connect(DATABASE)

def get_filepath(filename):
	return os.path.join(DATA_FOLDER, filename)

conn = connect_db()
cur = conn.cursor()

init_db()

ids = array('i')

wb_ro = load_workbook(filename = get_filepath('Company.xlsx'), read_only=True)
ws_ro = wb_ro['Sheet1']

wb_wo = load_workbook(filename=get_filepath('CompanyContact.xlsx'))
ws_wo = wb_wo['Sheet1']

for row in ws_ro.rows:
	if row[0].value != 'name':
		cur.execute('insert into client (name, imgFilename, industry) values (?, ?, ?)',
					(row[0].value, row[1].value, row[2].value))
		cur.execute('select max(id) FROM client')
		clientId = cur.fetchone()[0]
		ids.append(clientId)
		print "Created client with id ", clientId

for i, id in enumerate(ids):
	ws_wo.cell(row=i+2, column=6).value = id
wb_wo.save(get_filepath('CompanyContact.xlsx'))

for row in ws_wo.rows:
	if row[0].value != 'firstName':
		cur.execute('insert into clientContact (firstName, lastName, email, phone, address, clientId) values (?,?,?,?,?,?)',
					(row[0].value, row[1].value, row[2].value, row[3].value, row[4].value, row[5].value))

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

# for client in query_db('select * from property'):
	# 	print client[1], 'has the id', client[0]
	# g.db.execute('insert into property (name, imagepath, address, description) values (?, ?, ?, ?)',
	# 				(	'Empire State Building', 
	# 					'/static/Images/Realty/Empire_State_Building.jpg', 
	# 					'350 5th Ave, New York, NY 10118, United States', 
	# 					'The Empire State Building is a 102-story skyscraper located in Midtown Manhattan, New York City, on Fifth Avenue between West 33rd and 34th Streets.'
	# 				)
	# 			)
	# g.db.execute('insert into property (name, imagepath, address, description) values (?, ?, ?, ?)',
	# 				(	'John Hancock Center', 
	# 					'/static/Images/Realty/John_Hancock_Center_2.jpg', 
	# 					'875 North Michigan Avenue, Chicago, Illinois, United States', 
	# 					'The John Hancock Center is a 100-story, 1,127-foot (344 m) tall skyscraper at 875 North Michigan Avenue, Chicago, Illinois, United States.'
	# 				)
	# 			)
	# g.db.commit()
	# for prop in query_db('select * from property'):
	# 	print prop[1], 'has the id', prop[0]
	# cur = g.db.execute('select * from client')
	# clients = [make_dicts(cur, row) for row in cur.fetchall()]
	# cur = g.db.execute('select * from property') 
	# properties = [make_dicts(cur, row) for row in cur.fetchall()]
	# for client in clients:
	# 	for prop in properties:
	# 		g.db.execute('insert into client_property values (?, ?, ?, ?, ?)',
	# 						(client['id'], prop['id'], 'null', 'null', 0))
	# g.db.commit()