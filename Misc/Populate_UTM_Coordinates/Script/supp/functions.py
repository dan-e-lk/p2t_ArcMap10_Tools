
def rand_alphanum_gen(length):
	"""
	Generates a random string (with specified length) that consists of A-Z and 0-9.
	"""
	import random, string
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

# when you have a information like below:
# PROJCS["GCS North American 1983 UTM Zone 16U (Calculated)",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-87.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]
# codeblock function can be used within arcmap's "field calculation" to pick out the UTM zone.
codeblock = """
def f(i):
  start = i.find('UTM')
  start = start + 9
  end = start + 2
  return i[start:end]
"""


if __name__ == '__main__':
	import os
	tempFolder = os.path.join('C:\\','temp_' + rand_alphanum_gen(8))
	print(tempFolder)