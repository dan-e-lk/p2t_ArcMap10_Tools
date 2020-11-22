



def cfg_to_dict(cfg_file):
	r"""
	<notes for for the purose of the function>
	
	Parameters
	----------
	cfg_file : The input file: configparser format

	Returns
	-------
	<return> : <information/description>

	See Also
	--------
	<other information> : <information/description>

	Examples
	--------
	>>> 

	Dependencies (modules)
	------------

	"""
	import configparser
	parser = configparser.ConfigParser()
	parser.read(cfg_file)

	cfg_dict = {section: dict(parser.items(section)) for section in parser.sections()}
	return cfg_dict