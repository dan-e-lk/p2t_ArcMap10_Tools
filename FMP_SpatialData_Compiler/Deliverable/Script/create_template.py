# This script is originally a part of the FMP_SpatialData_Compiler tool

import os, datetime

print('importing arcpy...')
import arcpy

def print2(msg, msgtype = 'msg'):
	# print(msg)
	if msgtype == 'msg':
		arcpy.AddMessage(msg)
	elif msgtype == 'warning':
		arcpy.AddWarning(msg)




def create_template(outputgdb, unique_suffix, inv_class):
	""" Creates new polygon feature classes in the path outputgdb (must already have the gdb created) 
		with the fields described in fields dictionary
		It creates 2 empty FCs. One with all-text fields and one with actual fields.
		It returns the full path of the both FCs created in a list.
		"""

#	txt_fcname = 'temp_' + inv_class + '_alltxt_' + unique_suffix # eg. temp_bmi_alltxt_201801181529
	actual_fcname = inv_class + '_' + unique_suffix
	print2('\ncreating a new template FC: %s'%actual_fcname)

#	arcpy.CreateFeatureclass_management(out_path=outputgdb, out_name=txt_fcname, geometry_type="POLYGON", spatial_reference="PROJCS['MNR_Lambert_Conformal_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',930000.0],PARAMETER['False_Northing',6430000.0],PARAMETER['Central_Meridian',-85.0],PARAMETER['Standard_Parallel_1',44.5],PARAMETER['Standard_Parallel_2',53.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-35121300 -18032700 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")
	arcpy.CreateFeatureclass_management(out_path=outputgdb, out_name=actual_fcname, geometry_type="POLYGON", spatial_reference="PROJCS['MNR_Lambert_Conformal_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',930000.0],PARAMETER['False_Northing',6430000.0],PARAMETER['Central_Meridian',-85.0],PARAMETER['Standard_Parallel_1',44.5],PARAMETER['Standard_Parallel_2',53.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-35121300 -18032700 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")

#	txt_fc = os.path.join(outputgdb,txt_fcname)
	actual_fc = os.path.join(outputgdb,actual_fcname)


	# importing the corresponding library...
	import_script = 'import reference_%s as ref'%inv_class
	exec import_script in globals() # for example, "import reference_ar_hrv as ref"    globals() is necessary to specify the nature of the variable because this runs as a sub function.


	fieldDict = ref.fields

	# creating fields with correct field types
	for k,v in sorted(fieldDict.items()):
		#print2('Adding Field - %s'%v)
		fieldtype = v[2]
		if fieldtype == 'TEXT':
			fieldlength = str(v[1])
		else:
			fieldlength = ""
		arcpy.AddField_management(in_table=actual_fc, field_name=v[0], field_type=fieldtype, field_precision="", field_scale="", field_length=fieldlength)


	return actual_fc # this would be the full path of newly created feature class.




def create_gdb(output_folder, unique_suffix):
	"""This will create a new unique file geodatabase within the output_folder"""

	print2('executing create_gdb function...')
	out_gdb_name = 'Compiler_Output_' + unique_suffix

	arcpy.CreateFileGDB_management(out_folder_path=output_folder, out_name=out_gdb_name, out_version="CURRENT")

	out_gdb_path = os.path.join(output_folder,out_gdb_name + '.gdb')
	return out_gdb_path






if __name__ == '__main__':
	gdb = r'\\lrcpsoprfp00001\MNR_NER\GI_MGMT\Tools\Scripts\FMPTools_2017\FMP_SpatialData_Compiler\compiler_output\temp_201801181536.gdb'
	create_template(gdb)

	# create_gdb(r'\\lrcpsoprfp00001\MNR_NER\GI_MGMT\Tools\Scripts\FMPTools_2017\FMP_SpatialData_Compiler\compiler_output')