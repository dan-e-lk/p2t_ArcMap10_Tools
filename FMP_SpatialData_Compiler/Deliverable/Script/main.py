# This is the main script for FMP_SpatialData_Compiler
#
#########################################################################################
#
############                            Workflow                          ###############
#
#########################################################################################
#
# 1. you need a json script such as this:
#
# {
#	"inv_class": "bmi",
# 	"proj_descr": "project description",
# 	"unique_id": {
# 		"1": {
# 			"inv_name": "Gordon Cosens",
# 			"inv_descr": "Gordon Cosens PCI lite version",
# 			"path": "//lrcpsoprfp00001/MNR_NER/GI_MGMT/Tools/Scripts/FMPTools_2017/FMP_SpatialData_Compiler/TestData/Gordon_Cosens/FMP/2020/_data/FMP_Schema.gdb/MU438_20PCI99",
# 			"inv_type": "PCI",
# 			"inv_year": 2020,
# 			"sub_id": "99999"
# 			},
# 		"2": {
# 			"inv_name": "Hearst",
# 			"inv_descr": "Hearst 2017 PCM lite version",
# 			"path": "//lrcpsoprfp00001/MNR_NER/GI_MGMT/Tools/Scripts/FMPTools_2017/FMP_SpatialData_Compiler/TestData/Hearst/FMP/2017/_data/FMP_Schema.gdb/mu601_17pcm99",
# 			"inv_type": "PCM",
# 			"inv_year": 2017,
# 			"sub_id": "00000"
# 			}
# 		},
# 	"output_folder": "C:/TEMP/temp2"
# }
#
#
# 2. Check the input json file and see if all input paths exists and if the unique ids are actually unique.
# 3. Create a new file gdb in the user specified output folder.
# 4. Create and start populating log file.
# 5. Create the template feature class which has all the correct fields for 2017 tech spec.
# for each input inventory:
# 	6. Copy the original data to the newly created file gdb.
# 	7. Update the fieldnames to 2017 tech spec fields.
# 	8. Validate the format of non-string fields. For example, YRDEP field shouldn't contain string values.
# 	9. Adding and populating additional fields such as Date_append.
# 	10. Append the input inventory to the template feature class created in step 5.
# 	11. count the records appended to make sure all the data has been transferred.
# 12. do a total count check to make sure all the records have been appended.
# 13. finish writing up the log file.
#
#########################################################################################



import json_reader_from_file
import create_template
import reference_bmi
import copy_and_clean

import os, datetime, getpass, pprint, traceback

import arcpy # inevitable!!


def main(jsonfilename):

	error_flagged = False

	json_data = json_reader_from_file.load_json(jsonfilename)

	# need to check the json using functions from json_reader_from_file

	print(json_data) # {u'proj_descr': u'<description...>', u'unique_id': {u'1': {u'path': u'//lrcpsoprfp00001/mnr_ner/GI_MGMT/Tools/Scripts/FMPTools_2017/FMP_SpatialData_Compiler/TestData/Gordon_Cosens/FMP/2020/_data/FMP_Schema.gdb', u'inv_type': u'PCI', u'inv_name': u'Gordon Cosens', u'inv_descr': u"<This is used to describe the input for the inventory in 'path'>"}, ...

	output_folder = json_data['output_folder']
	inv_class = json_data['inv_class'] 

	date_today = datetime.datetime.now().strftime('%Y-%m-%d') # eg. '2018-29-09'
	unique_suffix = datetime.datetime.now().strftime('%Y%m%d%H%M') # eg. '201801181529'

	username = getpass.getuser()

	# creating a log text file
	logfilename = os.path.join(output_folder,'Compiler_log_' + unique_suffix + '.txt')
	log = open(logfilename,'w')

	try:
		msg = print2('Compiler output log - ' + str(date_today))
		msg += print2('\nRun by: ' + username)
		msg += print2('\nInput Location: ' + str(jsonfilename))

		# Creating a file geodatabase in the user-specified output folder
		output_gdb = create_template.create_gdb(output_folder,unique_suffix) # eg. \\lrcpsoprfp00001\MNR_NER\GI_MGMT\Tools\Scripts\FMPTools_2017\FMP_SpatialData_Compiler\compiler_output\Compiler_Output_201801181703.gdb			 \bmi_201801181703
		msg += print2('\nOutput Location: ' + str(output_gdb))


		# Creating the template feature class with all the correct fields
		template_fc = create_template.create_template(output_gdb,unique_suffix, inv_class = inv_class) # this will be the full path of the template FC created which will later become final.

		# Start the record counter. This will be later checked with the record count of the final product.
		accumulated_rec_num = 0
		count_appended = 0

		# for loop for individual files(inventories) in the user input
		msg += print2('\n\nWorking on user Input:\n')
		tot_num_inv = len(json_data['unique_id']) # total number of inventories.
		for k,v in sorted(json_data['unique_id'].items(), key= lambda x: int(x[0])): # this lambda function ensures that the unique ID is sorted as an int not as a str.
			try:
				unique_id = str(k)
				original_file_path = str(v['path'])
				inv_type = str(v['inv_type'])
				inv_name = str(v['inv_name'])
				sub_id = str(v['sub_id'])
				inv_descr = str(v['inv_descr'])
				inv_year = str(v['inv_year'])

				msg += print2("""
				\n\n***************	Inventory %s of %s:
				\n\tOriginal File Path: %s
				\n\tInventory Type: %s
				\n\tInventory Name: %s
				\n\tInventory Year: %s
				\n\tInventory Description: %s
				\n\tSubmission ID: %s
							"""%(unique_id, tot_num_inv, original_file_path,inv_type,inv_name,inv_year,inv_descr,sub_id))


				# Counting the number of records in the original input
				count = int(copy_and_clean.rec_counter(original_file_path)) # returns the number of records in str format
				msg += print2('\tRecord count: %s\n'%count)
				accumulated_rec_num += count
				json_data['unique_id']['record_count'] = count


				# copying the original data to the output location and if necessary, renaming fieldnames and editing the data itself (for example, if string value is in int field)
				copy_and_clean_return = copy_and_clean.copy_and_clean(output_gdb, unique_id, original_file_path, inv_type, inv_name, sub_id, inv_year, inv_class = inv_class)
				msg += copy_and_clean_return[0]
				temp_fc_path = copy_and_clean_return[1]


				# actually appending:
				msg += print2('\n\tAppending %s...'%temp_fc_path)
				arcpy.Append_management(inputs=temp_fc_path, target=template_fc, schema_type="NO_TEST")


				# counting records to see if everything has been moved over
				last_count_appended = count_appended
				count_appended = int(copy_and_clean.rec_counter(template_fc))
				if count_appended - last_count_appended == count:
					msg += print2('\n\tAll %s records appended successfully.'%count)
				else:
					missing_records = count - (count_appended - last_count_appended)
					msg += print2('\n\t!!! Not all records have been appended !!!\nMissing Records: %s'%missing_records,'warning')
			except:
				error_msg = traceback.format_exc()
				msg += print2(error_msg)
				error_flagged = True

		# Doing the total count check:
		msg += print2('\n\nFINAL COUNT CHECK:')
		final_count = int(copy_and_clean.rec_counter(template_fc))
		if final_count == accumulated_rec_num and not error_flagged:
			msg += print2('\nAll %s records appended successfully.\n'%final_count)
		else:
			missing_records = accumulated_rec_num - final_count
			msg += print2('\n!!! Not all records have been appended !!!\n','warning')
			if missing_records > 0:
				msg += print2('\nNumber of missing records: %s\n'%missing_records,'warning')


		pretty_string = pprint.pformat(json_data, indent=4)
		msg += '\n\n' + pretty_string

		return template_fc

	finally:
		log.write(msg)
		log.close()

		os.startfile(output_folder)




def print2(msg, msgtype = 'msg'):
	""" print, arcmap AddMessage and return string all in one!"""
	# print(msg)
	if msgtype == 'msg':
		arcpy.AddMessage(msg)
	elif msgtype == 'warning':
		arcpy.AddWarning(msg)
	return msg






# You can run this script right here. change the jsonfilename variable below to the path to your json input file.
if __name__ == '__main__':
	jsonfilename = os.path.join(os.path.dirname(__file__),'test_input_daniel.json')
	main(jsonfilename)