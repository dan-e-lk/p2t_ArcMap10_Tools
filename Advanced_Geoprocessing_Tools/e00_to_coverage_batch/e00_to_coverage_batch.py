# all e00 files inside the input_e00folder will be converted to coverage files
# if there are folders inside input_e00folder, the script won't look inside it
# because of the character limit of arcpy.ImportFromE00_conversion, the conversion will happen within
	# a temporary folder in C drive



import arcpy
import os, shutil

def main(input_e00folder, output_dir, also_create_gdb):

	# find the e00 files
	e00_list = []
	for root, folders, files in os.walk(input_e00folder):
		for file in files:
			if file.upper().endswith('.E00'):
				e00_list.append(os.path.join(root,file))
				# arcpy.AddMessage(os.path.join(root,file))
		break # this ensures that subfolders are not checked

	# stop if no e00 file found
	if len(e00_list) == 0:
		arcpy.AddError('No e00 file found in your input e00 folder')
	else:
		arcpy.AddMessage("The following e00 files found:")
		for file in e00_list:
			arcpy.AddMessage('\t' + os.path.split(file)[1])
			
	# create a temp folder
	temp_basefolder = r"C:\TEMP"
	temp_foldername = 'e002cov_' + rand_alphanum_gen(3)
	temp_folder = os.path.join(temp_basefolder,temp_foldername)

	temp_cov_dir = os.path.join(temp_folder, 'cov')
	temp_e00_dir = os.path.join(temp_folder, 'e00')
	os.makedirs(temp_cov_dir)
	os.makedirs(temp_e00_dir)

	# create temporary gdb if asked
	if also_create_gdb:
		gdb_name = 'e00_to_gdb.gdb'
		temp_gdb_dir = os.path.join(temp_folder, gdb_name)
		arcpy.CreateFileGDB_management (temp_folder, gdb_name)


	# copy e00 files to a temp folder
	# then start converting!!
	error_msg = ''
	try:
		temp_e00_list = []
		for file in e00_list:
			dst = os.path.join(temp_folder, 'e00', os.path.split(file)[1])
			shutil.copyfile(file, dst)
			temp_e00_list.append(dst)

		# e00 to coverage conversion
		temp_cov_list = [] # fullpath
		arcpy.AddMessage("Converting e00 to coverage...")
		for e00 in temp_e00_list:
			coverage_name = os.path.split(e00)[1][:-4]
			arcpy.ImportFromE00_conversion(Input_interchange_file = e00, Output_folder = temp_cov_dir, Output_name = coverage_name)
			arcpy.AddMessage('\t%s'%coverage_name)
			temp_cov_list.append(os.path.join(temp_cov_dir,coverage_name))

		# coverage to gdb conversion
		if also_create_gdb:
			arcpy.AddMessage("Converting coverage to feature class...")
			for cov in temp_cov_list:
				cov_name = os.path.split(cov)[1]

				# a coverage can be point, arc and/or polygon
				# if a coverage has polygon type then it's definitely polygon but it will also have arc type.
				# but in the case of polygon type you want to just create polygon feature class and not create arc.
				# therefore we loop through polygon, arc, and point in that order and break once we have the type that we need.
				for cov_type in ['polygon','arc','point','no_type']:
					try:
						if cov_type == 'no_type':
							# to trigger this, the coverage is non of the 3 types, which means something went wrong!
							arcpy.AddWarning("Could not convert %s to a feature class!"%cov_name)
						else:
							arcpy.FeatureClassToFeatureClass_conversion(os.path.join(cov,cov_type), temp_gdb_dir, cov_name)
							# if that worked, print and break
							arcpy.AddMessage('\t%s - %s'%(cov_name, cov_type))
							break
					except:
						# if errored out, just continue with the next type until we get one right
						continue


		# copy the coverages over to the output_dir/cov
		output_cov_dir = os.path.join(output_dir, 'cov')
		arcpy.AddMessage("Copying files over from a temp workspace to %s"%output_cov_dir)
		if os.path.isdir(output_cov_dir):
			shutil.rmtree(output_cov_dir)
		shutil.copytree(temp_cov_dir, output_cov_dir)

		# copy the gdb over to the output_dir/e00_to_gdb.gdb
		if also_create_gdb:
			output_gdb_dir = os.path.join(output_dir, gdb_name)
			if os.path.isdir(output_gdb_dir):
				shutil.rmtree(output_gdb_dir)
			shutil.copytree(temp_gdb_dir, output_gdb_dir)


	except Exception as e:
		error_msg += str(e)

	finally:
		# delete the temp folder whether the 'try' successfully run or not
		arcpy.AddMessage("deleting temporary workspace...")
		shutil.rmtree(temp_folder)

		if error_msg != '':
			arcpy.AddWarning("!!There was a problem while running the script:")
			arcpy.AddError(error_msg)


	# open the output folder at the end of the run
	try:
		import webbrowser
		webbrowser.open(output_dir)
	except:
		# nevermind if it didn't work
		pass



def rand_alphanum_gen(length):
	"""
	Generates a random string (with specified length) that consists of A-Z and 0-9.
	"""
	import random, string
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))




if __name__ == '__main__':
	# input_e00folder = r"C:\DanielK_Workspace\temp\MU060_2018_FMP"
	input_e00folder = arcpy.GetParameterAsText(0)
	output_dir = arcpy.GetParameterAsText(1)
	also_create_gdb = arcpy.GetParameterAsText(2)

	if output_dir == '':
		output_dir = input_e00folder
	if also_create_gdb == 'true':
		also_create_gdb = True
	else:
		also_create_gdb = False

	main(input_e00folder, output_dir, also_create_gdb)