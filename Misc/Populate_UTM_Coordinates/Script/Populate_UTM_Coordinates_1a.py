
version = '1a'

###########################################################################
#
#							Populate UTM Coordinates
#
# Purpose:
# This tool is intended for Ontario MNRF internal use only.
# Use this tool to populate UTM coordinates 
#
# Requirement:
# ArcMap version 10.0+ installed
# If the user has ArcMap 10.0 - 10.2, the tool will work but will not rename the field to Easting and Northing (it will appear as point_x and point_y)
#
# Notes:
# 
#
# Workflow:
# 1. make a copy of the input data
# 2. Create a new temporary field - UTM_Info (text 500)
# 3. Create a new permanent field - UTM_Zone
# 4. Run Calculate UTM Zone which will populate UTM zone info in the UTM_Info field.
# 5. Populate UTM_Zone field with the information from above.
# 6. Check all records in case an invalid UTM Zone was populated. Notify the user if any error found.
# 7. Make a temporary feature layer.
# 8. For each zone in [15,16,17,18], set the arcpy environment of the output coordinate system to each zone and run AddGeometryAttributes_management tool to populate the Easting and Northing.
# 9. Rename the x and y fields to easting and northing fields.
# 10. Create a log file if that was the user's choice.
#
#
# Assumptions: All points are in Ontario
# 
#
# Limitations: Only works on UTM Z15 - 18 North.
#			   Only works on point and polygon feature classes or shapefiles. Not for lines.
#
# Created: 2019/05/24
#
# Last Edited: 2019/06/03
#
# Contact: daniel.kim2@ontario.ca 
#
#   # # # Ontario Ministry of Natural Resources and Forestry 2019 # # #
#
###########################################################################


import os, datetime, shutil, traceback, time
import supp.functions
from supp.functions import rand_alphanum_gen
import supp.arclog as arclog


def main(input_fc,output_fc, create_logfile, logfile_folder):
	"""
	input_fc is the input shapefile or feature class where you want the UTM coordinates to be populated
	create_logfile should be either True or False
	logfile_folder is a name of an existing folder where the logfile will be created and saved at.
	"""

	l = arclog.log('DEBUG', disp_time_n_lvl = False)
	l.logger('Tool version = %s'%version)
	l.logger('\nInput data = %s'%input_fc)
	l.logger('Output fc = %s'%output_fc)
	l.logger('Create Log file = %s'%create_logfile)
	l.logger('Log File Folder = %s'%logfile_folder)

	output_gdb = os.path.split(output_fc)[0]
	if output_gdb.upper().endswith('.GDB'):
		arcpy.env.workspace = output_gdb
	else:
		raise Exception("The output feature class must be within a file geodatabase (not in a feature dataset).")

	# Checking the geometry shape type
	desc = arcpy.Describe(input_fc)
	shape_type = desc.shapeType # This can be either Polygon, Polyline, Point, Multipoint or MultiPatch
	l.logger("\nShapetype = %s"%shape_type)
	if shape_type not in ['Polygon', 'Point']:
		l.logger("Your input data's shapetype is %s"%shape_type, 'CRITICAL')
		l.logger("This tool only works on shapetype = Polygon or Point", 'CRITICAL')

	# copying the original data. the new name is the same as the original name plus "UTMCoord"
	l.logger('\nExporting the input to the output gdb...')
	output_fc_name = os.path.split(output_fc)[1]
	try:
		arcpy.FeatureClassToFeatureClass_conversion(input_fc, output_gdb, output_fc_name)
	except:
		# in case the same name already exists
		rand_char3 = rand_alphanum_gen(3)
		output_fc_name = output_fc_name + '_' + rand_char3
		arcpy.FeatureClassToFeatureClass_conversion(input_fc, output_gdb, output_fc_name)
	output_full_path = os.path.join(output_gdb,output_fc_name)

	# create a new field UTM_Info (text 500) and UTM_Zone
	l.logger('\nAdding Fields...')
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(output_fc_name)]
	if "UTM_INFO" not in existingFields:
		arcpy.AddField_management(output_fc_name,"UTM_INFO", "TEXT", field_length=500)
	else:
		l.logger("UMT_INFO field exists already.",'WARNING')
	if "UTM_ZONE" not in existingFields:
		arcpy.AddField_management(output_fc_name,"UTM_ZONE", "SHORT")
	else:
		l.logger("UTM_ZONE field exists already.",'WARNING')

	# running Calculate UTM Zone tool to populate the appropriate UTM projection of each record
	l.logger("\nRunning Calculate UTM Zone tool to populate the appropriate UTM projection of each record...")
	arcpy.CalculateUTMZone_cartography(output_fc_name, "UTM_INFO")

	# calculating the UTM_Zone
	l.logger("\nCalculating the UTM Zone...")
	arcpy.CalculateField_management(in_table=output_fc_name, field="UTM_Zone", expression="f(!UTM_INFO!)", expression_type="PYTHON_9.3", code_block=supp.functions.codeblock)

	# Check the UTM Zones. Inform the user if there are any nulls.
	l.logger("\nChecking if there's an invalid UTM Zone...")
	list_of_zones = []
	list_of_errors = []
	with arcpy.da.SearchCursor(output_fc_name, ['OBJECTID','UTM_ZONE']) as cursor:
		for row in cursor:
			zone_num = row[1]
			list_of_zones.append(zone_num)
			if zone_num not in [15,16,17,18]:
				err_msg = 'Error on OBJECTID %s: UTM_ZONE = %s. It should be between 15 and 18.'%(row[0],zone_num)
				list_of_errors.append(err_msg)

	# a printout of the errors and summary
	num_of_errors = len(list_of_errors)
	max_print_num = 10
	if num_of_errors > 0:
		if num_of_errors <= max_print_num:
			for error in list_of_errors:
				l.logger(error,'WARNING')
		else:
			for i in max_print_num:
				l.logger(list_of_errors[i],'WARNING')
			l.logger('... and %s other zone number errors were found.'%(num_of_errors-max_print_num),'WARNING')
		l.logger("Note that it's the OBJECTID of the newly created feature class (%s) and not the original input file."%output_fc_name,'WARNING')
	else:
		l.logger("No error found.")

	l.logger('\nSummary of Zones:')
	set_of_zones = set(list_of_zones)
	zone_counts = {zone:list_of_zones.count(zone) for zone in set_of_zones} # this will give {17: 220, 16: 99, None: 3}
	for k, v in zone_counts.items():
		if k in [15,16,17,18]:
			l.logger('Zone %s: %s records'%(k,v))
		else:
			l.logger('Zone %s: %s records <-- Check these records!'%(k,v),'WARNING')

	# Populating centroid Easting and Northing based on the coordinate system.
	l.logger('\nPopulating Easting and Northing...')
	arcpy.MakeFeatureLayer_management(output_fc_name, "temp_layer")

	set_of_possible_zones = {15,16,17,18}
	for zone in set_of_zones&set_of_possible_zones: # the intersect of two sets
		arcpy.SelectLayerByAttribute_management("temp_layer","NEW_SELECTION", '"UTM_ZONE" = %s'%zone)
		geo_property = 'POINT_X_Y_Z_M' if shape_type == 'Point' else 'CENTROID_INSIDE'
		length_unit = 'METERS'
		arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 UTM Zone %sN"%zone)
		arcpy.AddGeometryAttributes_management("temp_layer", geo_property)

	arcpy.SelectLayerByAttribute_management("temp_layer","CLEAR_SELECTION")

	# Cleaning up...
	l.logger('\nDeleting temporary fields...')
	arcpy.DeleteField_management(output_fc_name, "UTM_INFO")

	# Rename fields (only works on ArcMap v10.3 or greater)
	try:
		if shape_type == 'Point':
			arcpy.AlterField_management(output_fc_name, "POINT_X", "Easting_X")
			arcpy.AlterField_management(output_fc_name, "POINT_Y", "Northing_Y")
		else:
			arcpy.AlterField_management(output_fc_name, "INSIDE_X", "Inside_Centroid_Easting_X")
			arcpy.AlterField_management(output_fc_name, "INSIDE_Y", "Inside_Centroid_Northing_Y")
	except:
		pass

	l.logger("\nLocation of the final output:\n%s\n"%output_full_path)

	# Creating logfile
	try:
		if create_logfile:
			arcpy.AddMessage("Writing logfile...")
			import datetime
			datetime_now = datetime.datetime.now().strftime('%y%m%d_%H%M%S_%f')[:-5] # eg. '190531_144113_6'
			logfile_name = "PopulateUTM_" + datetime_now + ".txt"
			logfile_path = os.path.join(logfile_folder,logfile_name)
			log = open(logfile_path,'w')
			log.write(l.all_msg)
			log.close()
			arcpy.AddMessage("Logfile created:\n%s\n\n"%logfile_path)
	except:
		arcpy.AddWarning("\nUnable to write the logfile for some reason...")






if __name__ == '__main__':

	import arcpy

	input_data = arcpy.GetParameterAsText(0)
	output_fc = arcpy.GetParameterAsText(1)
	create_logfile_y_n = str(arcpy.GetParameterAsText(2))
	logfile_folder = arcpy.GetParameterAsText(3)

	create_logfile_y_n = True if create_logfile_y_n == 'true' else False

	main(input_data, output_fc, create_logfile_y_n, logfile_folder)

	# input_data = r'C:\DanielK_Workspace\test_data\All_NER_testdata.gdb\All_NER_BMI_pick10k'
	# output_gdb = r'C:\DanielK_Workspace\test_data\All_NER_testdata.gdb'
	# main(input_data, output_gdb)

