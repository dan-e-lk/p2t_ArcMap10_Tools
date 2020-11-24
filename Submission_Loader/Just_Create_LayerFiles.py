
import os, datetime, shutil, traceback, time
debug = True


from Loader.functions import print2, rand_alphanum_gen, get_rid_of_spc_char
import Loader.Apply_layerfile as Apply_layerfile
import Loader.merge_if_same_type as merge_if_same_type


def main(inputFolder,outputFolder,submissionType, filetype, subID, submYear):
	"""
	inputFolder must be a folder that contains e00 or shp, or a gdb folder
	"""

	print2('\n#######   USER INPUTS    ########')
	print2('inputFolder = %s'%inputFolder)
	print2('outputFolder = %s'%outputFolder)
	print2('submissionType = %s'%submissionType)
	print2('filetype = %s'%filetype)
	print2('subID = %s'%subID)
	print2('\n\n')

	# make a output sub-folder using the subID and the submission type
	if len(subID) > 25:	subID = subID[:25]
	output_subfoldername = get_rid_of_spc_char(subID)

	if filetype == 'geodatabase': filetype = 'gdb'
	if filetype == 'shapefile': filetype = 'shp'

	filelist = getFileList(inputFolder, filetype)
	print2(filelist)

	# Prep'ing the new location where the files will be moved to
	outputFolder = os.path.join(outputFolder,output_subfoldername) # for example, ...\SomeFolder\AR-244

	# However, all the work will be done in a temporary location in C drive
	tempFolder = os.path.join('C:\\','Temp\\temp_' + rand_alphanum_gen(8)) # for example, C:\Temp\temp_VV000VDW

	# if the outputFolder directory already exist, do nothing.
	if os.path.isdir(outputFolder):
		print2('\nThe same submission already exists in this folder:\n%s\nTerminating the tool...'%outputFolder,'warning')
		print2('If you need to re-run the sub %s, then you must first delete the folder and try again'%(subID),'warning')
	elif os.path.isdir(tempFolder):
		# this temp folder should never already exist...
		raise Exception('\n%s already exists!'%tempFolder)
	else:
		# try and except to delete all files if something went wrong.
		try:
			# Moving geospatial files
			print2('\nCopying %s to a temporary location: %s ...'%(filetype,tempFolder))
			if filetype == 'gdb':
				for filegdb in filelist:
					filegdbname = os.path.split(filegdb)[1]
					if debug: print2('Copying %s to %s'%(filegdb, os.path.join(tempFolder,'gdb',filegdbname)))
					shutil.copytree(filegdb,os.path.join(tempFolder,'gdb',filegdbname)) # copytree also creates a new directory
			elif filetype == 'shp':
				originalLocation = os.path.split(filelist[0])[0]  #eg. C:\\FIPDownload\\download_cart_2018-01-08\\Product Submission - 23035\\MU898_2018_AWS\\MU898_2018_AWS_LAYERS\\MU898_2018_AWS
				shutil.copytree(originalLocation,os.path.join(tempFolder,'shp'))
			elif filetype == 'e00':
				originalLocation = os.path.split(filelist[0])[0]
				shutil.copytree(originalLocation,os.path.join(tempFolder,'e00'))

			print2("\nCompleted copying all files to %s"%tempFolder)


			if len(filelist) > 0:
				# converting to gdb
				print2("\nCreating '_data' folder and 'FMP_Schema.gdb' ...")
				newgdb_path = convert2GDB(tempFolder,filetype,filelist)
				print2("\nAll data now in a temporary location: %s"%newgdb_path)


				# merge same type of layers. (eg. AOC01, AOC02...)
				print2("\nChecking if any of the fcs needs merging...")
				try:
					merge_if_same_type.main(newgdb_path)
				except:
					print2('WARNING: Merging same type of fcs (such as AOCs or SACs) was unsuccessful.\nThis can happen when trying to merge two or more layers with same field name but different field length or type.', 'warning')

			else: # if len(filelist) == 0
				print2('WARNING: No spatial data found!!!', 'warning')


			# moving the temporary files to the final output location

			print2("\nMoving files from %s\nto\n%s"%(tempFolder,outputFolder))
			shutil.copytree(tempFolder,outputFolder)

			print2('\nCleaning up temporary files...')
			shutil.rmtree(tempFolder)

			# Creating layer files...
			# using try and accept, because it's not mandatory to have layer files.
			print2('\nAttempting to create layer files and apply symbology to all layers...')
			fmuName=''
			fmuCode=''
			try:
				Apply_layerfile.main(submissionType, '2017', outputFolder, subID, fmuName, fmuCode, submYear)
				print2('\nLayer files (with symbology) successfully created!')
			except:
				print2("\nCould not create layer files due to the following error:", 'warning')
				print2(str(traceback.format_exc()), 'warning')


		# Error handling
		except:
			print2('Something went wrong while transferring and converting data...\nRemoving transitory files before terminating...','warning')
			if os.path.exists(outputFolder): shutil.rmtree(outputFolder)
			print2(str(traceback.format_exc()), 'warning')
			print2('\nERROR: The tool could not transfer and convert', 'error')

		finally:
			# making sure the temp folder is cleaned up whether ran into an error or not.
			if os.path.exists(tempFolder): 
				try:
					shutil.rmtree(tempFolder)
				except:
					print2('Failed to delete the temp folder: %s'%tempFolder, 'warning')








def getFileList(inputFolder, dataType):
	""" This tool is based on Loader.identifySubmission.py
		This tool does not convert or move any files around. Instead, the tool examines the input folder 
		and returns either one of the 3:
		1. list of shapefiles in the input folder,
		2. list of e00 files in the input folder,
		3. the input folder itself if the input folder is a file geodatabase workspace.
		An example of inputFolder is "D:\\ACTIVE\\HomeOffice\\MU060_2019_AR_LAYERS\\MU060_2019_AR.gdb" """

	# figuring out the geospatial file type and file names
	shpfileList = []
	e00fileList = []

	if dataType != 'gdb':
		walker = os.walk(inputFolder)
		for foldername, subfolders, filenames in walker:
			for filename in filenames:
				if filename.upper().endswith('.SHP'):
					shpfileList.append(os.path.join(foldername,filename))
				elif filename.upper().endswith('.E00'):
					e00fileList.append(os.path.join(foldername,filename))

	# test if dataType == 'geodatabase', that the folder is actually geodatabase.
	else:
		if arcpy.Describe(inputFolder).dataType != 'Workspace':
			# error out
			raise Exception("Input folder is not a geodatabase")
		else:
			output_list = [inputFolder]

	# check to make sure the output_list is not empty
	if dataType == 'shp':
		if len(shpfileList) == 0:
			raise Exception("Input folder does not contain any shapefile.")
		else:
			output_list = shpfileList
	elif dataType == 'e00':
		if len(e00fileList) == 0:
			raise Exception("Input folder does not contain any e00 files.")		
		else:
			output_list = e00fileList

	return output_list





def convert2GDB(outputFolder,filetype,filelist):
	""" This tool is based on Loader.Convert2GDB.main() function 
	takes the filetype and where they are saved and converts into the standard gdb format in the specified newpath.
	Note that filelist contains a list full path of shpfiles or e00 files or geodatabases (not feature classes).
	An example of outputFolder is C:\FIPDownload\test4\Ogoki\AR\2016\SubID_24671
	filetype must be either gdb, shp or e00.
	This function doesn't care if the submission is AR, AWS or FMP.
	"""

    #GDB path and GDB name identifiers
	newgdbname = 'FMP_Schema'
	newpath = os.path.join(outputFolder,'_data')
	newgdbpath = os.path.join(newpath, newgdbname + '.gdb')

    #Determine if the data folder already exists
	doesFolderExist = os.path.exists(newpath)
	if (not doesFolderExist):
		os.makedirs(newpath)

    #Determine if the gdb already exists
	doesGDBExist = arcpy.Exists(newgdbpath)
	if (doesGDBExist):
        #Delete any existing GDB
		arcpy.Delete_management(newgdbpath)

    #Determine which type of filetype is being submitted (gdb, shp, or e00)
	if filetype == 'gdb':
		if len(filelist) == 1: # if there's only one geodatabase
			# copying the gdb to the ..._data/ folder and renaming the gdb to FMP_Schema.gdb
			if debug: print2("Copying %s to %s" %(filelist[0], newgdbpath))

            #Create a copy of the GDB
			arcpy.Copy_management(filelist[0], newgdbpath)

		elif len(filelist) > 1: # if there are multiple geodatabases found.
			print2('WARNING: More than one geodatabase found.\nAll feature classes should be saved in a single geodatabase','warning')

	elif (filetype == 'e00' or filetype == 'shp'):
		arcpy.CreateFileGDB_management(newpath, newgdbname)

        # e00 requires converting the e00 files to coverages
        # NOTE: e00 will NO longer be valid using ArcGIS Pro (no coverage tools)
		if filetype == 'e00':
			cov_output_path = os.path.join(outputFolder, 'e00')
			cov_path_list = []

			# Converting e00 to coverage
			print2('\nConverting e00 to coverage...')
			for e00 in filelist:

                #Obtain the layer name without the extention. Ex: MU509_SAS00
				coverage_name = os.path.split(e00)[1][:-4]
				print2('\t%s'%coverage_name)

				#Possible issues: limitation on input/output name lengths, < 255 characters, no blank spaces
				# try:
				arcpy.ImportFromE00_conversion(Input_interchange_file = e00, Output_folder = cov_output_path, Output_name = coverage_name)
				# except:
				# 	print2 ('The e00 conversion operation could NOT be completed. Aborting!', 'warning')
				# 	return None

				# determining if the format is polygon, arc, or point
				if (arcpy.Exists(os.path.join(cov_output_path,coverage_name, 'polygon'))):
					cov_path_list.append(os.path.join(cov_output_path,coverage_name, 'polygon'))

				elif (arcpy.Exists(os.path.join(cov_output_path,coverage_name, 'arc'))):
					cov_path_list.append(os.path.join(cov_output_path,coverage_name, 'arc'))

				elif (arcpy.Exists(os.path.join(cov_output_path,coverage_name, 'point'))):
					cov_path_list.append(os.path.join(cov_output_path,coverage_name, 'point'))

				else:
					print2('WARNING: Could not determine the spatial type of %s' %(coverage_name), 'warning')

			if (debug): print2('Cov_path_list:\n%s' %(cov_path_list))

			# moving coverages to gdb using fc to fc tool.
			print2('\nConverting coverage to feature class...')

			for coverage in cov_path_list:
				# Format the coverage name; display name
				newfcname = os.path.split(os.path.split(coverage)[0])[1] # eg. mu415_16ndb00
				print2('\t%s'%newfcname)

				#Convert the object into a feature class
				arcpy.FeatureClassToFeatureClass_conversion(coverage, newgdbpath, newfcname)

		elif (filetype == 'shp'):
			print2('\nConverting shapefile to feature class...')

			for shpfile in filelist:
                # Format the shapefile name; display name
				newfcname = os.path.split(shpfile)[1][:-4] # eg. mu415_16ndb00
				print2('\t%s'%newfcname)

                #Convert the object into a feature class
				arcpy.FeatureClassToFeatureClass_conversion(shpfile, newgdbpath, newfcname)

    # The filetype is unknown, return an error (None)
	else:
		print2 ('Unknown filetype format', 'warning')
        # return None

    #Return the gdb object
	return newgdbpath




if __name__ == '__main__':

	import arcpy
	inputFolder = arcpy.GetParameterAsText(0) # must be a folder that contains e00 or shp, or a gdb folder
	outputFolder = arcpy.GetParameterAsText(1) # the outcome product of this tool will be saved here
	submissionType = arcpy.GetParameterAsText(2) # AR, AWS or FMP (need FMP layers)
	filetype = arcpy.GetParameterAsText(3) # geodatabase, shapefile or e00.
	subID = arcpy.GetParameterAsText(4) # this will turn into the folder name insdie the output folder
	submYear = arcpy.GetParameterAsText(5)

	main(inputFolder,outputFolder,submissionType, filetype, subID, submYear)