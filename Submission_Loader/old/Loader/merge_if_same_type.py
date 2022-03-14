# this was last edited on Feb 2022.
# The reason why this was edited is because some layers - the AOC kinds - errored out while merging
# The problem usually is that these AOC layers have inconsistent field lengths
# For example, AOCID field might start with just having 4 character length, then as you merge multiple layers
#   you'd encounter a layer with AOCID value greater than 4, in which case the ArcMap's merge function errors out
# The most reliable solution is to create a template for the AOC layers - AOC of FMP and SAC of AWS - and append the values.
# Another solution, easier but less reliable solution, is to take the first of these layers and arbitrarily increase the field length of all its fields.
# So that's sort of my soluther here. If the layers that didn't correctly merge are either AOC or SAC, then we will apply the template solution
# If the layers that didn't correctly merge are not AOC or SAC, then we will apply the increase field length solution.

debug = True
from functions import print2, rand_alphanum_gen
import arcpy
import os

def main(gdb):
	"""
	If there are more than one same type of layer in gdb (for example, AOC01, AOC02),
	this tool will merge the layers into one (for example, AOC_merge)
	This tool doesn't delete any of the original feature classes in the gdb.
	This tool assumes all layers have these two formats: mu415_16aoc00 or mu41516aoc000 *Jan2021: added a new acceptable format: mu415_16aoc000
	"""
	arcpy.env.workspace = gdb
	
	# creating a list of fcs
	fc_list = [str(i) for i in arcpy.ListFeatureClasses() if len(str(i)) == 13 or len(str(i)) == 14] #all variations have character len of 13 or 14
	if debug: print2('fc_list = %s'%fc_list)

	# no point running the function if it's an empty gdb
	if len(fc_list) == 0:
		raise Exception("Unable to run merge_if_same_type, because either the input gdb is empty or the fcs don't follow the correct naming convention.")

	# checking if there are more than one layer of the same type.
	# 3 potential types: mu415_16aoc00, mu41516aoc000 and mu415_16aoc000
	need_merge = False
	type_list = [i[8:11].upper() if i[5] =='_' else i[7:10].upper() for i in fc_list] # this will pick up 'AOC' from both mu415_16aoc01 and mu41516aoc001
	type_set = set(type_list)
	if len(type_list) == len(type_set):
		print2('No layer needs to be merged.')
	else:
		type_dict = {k:[] for k in type_set}  # this will create, for example, {'WTX': [], 'HRV': [], 'FTG': [], 'RDS': [], ...}
		for fc in fc_list:
			tpe = fc[8:11].upper() if '_' in fc else fc[7:10].upper() # this will pick up 'AOC' from both mu415_16aoc01 and mu41516aoc001
			if tpe in type_set:
				type_dict[tpe].append(fc) # this will create, for example, {'WTX': ['mu415_16wtx00'], 'HRV': ['mu415_16hrv00'], ...}

		# merging same type
		for k, v in type_dict.items():
			if len(v) > 1:
				print2('\tMerging %s...'%k)
				output_name = v[0][:-2] + '_merged' if '_' in v[0] else v[0][:-3] + '_merged'
				try:
					arcpy.Merge_management(v, output_name)
				except Exception as e:
					print2("\tInitial merge failed with the following error:")
					print2("\t %s"%str(e))
					# when the first attempt of merge fails, the most likely error looks something like,
					# ERROR 001156: Failed on input OID 1, could not write value 'WLSzzz' to output field AOCID\n Failed to execute (Merge).
					# ERROR 001156: Failed on input OID 1, could not write value 'Modified Riparian' to output field SYMBOL\n Failed to execute (Merge).
					# A workaround for this particular issue is to increase the length of the string attributes of the first layer
					if "ERROR 001156:" in str(e):
						try:
							print2("\t\tRe-attempting merge.")
							print2("\t\tIncreasing the field length of all the string fields of the first layer by +30...")
							print2("\t\t (Note that this doesn't alter the original data)")
							increase_field_length(v[0], 30)
							# try merging again
							print2("\n\t\tMerging %s (2nd try)..."%k)
							arcpy.Merge_management(v, output_name)
							print2("\t\t\tMerging successful!")

						except Exception as e:
							# this will still fail if there are field length mis-match between layers other than the first layer.
							print2(str(e), 'warning')
							print2('\t\tFailed to merge %s! (2nd try)'%k, 'warning')
							if arcpy.Exists(output_name):
								arcpy.Delete_management(output_name)

					else:
						print2('\t\tFailed to merge %s!'%k, 'warning')
						if arcpy.Exists(output_name):
							arcpy.Delete_management(output_name)



def increase_field_length(layer, increment):
	"""increases the field length of the layer by the specified increment.
	Only alters string fields.
	"""
	f = arcpy.ListFields(layer)
	original_fields = {}  # eg. {'AOCID': 6, ...}
	for field in f:
		# get fields with type - string
		if field.type == "String":
			fname = field.name
			flength = int(field.length)
			original_fields[fname] = flength

	# unfortunately, the fieldlength cannot be directly changed.
	# current field will be renamed, then the new field will be created with larger field length, then the values will be copied over to the new field.
	for fname, flength in original_fields.items():
		print2("\t\t Increasing the field length of %s - %s"%(layer,fname))
		# rename the original field
		temp_fname = fname + '_' + rand_alphanum_gen(4)
		arcpy.management.AlterField(in_table=layer, field=fname, new_field_name=temp_fname)
		# create a new field using the original fieldname such as 'AOCID'
		new_flength = flength + increment
		arcpy.AddField_management(in_table=layer, field_name=fname, field_type="TEXT", field_length=new_flength)
		# populate the new field with the original values
		expression = "!%s!"%temp_fname
		arcpy.CalculateField_management(layer, fname, expression, "PYTHON_9.3")
		# delete the temporary field
		arcpy.DeleteField_management (layer, temp_fname)




if __name__ == '__main__':
	gdb = r'C:\DanielK_Workspace\_TestData\Temagami\AWS\2022\LayerMergeIssue\test\_data\FMP_Schema.gdb'
	main(gdb)


	# increase_field_length unit test
	# lyr = r'C:\DanielK_Workspace\_TestData\Temagami\AWS\2022\LayerMergeIssue\test\_data\FMP_Schema.gdb\MU898_22SAC03'
	# increment = 30
	# increase_field_length(lyr, increment)
