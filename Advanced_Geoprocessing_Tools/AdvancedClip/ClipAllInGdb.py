
print('importing arcpy...')
import arcpy
import os
import re

def clipAll(input_gdb,output_gdb,clip_feature,suffix):
	"""
	Individually clips each and every feature classes in input_gdb using clip_feature shape and exports it to the specified output_gdb.
	"""

	# list of existing fcs in the output gdb
	arcpy.env.workspace = output_gdb
	fcs = arcpy.ListFeatureClasses()
	list_of_existing_fcs = [str(fc) for fc in fcs]


	# resetting the workspace
	arcpy.env.workspace = input_gdb
	fcs = arcpy.ListFeatureClasses()
	total = len(fcs)
	arcpy.AddMessage('Total number of features to clip: %s'%total)


	for num, fc in enumerate(fcs):
		arcpy.AddMessage('%s out of %s - Clipping %s...'%(str(num + 1), total, str(fc)))
		newfc_name = str(fc) + '_' + suffix
		newfc_path = os.path.join(output_gdb, newfc_name)

		if newfc_name not in list_of_existing_fcs:
			arcpy.Clip_analysis(in_features=fc, clip_features=clip_feature, out_feature_class= newfc_path, cluster_tolerance="")
		else:
			arcpy.AddMessage('\t%s already exists.'%(newfc_name))


if __name__ == '__main__':

	input_gdb = arcpy.GetParameterAsText(0) # for example, 'N:\NDD\GDDS-Internal-MNRF.gdb' 
	output_gdb = arcpy.GetParameterAsText(1) # for example, '\\lrcpsoprfp00001\MNR_NER\GI_MGMT\Temp\DataForKL\KL_NDD_NonSens.gdb' 
	clip_feature = arcpy.GetParameterAsText(2) # for example, 'C:\DanielK_Workspace\Scripts\ClipToKL\KL_Non_Sens.gdb\KL_DistrictBdry_Buff20k'
	suffix = arcpy.GetParameterAsText(3) # for example, 'test'

	# suffix must have no space and no special characters except _ and -
	if re.match("^[\w\d_-]*$",suffix):
		if len(suffix) < 100:
			pass
		else:
			raise Exception("Your suffix is too long!")
	else:
		raise Exception("Your suffix contains spaces or special characters.")


	clipAll(input_gdb,output_gdb,clip_feature,suffix)

