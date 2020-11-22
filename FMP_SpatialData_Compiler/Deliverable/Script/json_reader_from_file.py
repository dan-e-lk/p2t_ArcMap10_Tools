#-------------------------------------------------------------------------------
# Name:         Compile forest inventory execution instructions and associated metadata.
# Purpose:      To provide reuseable and accurate documentation of the specific instructions for the compiler.
#
# Author:       littleto
#
# Created:      15-01-2018
# Copyright:    (c) littleto 2018
# Licence:      <your licence>
#-------------------------------------------------------------------------------

import os, io, json

def load_json(exe_instruct):
    """
    exe_instruct, is the path and file name of the execute instructions. The
    execute instructions are a string variable to define location of the
    spatial data compiler execution instructions and other project metadata.
    This file must be a JSON file.

    The anticiapted format of the JSON is as follows:

    {
    	"proj_descr": "<This is user input for the description of the project>",
    	"unique_id": {
    		"1": {
    			"inv_name": "<User defined name of the inventory>",
    			"inv_descr": "<This is used to describe the input for the inventory in 'path'>",
    			"path": "<User defined path and name of the ESRI file geodatabase (.gdb)>",
    			"inv_type": "<User defined type of inventory, this is initially intended as metadata to identify the FMP Tech Spec. information type: FRI, EFRI, PCM, BMI, PCI, OPI>"
    		}<place a "," and contiune for the next inventory unique id.>
    	},
    	"output_folder": "<User defined path for the output of the compiler>"
    }

    JSONLint - The JSON Validator is a tool validate JSON syntax, and can be
    useful for large JSON files:

        https://jsonlint.com/

    """

    # Check to see if the execute instruction and the project information file exits, if not it raises an exception.
    if os.path.exists(exe_instruct) == True:
        print "Project path is set to: " + exe_instruct + "\n"
    else:
        raise Exception("The compiler execute instructions and project information file does not exist.")

    # Open the json file.
    json_file = open(exe_instruct, "r")

    # Load the instructions to a python dictionary from the json file.
    json_data = json.load(json_file)

    # Close the json file.
    json_file.close()

    # See raw results of the load json data as python dictionary.
##    print json_data

    # Return the json data, read from the file as a python dictionary
    return json_data

def print_json_data(data):
    """
    Test print the loaded json data to the python interpreter.

    data, is the results from the "load_json" function.

    """

    # Print the project information
    for project_info in sorted(data.iterkeys()):
        print project_info + '\n'

        # Test is the project information is the "unique_id" containing the inventory specifics
        if project_info == "unique_id":

            # Print the inventory specifics for each inventory "unique_id"
            ## The print order is "sorted" by the iterable keys for the unique id dict, since dictionaries themselves are not "sortable".
            for inventory in sorted(data["unique_id"].iterkeys()):
                print "\t Inventory unique id: %(id)s" %{"id":inventory}

                # Print the inventory information for each inventory in the project
                for inventory_info in data["unique_id"][inventory]:
                    print '\t\t' + inventory_info + ": " + data["unique_id"][inventory][inventory_info]
                print
            else:
                pass

def write_json(data, outputfile):
    """
    Write the loaded json data to the a unicode file.

    This function is expected to by useful if the script modifies the loaded
    json data... or hopely adds to it... :-)

    data, is the results from the "load_json" function.

    outputfile, is the path and nameo of the file that is written, with the extension.

    """

    # Open and new uft8 file and write the loaded json file to it.
    with io.open(outputfile, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data,
                      indent=4, sort_keys=True,
                      separators=(',', ': '), ensure_ascii=False)
        # Write the json in unicode.
        outfile.write(unicode(str_))

def check_json(data):
    """
    This function checks the existence of the paths for critical execute information in the JSON file.

    It is desireable not to call the "arcpy" module in this module. For re-useability of the script it is desireable to minimize the modules in which we call "arcpy" module.
    """

    # Check to see if the project "output_folder" key path exits, if not it raises an exception.
    if os.path.exists(data["output_folder"]) == True:
        print "Compiler project information folder/path for the output is set to: " + data["output_folder"] + "\n"
    else:
        print data["output_folder"]
        raise Exception("The compiler project information folder/path for the output does not exist.")

    # Check to see if the project "unique_id" (i.e., inventory path(s)) exists using the "path" key in each "unique_id", if not it raises an exception.
    for inventory in data["unique_id"]:
        if os.path.exists(data["unique_id"][inventory]["path"]) == True:
            print data["unique_id"][inventory]["path"]
##            pass
        else:
            raise Exception("The compiler source data file path to inventory (i.e., \"unique_id\") number '%(id)s' does not exist" %{"id":inventory})


if __name__ == '__main__':
    # execute_input =   r"\\lrcpsoprfp00001\mnr_ner\GI_MGMT\Tools\Scripts\FMPTools_2017\FMP_SpatialData_Compiler\Deliverable\Script\fmp_spatialdata_compilier_execute_instructions.json"
    # json_output =            r"\\lrcpsoprfp00001\mnr_ner\GI_MGMT\Tools\Scripts\FMPTools_2017\FMP_SpatialData_Compiler\Deliverable\Script\fmp_spatialdata_compilier_execute_instructions_dump2.json"

    # execute_info = load_json(execute_input)

    # print_json_data(execute_info)
    # write_json(execute_info, json_output)

    # check_json(execute_info)

    dict1 = {'a':'apple','b':'boat'}
    output_file = r'C:\TEMP\temp2\test.json'
    write_json(dict1,output_file)
