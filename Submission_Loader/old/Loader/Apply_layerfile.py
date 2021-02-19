# ----------------------------
#
#
#
#
# ----------------------------

import os, shutil, arcpy
from functions import print2

#Provide the user with additional feedback when debugging the script
debug = False
arcpy.env.overwriteOutput = True

def findLyrFile(subType, techspec = '2017'):
	"""
	outputs a list of layer files (full path) of the correct subType and techspec version
	subType has to be AR, AWS or FMP
	techspec has to be '2017' or '2009'
	For example, an output can be...
   ['Z:\\Submission_Loader\\Loader\\lyrs\\2017spec\\AR\\AGG_AR.lyr',
	'Z:\\Submission_Loader\\Loader\\lyrs\\2017spec\\AR\\FTG_AR.lyr', ...]
	"""
	# for example, ...\Python2_Tools\Submission_Loader\Loader\lyrs\2017spec\AR
	path2lyrDir = os.path.join(os.path.split(__file__)[0], 'lyrs', techspec + 'spec', subType)
	if (os.path.exists(path2lyrDir)):
		path2lyr_list = [os.path.join(path2lyrDir, lyr) for lyr in os.listdir(path2lyrDir) if lyr.lower().endswith('.lyr')]
		return path2lyr_list
	else:
		return None

#Determine if the gdb exists, return True if it does, return False if it doesn't
def configureWorkspace(gdb, outputFolder):
 	# if gdb is not specified, it will default to the .../_data/FMP_Schema.gdb
	if (debug): print2('Attempting to set workspace...')

	if (gdb == None):
		if (debug): print2('gdb: %s' %(gdb))
		gdb = os.path.join(outputFolder, '_data','FMP_Schema.gdb')

		#Ensure that the default gdb exists, before continuing
		if (arcpy.Exists(gdb)):
			arcpy.env.workspace = gdb
		else:
			#gdb doesn't exist
			return False
	else:
		#Set the workspace to the GDB
		arcpy.env.workspace = gdb
	return True

#Obtain the layer file list, store them in dictionary format
def obtainLayerTypes(gdb, fc_list):
	if (debug): print2('identifying the layer types in %s' %(gdb))

	# this will pick up 'AOC' from both mu415_16aoc01 and mu41516aoc001 * and mu415_16aoc0001
	type_list = [i[8:11].upper() if i[5] =='_' else i[7:10].upper() for i in fc_list]
	type_set = set(type_list)

	# this will create, for example, {'WTX': [], 'HRV': [], 'FTG': [], 'RDS': [], ...}
	type_dict = {k:[] for k in type_set}

	for fc in fc_list:
		# this will pick up 'AOC' from both mu415_16aoc01 and mu41516aoc001
		tpe = fc[8:11].upper() if '_' in fc else fc[7:10].upper()

		if (tpe in type_set):
			# this will create, for example, {'WTX': ['mu415_16wtx00'], 'NDB': ['mu415_16ndb01', 'mu415_16ndb02', 'mu415_16ndb_merged'], ...}
			type_dict[tpe].append(fc)

	if (debug): print2('%s'%(type_dict))
	return type_dict

#Create the layer files, store them in array and return results
def createNewLayerFiles(type_dict, lyrTemplate_list, lyrInfo_dict, subType):
	print2('\nCreating layer files:')
	lyr_list = []

	# acronym = 'AOC', fclist = ['mu415_16aoc01','mu415_16aoc02']
	for acronym, fclist in type_dict.items():

		# locate the correct template layer
		template_finder = [template for template in lyrTemplate_list if acronym in os.path.split(template)[1]]

		if (len(template_finder) < 1):
			print2('\tNo template available for %s' %(fclist), 'warning')

			# still make a layer file, but no symbology...
			for fc in fclist:
				lyrname = '%s_%s'%(subType, fc)
				print2('\t%s'%(lyrname))
				arcpy.MakeFeatureLayer_management(in_features = fclist[0], out_layer = lyrname)
				lyr_list.append(lyrname)

		# if the template exists for this acronym, make a layer and apply the template's symbology
		elif (len(template_finder) >= 1):
			template_lyr = template_finder[0]
			if (debug): print2('\ttemplate layer: %s' %(template_lyr))

			# if there's only one feature class for this particular acronym (layer type)
			# In cases like this - 'AGG': ['mu415_16agg00']
			if (len(fclist) == 1):
				try:
					# if the acronym is EST, then lyrname = Establishment Assessment
					lyrname = '%s (%s)' %(lyrInfo_dict[acronym][0], acronym)

				except KeyError:
					# if the acronym is unknown, just use the name of the feature class.
					# This shouldn't happen because if the acronym is unknown, you won't have a template.
					lyrname = fclist[0]

				print2('\t%s' %(lyrname[2:]))
				arcpy.MakeFeatureLayer_management(in_features = fclist[0], out_layer = lyrname)
				arcpy.ApplySymbologyFromLayer_management(in_layer = lyrname, in_symbology_layer = template_lyr)
				lyr_list.append(lyrname)

			elif (len(fclist) > 1):
				# In cases like this - 'NDB': ['mu415_16ndb01', 'mu415_16ndb02', 'mu415_16ndb_merged']
				# find the merged one and use that layer only.
				merged_fc = [i for i in fclist if '_merged' in i]

				if (len(merged_fc) == 0):
					print2("\tFailed to create %s layer file - could not find a merged version of %s" %(acronym,acronym), 'warning')

				elif (len(merged_fc) > 1):
					print2("\tThere are more than one merged layer for %s:\n%s" %(acronym,fclist), 'warning')

				else:
					try:
						# if the acronym is EST, then lyrname = Establishment Assessment
						lyrname = '%s (%s) (merged)' %(lyrInfo_dict[acronym][0], acronym)

					except KeyError:
						# if the acronym is unknown, just use the name of the feature class.
						# This shouldn't happen because if the acronym is unknown, you won't have a template.
						lyrname = merged_fc[0]

					print2('\t%s'%lyrname[2:])
					arcpy.MakeFeatureLayer_management(in_features = merged_fc[0], out_layer = lyrname)
					arcpy.ApplySymbologyFromLayer_management(in_layer = lyrname, in_symbology_layer = template_lyr)
					lyr_list.append(lyrname)

	return lyr_list

#Group and save the layer files
def consolidateLayers(lyr_list, outputFolder, subType, fmuName, fmuCode, submYear, SubID):
	groupLyrName = '%s_%s_(%s)_%s_%s.lyr' %(subType,fmuName,fmuCode,submYear,SubID) # for example, AR_Gordoen_Cosens_(438)_2017_24649.lyr
	print2('\nCreating a group layer:  %s'%groupLyrName)

	# This mxd file has one dataframe with one empty group layer (the name of the group layer doesn't matter, but it has to be empty)
	mxd = arcpy.mapping.MapDocument(os.path.join(os.path.split(__file__)[0], 'lyrs', 'lyr_proj.mxd'))
	df = arcpy.mapping.ListDataFrames(mxd)[0]

	targetGroupLayer = arcpy.mapping.ListLayers(mxd)[0] # this would be 'a_group_layer' in the mxd file.
	targetGroupLayer.name = groupLyrName[:-4] # this renames 'a_group_layer' to something like AR_Gordoen_Cosens_(438)_2017_24649

	for lyr in sorted(lyr_list):
		addLayer = arcpy.mapping.Layer(lyr)
		addLayer.name = addLayer.name[2:]
		arcpy.mapping.AddLayerToGroup(data_frame = df, target_group_layer = targetGroupLayer, add_layer = addLayer, add_position = "BOTTOM")

	arcpy.SaveToLayerFile_management (targetGroupLayer, os.path.join(outputFolder,groupLyrName))

	# optionally, you can also save as mxd file (but not recommended because 10.3 mxd is not compatible with 10.1)
	# mxd.saveACopy(r"C:\FIPDownload\test1\Gordon_Cosens\AR\2017\SubID_24649\Project2.mxd")

	del mxd, df, targetGroupLayer


#import each layer, store results into dictionary array
def importLayerFiles(techspec, subType):
	if (techspec == '2017'):
		exec_command = 'from LayerInfo import %s_new as lyrInfo_dict' %(subType)
		exec(exec_command)
		return True, lyrInfo_dict
	else:
		return False, None


""" subType must be AR, AWS or FMP
	techspec must be either 2009 or 2017 in string form
	outputFolder is the full path to the parent folder of _data/FMP_Schema.gdb folder
	gdb is the full path to the geodatabase if it's not stored in _data/FMP_Schema.gdb
	"""
def main(subType, techspec, outputFolder, SubID, fmuName, fmuCode, submYear, gdb=None):

	# find layer files that will be used as a template.
	# note that this is stored in the tool package itself.
	if debug: print2('\nAttempting to create layer files and apply symbology to all layers...')
	lyrTemplate_list = findLyrFile(subType, techspec) # list of full path

	# If the path is NOT defined, then end the script
	if (not configureWorkspace(gdb, outputFolder)):
		print2('There was an error locating: %s' %(gdb), 'warning')
		print2('Unable to extract layers...', 'warning')
		return

	# Obtain the list of feature classes from the gdb
	fc_list = [str(i) for i in arcpy.ListFeatureClasses()]

	# identifying the layer types
	type_dict = obtainLayerTypes(gdb, fc_list)
	if (type_dict == []):
		print2('There are no layer file types...', 'warning')
		return

	# importing layer information such as "AGG":  ["Forestry Aggregate Pits",  ...]
	if (debug): print2('importing layer information...')
	validTechSpec, lyrInfo_dict = importLayerFiles(techspec, subType)
	if (not validTechSpec):
		print2('This tool will only work with the 2017 Tech Spec', 'warning')
		return

	# creating new layer files
	if (debug): print2('Creating new layers...')
	lyr_list = createNewLayerFiles(type_dict, lyrTemplate_list, lyrInfo_dict, subType)

	# consolidate (group) layer before save to layer file.
	if (debug): print2('Grouping layers...')
	consolidateLayers(lyr_list, outputFolder, subType, fmuName, fmuCode, submYear, SubID)

	#print2('There was a problem running the layer script. Aborting!', 'warning')


#--------------


if __name__ == '__main__':

	print(findLyrFile('AWS'))
	subType, techspec, outputFolder, SubID, fmuName, fmuCode, submYear = ['AWS','2017',r'\\lrcpsoprfp00001\GIS-DATA\WORK-DATA\FMPDS\Nipissing\AWS\2019\SubID_25284',25284, 'Nipissing', '754',2019]

	main(subType, techspec, outputFolder, SubID, fmuName, fmuCode, submYear)


#END OF FILE

