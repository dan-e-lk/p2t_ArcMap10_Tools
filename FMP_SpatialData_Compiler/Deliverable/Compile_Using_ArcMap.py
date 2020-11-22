# This script will be used to create the arcmap tool.
# The script will try to find submission ID in the parent folder by looking for fi_submission_99999.txt file where 99999 is the sub id.
# use local (C drive) as the output folder for the best performance.
# all the input layer names must have "MU<FMU Code>_<year><layertype>" in its name. for example, "xyz_MU898_20PCI_daniel" is a valid name because it has 'MU898_20PCI'.


import os, datetime, io, json
import arcpy
import Script.identify_submission as ID_Sub
import Script.main

inv_class = arcpy.GetParameterAsText(0) # this defines the template to which you are appending your data. to use the template defined by reference_ar_hrv.py, put 'ar_hrv' here.
output_folder = arcpy.GetParameterAsText(1)
inventory_list = arcpy.GetParameter(2) # we will use the "feature layer" data type on the ArcMap tool because it's easier for the user. But we will have to find the full path of these layers.
proj_desc = arcpy.GetParameterAsText(3)


# inventory_list is an arc object. We need to turn it into a list of full paths.
pathlist = []
for inv in inventory_list:
	desc = arcpy.Describe(inv)
	fullpath = os.path.join(desc.path,desc.name)
	pathlist.append(fullpath)


# Converting the inputs into a dictionary
input_detail_dict = {}
for index, path in enumerate(pathlist, start = 1):
	input_detail_dict[index] = ID_Sub.identifySubmission(path)

input_dict = {
			"inv_class": 		inv_class,
			"proj_descr": 		proj_desc,
			"output_folder": 	output_folder,
			"unique_id":		input_detail_dict
			}


# Creating the JSON file in the user specified output folder.
unique_suffix = datetime.datetime.now().strftime('%Y%m%d%H%M') # eg. '201801181529'
outputfilename = 'compiler_run_' + unique_suffix + '.json'
outputfile = os.path.join(output_folder,outputfilename)

with io.open(outputfile, 'w', encoding='utf8') as outfile:
    str_ = json.dumps(input_dict,
                  indent=4, sort_keys=True,
                  separators=(',', ': '), ensure_ascii=False)
    # Write the json in unicode.
    outfile.write(unicode(str_))





# running the main script using the json file created above.
final_output = Script.main.main(outputfile) # this will run the main script and return the full path of the feature class created at the end of the script
arcpy.SetParameterAsText(4, final_output) # this will display the final product on arcmap table of contents.