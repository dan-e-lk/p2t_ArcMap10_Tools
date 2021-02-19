
def print2(msg, msgtype = 'normal'):
	""" print and arcmap AddMessage"""
	# print(msg)  # this line was causing the following error: IOError: [Errno 9] Bad file descriptor   python v2 issue???
	try:
		import arcpy
		if msgtype == 'normal':
			arcpy.AddMessage(msg)
		elif msgtype == 'warning':
			arcpy.AddWarning(msg)
		elif msgtype == 'error':
			arcpy.AddError(msg)
	except:
		pass

def rand_alphanum_gen(length):
	"""
	Generates a random string (with specified length) that consists of A-Z and 0-9.
	"""
	import random, string
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))


def get_rid_of_spc_char(input_str):
	import re
	new_str = re.sub('[^A-Za-z0-9-_]+', '', input_str) # all characters not alphanumeric or dash or underscore will be removed
	return new_str


if __name__ == '__main__':
	# import os
	# tempFolder = os.path.join('C:\\','temp_' + rand_alphanum_gen(8))
	# print(tempFolder)

	input_str = 'AR-34-K!23'
	print(get_rid_of_spc_char(input_str))