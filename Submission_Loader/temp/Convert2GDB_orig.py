debug = False
import arcpy
import os, shutil
from functions import print2


def main(outputFolder,filetype,filelist):
	""" This Convert2GDB.main() function takes the filetype and where they are saved
		and converts into the standard gdb format in the specified newpath.
		Note that filelist contains a list full path of shpfiles or e00 files or geodatabases (not feature classes).
		An example of outputFolder is C:\FIPDownload\test4\Ogoki\AR\2016\SubID_24671
		filetype must be either gdb, shp or e00.
		This function doesn't care if the submission is AR, AWS or FMP.
		"""

	newpath = os.path.join(outputFolder,'_data')
	newgdbname = 'FMP_Schema'
	newgdbpath = os.path.join(newpath, newgdbname + '.gdb')

	if filetype == 'gdb':
		if len(filelist) == 1: # if there's only one geodatabase
			# copying the gdb to the ..._data/ folder and renaming the gdb to FMP_Schema.gdb
			if debug: print2("Copying %s to %s"%(filelist[0], newgdbpath))
			os.makedirs(newpath)
			arcpy.Copy_management(filelist[0], newgdbpath)


		elif len(filelist) > 1: # if there are multiple geodatabases found.
			print2('WARNING: More than one geodatabase found.\nAll feature classes should be saved in a single geodatabase','warning')

	elif filetype in ['e00','shp']:
		os.makedirs(newpath)
		arcpy.CreateFileGDB_management(newpath, newgdbname)
		
		if filetype == 'e00':
			cov_output_path = os.path.join(outputFolder,'e00')
			cov_path_list = []
			
			# Converting e00 to coverage
			print2('\nConverting e00 to coverage...')		
			for e00 in filelist:
				coverage_name = os.path.split(e00)[1][:-4]
				print2('\t%s'%coverage_name)
				arcpy.ImportFromE00_conversion(Input_interchange_file = e00, Output_folder = cov_output_path, Output_name = coverage_name)

				# determining if the format is polygon, arc or point
				if arcpy.Exists(os.path.join(cov_output_path,coverage_name,'polygon')):
					cov_path_list.append(os.path.join(cov_output_path,coverage_name,'polygon'))
				elif arcpy.Exists(os.path.join(cov_output_path,coverage_name,'arc')):
					cov_path_list.append(os.path.join(cov_output_path,coverage_name,'arc'))
				elif arcpy.Exists(os.path.join(cov_output_path,coverage_name,'point')):
					cov_path_list.append(os.path.join(cov_output_path,coverage_name,'point'))
				else:
					print2('WARNING: Could not determine the spatial type of %s'%coverage_name,'warning')
			if debug: print2('Cov_path_list:\n%s'%cov_path_list)

			# moving coverages to gdb using fc to fc tool.
			print2('\nConverting coverage to feature class...')
			for coverage in cov_path_list:
				newfcname = os.path.split(os.path.split(coverage)[0])[1] # eg. mu415_16ndb00
				print2('\t%s'%newfcname)
				arcpy.FeatureClassToFeatureClass_conversion(coverage,newgdbpath,newfcname)

		elif filetype == 'shp':
			print2('\nConverting shapefile to feature class...')
			for shpfile in filelist:
				newfcname = os.path.split(shpfile)[1][:-4] # eg. mu415_16ndb00
				print2('\t%s'%newfcname)
				arcpy.FeatureClassToFeatureClass_conversion(shpfile,newgdbpath,newfcname)

	return str(newgdbpath)


if __name__ == '__main__':
	outputFolder = r'C:\FIPDownload\SubID_24671'
	filetype = 'shp'
	filelist = [r'C:\FIPDownload\SubID_24671\shp\mu415_16ftg00.shp',
				r'C:\FIPDownload\SubID_24671\shp\mu415_16hrv00.shp',
				r'C:\FIPDownload\SubID_24671\shp\mu415_16ndb00.shp',
				r'C:\FIPDownload\SubID_24671\shp\mu415_16rds00.shp',
				r'C:\FIPDownload\SubID_24671\shp\mu415_16wtx00.shp',
				]

	main(outputFolder,filetype,filelist)