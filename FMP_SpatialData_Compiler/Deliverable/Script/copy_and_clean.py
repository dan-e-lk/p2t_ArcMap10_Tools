# This script copies over the user defined input file to user defined output folder.
# This script also changes field names and corrects the data if necessary.

import os, datetime

print('importing arcpy...')
import arcpy

def print2(msg, msgtype = 'msg'):
	# print(msg)
	if msgtype == 'msg':
		arcpy.AddMessage(msg)
	elif msgtype == 'warning':
		arcpy.AddWarning(msg)
	return msg


def copy_and_clean(output_gdb, unique_id, original_file_path, inv_type, inv_name, sub_id, inv_year, inv_class):
	""" Copies the user input inventory to the user specified output location.
		Also corrects the fields (for example changes WG to LEADSPC) and checkes the record (eg. if AGE field is filled out with integers)
		to make sure the data is ready to get appended to the template feature class"""
	temp_fc_name = 'temp' + str(unique_id)
	msg = ''

	print2('Copying %s-%s-%s to the output location...'%(unique_id,inv_name,inv_type))
	arcpy.FeatureClassToFeatureClass_conversion(in_features=original_file_path, out_path=output_gdb, out_name=temp_fc_name, where_clause="")
	temp_fc_path = os.path.join(output_gdb,temp_fc_name)
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(temp_fc_path)]

	# importing the corresponding library...
	import_script = 'import reference_%s as ref'%inv_class
	exec import_script in globals() # for example, "import reference_ar_hrv as ref".   globals() is needed here because this will be run as a sub-function.


	# if the user's data contains old fields that needs update (such as WG), the following will update those fields
	print2('Editing fieldnames of %s-%s-%s...'%(unique_id,inv_name,inv_type))
	for k,v in ref.fieldname_update.items():
		old_field_list = v
		correct_field = k
		for existingField in existingFields:
			if correct_field not in existingFields and existingField in old_field_list:  # if the correct field already exists, no need to alter field.
				msg += print2("\nRenaming the field %s to %s."%(existingField,k))
				try:
					# this only works on 10.2 or above
					arcpy.AlterField_management(in_table=temp_fc_path, field=existingField, new_field_name=k)
				except:
					# this will work on any arcmap version
					import alter_field2
					alter_field2.alter_field2(full_fc_path = temp_fc_path, old_field = existingField, new_field = k)


	# Adding additional fields such as AUTOGEN_DATE_APPEND to the temp FC
	for k,v in ref.fields.items():
		if k < 0 or k > 100:
			new_field_name = v[0]
			if new_field_name in existingFields:
				arcpy.DeleteField_management(in_table=temp_fc_path, drop_field=new_field_name)
			fieldtype = v[2]
			if fieldtype == 'TEXT':
				fieldlength = str(v[1])
			else:
				fieldlength = ""
			arcpy.AddField_management(in_table=temp_fc_path, field_name=new_field_name, field_type=fieldtype, field_precision="", field_scale="", field_length=fieldlength)


	# We will use the field 101 (record_altered) field to keep record of any edits we make to the rawe data.
	record_altered_field = ref.fields[101][0] # this is the name of the field that will keep the record of edits if any.
	arcpy.CalculateField_management(in_table=temp_fc_path, field=record_altered_field, expression="''", expression_type="PYTHON") # filling this field with a blank space is required to concatenate strings later


	# We are going to give special attention to the non-text fields - to make sure they do append to the final template.
	fields_and_types = {str(f.name).upper(): str(f.type).upper() for f in arcpy.ListFields(temp_fc_path)}

	# checking non-text fields to make sure they can be turned into int or float (going through each field then each record)
	print2('checking non-text fields to make sure they can be turned into int or float...')
	for k,v in ref.fields.items():
		field = v[0]
		fieldtype = v[2]
		if field in existingFields:
			if fieldtype in ['SHORT','LONG','FLOAT','DOUBLE']: 
				if fields_and_types[field] not in ['INTEGER','SMALLINTEGER','SINGLE','DOUBLE']: # in English: if what should be a number field is not a number field...
					cursor = arcpy.da.UpdateCursor(temp_fc_path,[field,record_altered_field])
					for row in cursor:
						if row[0] != None:
							try:
								int(row[0]) # will error if it's not a number
							except:
								row[1] = row[1] + '%s: [%s] to [None]  '%(field,row[0]) # if not a numer, turn it into "None" and write what's been edited.
								row[0] = None
							cursor.updateRow(row)
					del cursor # Delete cursor and row objects to remove locks on the data.


	# populate user inputs and auto fields...
	print2('Populating user inputs such as inventory name...')

	arcpy.CalculateField_management(in_table=temp_fc_path, field="USER_INPUT_INV_YEAR", expression='"' + inv_year + '"', expression_type="PYTHON")
	arcpy.CalculateField_management(in_table=temp_fc_path, field="USER_INPUT_FOREST", expression='"' + inv_name + '"', expression_type="PYTHON")
	arcpy.CalculateField_management(in_table=temp_fc_path, field="USER_INPUT_SUB_ID", expression='"' + sub_id + '"', expression_type="PYTHON")	
	arcpy.CalculateField_management(in_table=temp_fc_path, field="USER_INPUT_INVTYPE", expression='"' + inv_type + '"', expression_type="PYTHON")
	arcpy.CalculateField_management(in_table=temp_fc_path, field="AUTOGEN_INVID", expression='"' + unique_id + '"', expression_type="PYTHON")

	date_today = datetime.datetime.now().strftime('%Y-%m-%d')
	arcpy.CalculateField_management(in_table=temp_fc_path, field="AUTOGEN_DATE_APPEND", expression='"' + date_today + '"', expression_type="PYTHON")

	return msg, temp_fc_path




# The rec_counter really has nothing to do with copy and clean, but there's no good place to put this so it's here now...
def rec_counter(fc):
	count = arcpy.GetCount_management(fc)[0]
	return str(count)




