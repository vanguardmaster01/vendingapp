import sqlite3
import datetime
# from config import utils
import os
import threading
from dotenv import load_dotenv
load_dotenv()
# import os
# import sys

# script_dir = os.path.dirname( __file__ )
# urils_dir = os.path.join( script_dir, '..', 'config' )
# sys.path.append(urils_dir)
# import utils

from model.Product import Product
from model.Ad import Ad
from model.Machine import Machine

dbPath = os.environ.get('dbPath')




#lock = threading.Lock()
conn = None

def openDatabase():
	try:
		global conn
		print("opening")
		conn = sqlite3.connect(dbPath)
		# Mape value from SQLite's THREADSAFE to Python's DBAPI 2.0
		# threadsafety attribute.
		sqlite_threadsafe2python_dbapi = {0: 0, 2: 1, 1: 3}
		#conn = sqlite3.connect(dbPath)
		threadsafety = conn.execute(
					"""
			select * from pragma_compile_options
			where compile_options like 'THREADSAFE=%'
			"""
				).fetchone()[0]
		print(threadsafety)
		conn.close()

		threadsafety_value = int(threadsafety.split("=")[1])

		if sqlite_threadsafe2python_dbapi[threadsafety_value] == 3:
			check_same_thread = False
		else:
			check_same_thread = True

		conn = sqlite3.connect(dbPath, check_same_thread=check_same_thread)

		print("ok", conn)

		return True
	except sqlite3.Error as error:
		print('db connection error', error)

	return False

def closeDatabase():
	try:
		global conn
		if conn:
			conn.close()
	except sqlite3.Error as error:
		print('db closing error', error)

def insert_ads(ad):
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		insert_query = """insert into ads (type, content)
							values (?, ?)"""

		# blodData = utils.convert_to_blod_data(ad.content)
		data = (ad.type, ad.content)
		
		cursor.execute(insert_query, data)
		
		print("inserted ad successfully")
		
		conn.commit()
		cursor.close()
		return True

	except sqlite3.Error as error:
		print('insert_ad_fail', error)
		return False
	finally:
		#if conn:
			#conn.close()
		print('insert_ad_connection is closed')

def insert_machine(machine):
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		insert_query = """insert into machines (name, unit, value, thumbnail)
							values (?, ?, ?, ?)"""
		
		# blodData = utils.convert_to_blod_data(machine.thumbnail)
		data = (machine.name, machine.unit, machine.value, machine.thumbnail)
		
		cursor.execute(insert_query, data)
		
		print("inserted machine successfully")
		
		conn.commit()
		cursor.close()
		return True

	except sqlite3.Error as error:
		print('insert_machine_fail', error)
		return False
	finally:
		print('insert_machine_connection is closed')


# insert into product table
def insert_product(product):
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		insert_query = """insert into products (itemno, name, thumbnail, nicotine, batterypack, tankvolumn, price, currency, caution, stock)
							values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
		# imageBlob = utils.convert_to_blod_data(product.thumbnail)
		data = (product.itemno, product.name, product.thumbnail, product.nicotine, product.batterypack, 
		product.tankvolumn, product.price, product.currency, product.caution, product.stock)
		cursor.execute(insert_query, data)
		
		print("inserted product successfully")
		
		conn.commit()
		cursor.close()
		return True

	except sqlite3.Error as error:
		print('insert_prodcut_fail', error)
		return False
	finally:
		print('insert_prodcut_connection is closed')

# update product item
def update_product(id, image, price):
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		update_query = '''update products set thumbnail = ?, price = ? where id = ?'''
		# imageBlob = utils.convert_to_blod_data(image)
		params = (image, price, id)
		cursor.execute(update_query, params)
		
		conn.commit()
		cursor.close()
		return True

	except sqlite3.Error as error:
		print('update_product_fail', error)
		return False
	finally:
		print('update_prodcut_connection is closed')

# get all products
def get_products():
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		select_query = '''select * from products order by itemno'''
		cursor.execute(select_query)
		records = cursor.fetchall()

		products = []
		for record in records:
			product = convert_to_product(record)
			products.append(product)

		#conn.commit()
		cursor.close()
		return products

	except sqlite3.Error as error:
		print('get_prodcuts_fail', error)
		return []
	finally:
		print('db get_prodcuts_connection is closed')


# get product
def get_product(itemno):
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		select_query = '''select * from products where itemno = ?'''
		cursor.execute(select_query, (itemno,))
		record = cursor.fetchone()
		
		product = None
		if record:
			product = convert_to_product(record)

		#conn.commit()
		cursor.close()

		return product

	except sqlite3.Error as error:
		print('get_prodcut_fail', error)
		return None
	finally:
		print('get_product_connection is closed')

# get Ad
def get_ad():
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		select_query = '''select * from ads'''
		cursor.execute(select_query)
		record = cursor.fetchone()

		ad = None
		if record:
			ad = convert_to_ad(record)

		#conn.commit()
		cursor.close()
		return ad

	except sqlite3.Error as error:
		print('get_ad_fail', error)
		return None
	finally:
		print('get_ad_connection is closed')

# get Ad
def get_ad_row(id):
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		select_query = '''select * from ads where id = ?'''
		cursor.execute(select_query, (id,))
		record = cursor.fetchone()

		ad = None
		if record:
			ad = convert_to_ad(record)

		#conn.commit()
		cursor.close()
		return ad

	except sqlite3.Error as error:
		print('get_ad_fail', error)
		return None
	finally:
		print('get_ad_row_connection is closed')


# get Ad
def get_machines():
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		select_query = '''select * from machines order by name'''
		cursor.execute(select_query)
		record = cursor.fetchall()
		
		machines = []
		for item in record:
			machine = convert_to_machine(item)
			machines.append(machine)

		#conn.commit()
		cursor.close()
		return machines

	except sqlite3.Error as error:
		print('get_machine_fail', error)
		return []
	finally:
		print('db get_machine_connection is closed')

def get_product_count():
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		select_query = '''select count(id) from products '''
		cursor.execute(select_query)
		record = cursor.fetchone()
		
		cnt = 0
		if record:
			cnt = record[0]

		#conn.commit()
		cursor.close()

		return cnt

	except sqlite3.Error as error:
		print('fail', error)
		return None
	finally:
		print('get_prodcut_count_connection is closed')

# delete Machines
def delete_machines():
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		delete_query = '''delete from machines'''
		cursor.execute(delete_query)
		
		conn.commit()
		cursor.close()
		return True

	except sqlite3.Error as error:
		print('delete_machine_fail', error)
		return False
	finally:
		print('delet_machines_connection is closed')

# delete Ads
def delete_ads():
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		delete_query = '''delete from ads'''
		cursor.execute(delete_query)
		
		conn.commit()
		cursor.close()
		return True

	except sqlite3.Error as error:
		print('delete_ads_fail', error)
		return False
	finally:
		print('delete_ads_connection is closed')

# delete Ads
def delete_products():
	
	try:
		global conn
		#conn = sqlite3.connect(dbPath)
		cursor = conn.cursor()

		delete_query = '''delete from products'''
		cursor.execute(delete_query)
		
		conn.commit()
		cursor.close()
		return True

	except sqlite3.Error as error:
		print('delete_products_fail', error)
		return False
	finally:
		print('delte_produts_connection is closed')

def convert_to_product(record):
	product = Product(record[0], record[1], record[2], record[3], record[4], 
				   record[5], record[6], record[7], record[8], record[9], record[10])

	return product

def convert_to_ad(record):
	ad = Ad(record[0], record[1], record[2])
	return ad
	
def convert_to_machine(record):
	machine = Machine(record[0], record[1], record[2], record[3], record[4])
	return machine
