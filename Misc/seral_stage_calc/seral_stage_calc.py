#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      littleto
#
# Created:     24-09-2018
# Copyright:   (c) littleto 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
r""" This module is the version 0 of a seral stage calculator for ArcMap"""
import arcpy
import os
from datetime import datetime
from messages import print2
from messages import output

# This is the seral stage dictionary from Dave Morris
## email Dave Morris 2018-05-24 10:46; attachment (1)
## There is one seral stage age range suite for all of his species groupings
DaveM_Seral_Stage_Dict = {  'Est'   :[0,    20],
                            'CC'    :[21,   40],
                            'ST'    :[41,   60],
                            'M'     :[61,   100],
                            'OG'    :[101,  'unlim']}

def seral_field(layer_name, field_name):
    r"""
    Check to see of the seral stage record field exists.

    If the field exists... [do nothing at the moment].

    If the field does not exist then add the field.

                *** This function requires the arcpy module. ***
    """

    # Check if the user-defined seral stage field name already exists.
    if field_name in [f.name for f in arcpy.ListFields(layer_name)]:
        print "The '%s' is already in '%s'" %(field_name, layer_name)
    else:   # If the user-defined field name does not exist, then make it.
        print "The '%s' is NOT in '%s'" %(field_name, layer_name)
        arcpy.AddField_management(  layer_name,
                                    field_name,
                                    field_type="TEXT",
                                    field_precision="",
                                    field_scale="",
                                    field_length="",
                                    field_alias="",
                                    field_is_nullable="NULLABLE",
                                    field_is_required="NON_REQUIRED",
                                    field_domain="")


def seral_calc_method_1(layer_name, field_name, seral_dict, inventory_age, field_yr_origin = "OYRORG", log_output_path = r"w:\temp"):
    # This method only calls one arcpy command: CalculateField_management, for
    # each iteration.
    ## The alternative approach I thought of requires a SelectLayerByAttribute_managment
    ## and then a CalculateField_management, for each iteration. I am thinking
    ## this would be less efficient than my chose alternative.
    r"""Calculate the seral stages as per the identified seral stage dictionary.

    *** This function will calculate seral stages for non-forest areas ***

    To avoid calculating seral stages for non-forest area prepare your state by
    pre-selecting forest records; for example, POLYTYPE = 'FOR'.

                *** This function requires the arcpy module. ***
    """
    # Mark start time
    starttime = datetime.now()
    msg = print2('Start of process: %(start)s' %{'start':starttime.strftime('%Y-%m-%d %H:%M:%S')})

    msg += print2('layer: %(layer)s\nnew field: %(field_seral)s\nseral dictionary: %(seral_dict)s\ninventory age: %(invage)s\nyear_origin_field: %(field_yr_origin)s' %{'layer':layer_name, 'field_seral':field_name, 'seral_dict':seral_dict, 'invage': inventory_age, 'field_yr_origin':field_yr_origin})

    seral_field(layer_name, field_name)

    # Check to ensure that that user-defined 'field_yr_origina' exists in the inventory
    if field_yr_origin in [f.name for f in arcpy.ListFields(layer_name)]:
        print "The '%s' in '%s'" %(field_yr_origin, layer_name)
    else:
        # https://docs.python.org/3/library/exceptions.html#exception-hierarchy
        # https://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python
        raise Exception("The '%s' is NOT in '%s'" %(field_yr_origin, layer_name))

    # Print the seral stage dictionary
    msg += print2(str([(k, v) for k, v in seral_dict.iteritems()]))

    # Iterate throught the seral stage dictionary
    for k, v in seral_dict.iteritems():

        msg += print2('\tseral code: %(kcode)s, lower age limit: %(low)s, upper age limit: %(upp)s' %{'kcode':k, 'low':v[0], 'upp':v[1]})

        # Change the CalculateField code block for the final seral stage.
        if v[1] <> 'unlim':
            Calc_Select_Rec = """def Calc_Select_Rec(field, inventory_age, yrorg, lower, upper, code):
                age = inventory_age - yrorg
                if age >= lower and age <= upper:
                    return code
                else:
                    return field
            """
        elif v[1] == 'unlim':
            v[1] = 0        # This is to replace the 'string' values with an integer to pass to the one arcpy.CalculateField_management function.
                            ## I suppose I could have just rewritten the CalculateFIeld_management 'expression' argument, but re-assigning v[1] as a integer seemed easier at time.
            Calc_Select_Rec = """def Calc_Select_Rec(field, inventory_age, yrorg, lower, upper, code):
                age = inventory_age - yrorg
                if age >= lower:
                    return code
                else:
                    return field
            """

        arcpy.CalculateField_management(layer_name,
                                        field_name,
                                        expression="Calc_Select_Rec(!" + field_name + "!, int(" + str(inventory_age) + "), !" + field_yr_origin + "!, int(" + str(v[0]) + "), int(" + str(v[1]) + "), '" + k + "')",
                                        expression_type="PYTHON_9.3",
                                        code_block=Calc_Select_Rec)



    # Mark end time
    endtime = datetime.now()
    msg += print2('\nEnd of process: %(end)s' %{'end':endtime.strftime('%Y-%m-%d %H:%M:%S')})
    msg += print2('Elapsed time: %(duration)s seconds.' %{'duration':(endtime - starttime).total_seconds()})
    msg += print2(10*'\n' + '\t[' + os.path.basename(__file__).split(".")[0] + ']')   #https://stackoverflow.com/questions/4152963/get-the-name-of-current-script-with-python

    # write the messages as a log file.
    ## Create the log file name
    log_output_file_name = os.path.split(layer_name[0:28])[1] + "_seral_stage_calc_log_" + starttime.strftime('%Y_%m_%d_%H%M') + ".txt"

    ## Assemble the log file path and name
    Output_log_file = os.path.join(log_output_path, log_output_file_name)
    with open(Output_log_file, "w") as f:
        f.writelines(msg)

    return [msg]

if __name__ == '__main__':

    layer_name  = "IMF3EPoC7Spp_NERSFURev_DFTv6 (testing subset)"    # This is the testing layer, subset of the "bmi_201806010949_Intersect_IMF3EPoC7Spp_NERSFURev_DFTv6"
    layer_name  = "bmi_201806010949_Intersect_IMF3EPoC7Spp_NERSFURev_DFTv6"
    field_name  = "DaveM_Seral_Stages"
    seral_dict  = DaveM_Seral_Stage_Dict
    field_yr_origin = "MYRORG"
    inventory_age = 2018
    log_output_path = r"C:\Users\littleto\data\imf\imf_3E_proof_of_concept_project"

    seral_calc_method_1(layer_name, field_name, seral_dict, inventory_age, field_yr_origin, log_output_path)
