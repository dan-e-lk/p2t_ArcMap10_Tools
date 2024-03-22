version = '0.1'
# This script should replace the old block stratification walk-through document
# Input = EST or FTG layer of AR
# Output = Polygons with the same SPCOMP and STKG, AND are nearby each other are merged


import arcpy
import os

def main(input_fc,output_fc,aggr_dist):

	arcpy.AddMessage("version v%s"%version)

	# checking minimum requirements to run this tool
	mand_fields = ['SPCOMP','STKG']
	# other mandatory fields include either (FTGFU or ESTFU) and (FTG or ESTIND)
	estfu_field = '' # this will be either FTGFU or ESTFU
	estind_field = '' # this will be either FTG or ESTIND

	# get fieldnames
	arcpy.AddMessage("Verifying fields...")
	fields = [str(f.name).upper() for f in arcpy.ListFields(input_fc)]
	arcpy.AddMessage("Fields found: %s\n"%fields)

	# checking mand_fields
	fields_all_good = True
	if set(mand_fields) <= set(fields):
		arcpy.AddMessage("Mandatory fields %s Exists!"%mand_fields)
	else:
		fields_all_good = False		
	if 'FTGFU' in fields or 'ESTFU' in fields:
		if 'FTGFU' in fields: estfu_field = 'FTGFU'
		if 'ESTFU' in fields: estfu_field = 'ESTFU'
	else:
		fields_all_good = False
	if 'FTG' in fields or 'ESTIND' in fields:
		if 'FTG' in fields: estind_field = 'FTG'
		if 'ESTIND' in fields: estind_field = 'ESTIND'
	else:
		fields_all_good = False
	if fields_all_good:
		arcpy.AddMessage("All mandatory fields are found.")
		mand_fields.append(estfu_field)
	else:
		arcpy.AddError("There some missing mandatory field. You need at least SPCOMP, STKG, (FTGFU or ESTFU) and (FTG or ESTIND) fields to continue.")

	# create temporary space to work on
	arcpy.AddMessage("Creating temporary workspace...")
	temp_foldername = r"C:\Temp\temp" + rand_alphanum_gen(4)
	temp_gdb = 'rap_stratif_temp.gdb'
	temp_gdb_fullpath = os.path.join(temp_foldername, temp_gdb)
	os.mkdir(temp_foldername)

	# try, except and finally - to ensure deleting the temporary workspace even if the script fails
	try:
		arcpy.CreateFileGDB_management(temp_foldername, temp_gdb)
		temp_path = os.path.join(temp_foldername, temp_gdb)
		# set the temp workspace as the environment
		arcpy.env.workspace = temp_path

		arcpy.AddMessage("\n######   STEP 1   ###################################")
		arcpy.AddMessage("Selecting and exporting %s='Y' as FTGy"%estind_field)
		arcpy.conversion.FeatureClassToFeatureClass(input_fc, temp_path, 'FTGy', "%s='Y'"%estind_field)


		arcpy.AddMessage("\n######   STEP 2   ###################################")
		arcpy.AddMessage("Defining forest block patches using Aggregate Polygons tool...")
		arcpy.AggregatePolygons_cartography('FTGy', 'FTGy_Aggr', "%s Meters"%aggr_dist)
		# create Aggr_ID field
		arcpy.AddMessage("Populating patch IDs in AGGR_ID field...")
		arcpy.management.AddField('FTGy_Aggr','AGGR_ID', 'LONG')
		arcpy.management.CalculateField('FTGy_Aggr','AGGR_ID', "!OBJECTID!", "PYTHON_9.3")


		arcpy.AddMessage("\n######   STEP 3   ###################################")
		arcpy.AddMessage("Spatial Joining the AGGR_ID to the FTGy layer")
		arcpy.SpatialJoin_analysis(target_features="FTGy", join_features="FTGy_Aggr", out_feature_class="FTGy_Aggr_SpJoin", join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", match_option="INTERSECT")


		arcpy.AddMessage("\n######   STEP 4   ###################################")
		mand_fields.append('AGGR_ID')
		arcpy.AddMessage("Dissolving the FTGy_Aggr_SpJoin layer using these fields: %s"%mand_fields)
		arcpy.Dissolve_management('FTGy_Aggr_SpJoin', output_fc, mand_fields, "", "MULTI_PART")

		arcpy.AddMessage("\n######  SUCCESS!  ###################################")

	except Exception:
		arcpy.AddError(traceback.format_exc())

	finally:
		arcpy.AddMessage("Deleting temporary workspace...")
		try:
			arcpy.Delete_management(temp_gdb_fullpath)
			shutil.rmtree(temp_foldername)
			arcpy.AddMessage("temporary workspace deleted")
		except:
			arcpy.AddWarning("temporary workspace was not deleted. Location of the temp workspace:\n%s"%temp_foldername)




def rand_alphanum_gen(length):
	"""
	Generates a random string (with specified length) that consists of A-Z and 0-9.
	"""
	import random, string
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))



if __name__ == '__main__':
	input_fc = arcpy.GetParameterAsText(0) # this should be AR's FTG or EST file in fc format
	output_fc = arcpy.GetParameterAsText(1) # output feature class
	# aggr_dist = arcpy.GetParameterAsText(2) # if two or more polygons are less than aggr_dist apart, they are considered one patch. eg. 100
	aggr_dist = 100 # I am just gonna hard code this one.

	main(input_fc,output_fc,aggr_dist)
