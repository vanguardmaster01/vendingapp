import sqlite3
import datetime
import os
import sys
# import db
script_dir = os.path.dirname( __file__ )
constants_dir = os.path.join( script_dir, '..', 'config' )
sys.path.append(constants_dir)
import utils

class Ad:
    def __init__(self, id, type, content):
        self.id = id
        self.type = type
        self.content = content
		
# convert image to blob data
def convert_to_blod_data(filename):
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData		

def update_product(id, image, price):
	try:
		conn = sqlite3.connect('./sql.db')
		cursor = conn.cursor()

		update_query = '''update products set thumbnail = ?, price = ? where id = ?'''
		imageBlob = utils.convert_to_blod_data(image)
		params = (imageBlob, price, id)
		cursor.execute(update_query, params)
		
		conn.commit()
		cursor.close()

	except sqlite3.Error as error:
		print('update_product_fail', error)
	finally:
		if conn:
			conn.close()
			print('db connection is closed')
			
# insert into product table
def insert_product(product):
	try:
		conn = sqlite3.connect('./sql.db')
		cursor = conn.cursor()

		insert_query = """insert into products (itemno, name, thumbnail, nicotine, batterypack, tankvolumn, price, currency, caution)
							values (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
		imageBlob = utils.convert_to_blod_data(product.thumbnail)
		data = (product.itemno, product.name, (imageBlob), product.nicotine, product.batterypack, product.tankvolumn, product.price, product.currency, product.caution)
		cursor.execute(insert_query, data)
		
		print("inserted successfully")
		
		conn.commit()
		cursor.close()

		return True
	except sqlite3.Error as error:
		print('insert_prodcut_fail', error)
		return False
	finally:
		if conn:
			conn.close()
			print('db connection is closed')
		return False

def insert_ads(ad):
	try:
		conn = sqlite3.connect('./sql.db')
		cursor = conn.cursor()

		insert_query = """insert into ads (type, content)
							values (?, ?)"""
		blodData = convert_to_blod_data(ad.content)
		print(blodData)
		data = (ad.type, (blodData))
		
		cursor.execute(insert_query, data)
		
		print("inserted ad successfully")
		
		conn.commit()
		cursor.close()

		return True
	except sqlite3.Error as error:
		print('insert_ad_fail', error)
		return False
	finally:
		if conn:
			conn.close()
			print('db connection is closed')
		return False
