# this tool is incomplete.

import sys
print(sys.version)

def get_fieldname_n_type(input_fc):
	"""
	all this function does is analyzing the input fc and outputting the fieldnames and file types.
	"""
	pass






def csv_to_sqlite(csvfile, database_name, table_name):
	"""
	turns your feature class or shapefile into a new table in a new or existing sqlite database.
	Note that if the same table already exists, this will replace the old table.
	If the database does not already exist, it will create a new database with the assigned name (eg. 'mydatabase.sqlite')
	"""
	import csv, sqlite3

	csvfile = open(csvfile)
	reader = csv.reader(csvfile)
	fieldnames = reader.next() # a list of field names.

	# the sql script for creating a new table
	create_t_sql = "CREATE TABLE %s "%table_name
	str_fieldnames = '('
	for f in fieldnames:
		str_fieldnames += f + ','
	str_fieldnames = str_fieldnames[:-1] # to remove the trailing comma

	str_fieldnames += ")"
	create_t_sql += str_fieldnames + ";"


	# creating the sql database and table
	con = sqlite3.connect(database_name)
	cur = con.cursor()
	try:
		print("Creating a new table: %s"%table_name)
		# print(create_t_sql)
		cur.execute(create_t_sql)
	except:
		print("Table '%s' already exists. Dropping and recreating the table."%table_name)
		cur.execute("DROP TABLE %s"%table_name)	
		cur.execute(create_t_sql)


	# inserting values
	print("running INSERT statement...")
	insert_sql = "INSERT INTO %s %s"%(table_name, str_fieldnames)
	row_counter = 0
	for row in reader:
		val = str(tuple(row))
		values_sql = " VALUES %s;"%val
		sql = insert_sql + values_sql
		# print(sql)
		cur.execute(sql)
		row_counter += 1
	print("%s rows have been successfully transferred to your sqlite database."%row_counter)

	con.commit()
	con.close()
	csvfile.close()



if __name__ == '__main__':

	# csvfile = r'\\lrcpsoprfp00001\MNR_NER\FISH_MGMT\Reference\StockingMaps\Workspace\FishStocking_AllNER_withPop.csv'
	# table_name = 'fishstocking'
	# database_name = 'myfish_sqlite.sqlite'

	# csv_to_sqlite(csvfile, database_name, table_name)


