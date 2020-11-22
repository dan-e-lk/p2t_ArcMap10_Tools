# ----------------------------
#
#
#
#
# ----------------------------

import os, shutil, arcpy
from functions import print2
import zipfile

#Provide the user with additional feedback when debugging the script
debug = False

#Determine if an object exists and create/update object such as a folder or GDB
##def doesObjectExist(path, objType, objName = None, deleteObj):
##    #Evaluate folders using the OS module
##    if (objType == 'Folder'):
##        #The folder exists
##    	if (os.path.exists(path)):
##            #The folder should be deleted, thus create a new folder
##            if (deleteObj):
##                os.rmdir(path)
##                os.makedirs(newpath)
##        #The folder doesn't exist, create a new folder
##        else:
##            os.makedirs(newpath)
##
##    #Evaluate GDBs using arcpy
##    elif (objType == 'gdb'):
##        #The GDB exists
##        if (arcpy.Exists(path)):
##            #The GDB should be deleted, thus create a new GDB
##            if (deleteObj):
##                arcpy.Delete_management(path)
##                arcpy.CreateFileGDB_management(path, objName)
##        #The GDB doesn't exist, create a new GDB
##        else:
##            arcpy.CreateFileGDB_management(path, objName)


def main(outputFolder,filetype,filelist):
	""" This Convert2GDB.main() function takes the filetype and where they are saved
	and converts into the standard gdb format in the specified newpath.
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
				try:
					arcpy.ImportFromE00_conversion(Input_interchange_file = e00, Output_folder = cov_output_path, Output_name = coverage_name)
				except:
					print2 ('The e00 conversion operation could NOT be completed. Aborting!', 'warning')
					return None

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
        return None

    #Return the gdb object
	return str(newgdbpath)


# -----------------------


if __name__ == '__main__':

	outputFolder = r'C:\FIPDownload'
	arcpy.env.workspace = outputFolder
	filetype = 'e00'
	fc_list = [r'C:\FIPDownload\download_cart_2019-02-25Nipissing\ProductSubmission-25284\MU754_2019_AWS\MU754_2019_AWS_LAYERS\MU754_2019_AWS\mu754_19agp00.e00',
		r'C:\FIPDownload\download_cart_2019-02-25Nipissing\ProductSubmission-25284\MU754_2019_AWS\MU754_2019_AWS_LAYERS\MU754_2019_AWS\mu754_19sac01.e00']

	#main(outputFolder,filetype,fc_list)


#END OF FILE

