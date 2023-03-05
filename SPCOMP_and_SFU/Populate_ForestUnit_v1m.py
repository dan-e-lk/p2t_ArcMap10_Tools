version = '1m'

# 2022 - this tool populates SFU for records with POLYTYPE other than 'FOR'. Fix THIS!
#
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      kimdan
#
# Note: Work to be completed:
#   1. create and populate OSC field if it doesn't exist.
#   2. create Ecosite field and populate with only the first 4 letters of Ecosite1. Done
#   3. create user interface
#
# Changes Documentation:
#   2018-01-22  littleto    Add additional options to the typeLookup dict
#   2018-01-22  littleto    Correct the sorted order for the processing of the SQL criteria suite
#                               to "reverse = False"
#   2018-01-22  littleto    Add the replace string to incorperate "<user_defined_sfu_field_name>" for "Is
#                               Not Null" type interpretations in SQL criteria suite
#   2018-01-23  littleto    Add arc message to document script source file path for ArcMap users
#   2018-01-23  littleto    Add custom field name for AGE. Required for "NER_Boreal_SFU_TN021".
#                               - This requires update to the arguments for the "Main" function: AGEfield = "OAGE"
#                               - This required update to the ArcGIS toolbox
#   2018-01-23  littleto    Elaborte on script comments throughout.
#   2018-12-10  kimdan      replaced <user_defined_spcomp_field_name> with <user_defined_sfu_field_name>
#                           Now the tool prints out the final count of the newly created forest units, and the number of records and area for each fu.
#
#-------------------------------------------------------------------------------

import arcpy
import os
from library import ForestUnit_SQL as libSQL
from library import ForestUnit_SQL_SR_Only as libSQL_SR


def main(inputfc, outputfc, forestunittype, OSCfield = "OSC", OSTKGfield = "OSTKG", useecosite = 'false', AGEfield = "OAGE"):

    # Documents the location of the __Main__ file.
    arcpy.AddMessage("Populate Forest Unit version %s"%version)
    arcpy.AddMessage("Script source: " + os.path.abspath(__file__))

    # based on forest unit type, different SQL dictionary will be used
    typeLookup = {"NER Boreal SFU TN021"                   : "libSQL.NER_Boreal_SFU_TN021",                   # Original official version
                  "NER Boreal SFU"                         : "libSQL.NER_Boreal_SFU",                         # Original official version
                  "NER Boreal SFU Nsiah"                   : "libSQL.NER_Boreal_SFU_Nsiah ",                  # Dec 2018 version, by Sam Nsiah
                  # "NER GLSL SFU"                         : "libSQL.NER_GLSL_SFU",                           # Original official version, Depricated. Incorrect
                  # "NER_GLSL_SFU_Nsiah"                   : "libSQL.NER_GLSL_SFU_Nsiah",                         # Mar 2018 version, by Sam Nsiah. Matches "Kun's tool".
                  # "NER Boreal SFU old"                   : "libSQL.NER_Boreal_SFU_old",                     # Not sure what this is (delete?), but it is a Jan 2018 version
                  # "NER Boreal SFU SubAU"                 : "libSQL.NER_Boreal_SubAU",                       # ?
                  # "NER Boreal SFU Abitibi"               : "libSQL.NER_Boreal_SFU_Abitibi",                 # Abitibi only
                  "Eco3E Seven Spc Groups"                 : "libSQL.IMF_3E_proof_of_concept_7_spp",          # This is being applied for eFRI compilation for all province.
                  "NER Boreal Revised SFU 2019 v9"         : "libSQL.NER_Boreal_Revised_SFU_2019_v9",         # Growth and Yield Program, NER SFU revision project (Todd Little, John Parton)
                  "NER Boreal Revised SFU 2019 v9 ROD2023" : "libSQL.NER_Boreal_Revised_SFU_2019_v9_ROD2023", # Sam's version
                  "SR GLSL LG SFU"                         : "libSQL_SR.SR_GLSL_LG_SFU",                      # added in 2023 by Glen Watt. Matches the SQL in Kun's tool
                  "GLSL SFU SQL v1"                        : "libSQL.GLSL_SFU_SQL_V1_03_01_23"                # This is the starting point for the ROD GY GLSL SFU revision project task team
                  }
    fuType = eval(typeLookup[forestunittype])

    # examining existing fields - Need POLYTYPE field and at least one of SC or OSC field
    arcpy.AddMessage("Checking if the input file has the mandatory fields: POLYTYPE and (OSC or SC).")
    existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]

    if 'POLYTYPE' not in existingFields:
        arcpy.AddError("\nPOLYTYPE field does not exist in your input data.\n")
        raise Exception("POLYTYPE field not found in the input table.")

    # new in 2019
    if forestunittype == "NER Boreal SFU SubAU":
        if 'LEADSPC' not in existingFields and 'OLEADSPC' not in existingFields:
            arcpy.AddError("\nEither LEADSPC or OLEADSPC is required to populate sub-analysis unit. \n")
            raise Exception("Either LEADSPC or OLEADSPC is required to populate sub-analysis unit.")
    if forestunittype == "NER Boreal SFU":
        if 'DEVSTAGE' not in existingFields:
            arcpy.AddError("\nDEVSTAGE field is required to populate NER Boreal SFU. \n")
            raise Exception("DEVSTAGE field is required to populate NER Boreal SFU.")

    # Copy the feature class to the ouput location
    arcpy.AddMessage("Copying the input to the output location...")
    outpath = os.path.split(outputfc)[0]
    outname = os.path.split(outputfc)[1]
    arcpy.FeatureClassToFeatureClass_conversion(inputfc,outpath,outname)


    # create a temporary layer file - this layer will be used for selecting and calculating field until finally being exported to a real feature class.
    arcpy.AddMessage("Creating a temporary layer...")
    arcpy.MakeFeatureLayer_management(outputfc,"templyr")


    # create a new field
    newSFU_Field = forestunittype.replace(" ","_")
    if useecosite == 'true': newSFU_Field = newSFU_Field + "_wEco" # used to be + "_withEcosite"
    random_suffix = rand_alphanum_gen(4)
    newSFU_Field = '%s_%s'%(newSFU_Field, random_suffix) # add in a new random suffix in case the tool was run on the same inventory more than one time.

    arcpy.AddMessage("Creating a new field: %s"%newSFU_Field)
    arcpy.AddField_management(in_table = "templyr", field_name = newSFU_Field, field_type = "TEXT", field_length = "10")


    # If ecosite incorporated, add a field to templyr and populate it with the portion of the ecoiste used in the sql
    if useecosite == 'true':
        if 'ECOSITE1' in existingFields:
            ecositeField = "ECOSITE1"
        elif 'PRI_ECO' in existingFields:
            ecositeField = "PRI_ECO"
        else:
            arcpy.AddError("\nECOSITE1 or PRI_ECO field does not exist in your input data.\n")
            raise Exception("ECOSITE1 or PRI_ECO field not found in the input table.")

        newEcoField = 'Ecosite_GeoRangeAndNumber'
        if newEcoField not in existingFields:
            arcpy.AddField_management(in_table = 'templyr', field_name = newEcoField, field_type = "TEXT", field_length = "10")
            arcpy.SelectLayerByAttribute_management("templyr", "NEW_SELECTION", ' "' + ecositeField + '" IS NOT NULL ')
            arcpy.CalculateField_management("templyr", newEcoField, "!" + ecositeField + "![:4]", "PYTHON_9.3")


    # select by attribute and calculate field
    arcpy.AddMessage("Selecting and calculating field...")
    for k, v in sorted(fuType.iteritems(),reverse = False): ## without sorted function, the order will be incorrect.

        # if useecosite is True, incorporate ecosite in the SQL
        if useecosite == 'false':
            sql = v[1]
        else:
            sql = v[1] + v[2]

        # if the SQL contains the string "<user_defined_sfu_field_name>" replace it with the user-defined field name in the SQL criteria.
        sql = sql.replace("<user_defined_sfu_field_name>","\"" + newSFU_Field + "\"")

        # if custom field names are used for AGE
        if AGEfield not in [None,'AGE','']:
            sql = sql.replace('"AGE"', '"' + AGEfield + '"')

        # if custom field names are used for OSC and OSTKG
        if OSCfield not in [None,'OSC','']:
            sql = sql.replace('"OSC"', '"' + OSCfield + '"')
        if OSTKGfield not in [None,'OSTKG','']:
            sql = sql.replace('"OSTKG"', '"' + OSTKGfield + '"')

        # new in Apr 2019
        if forestunittype == "NER Boreal SFU SubAU" and "LEADSPC" not in existingFields:
            if "OLEADSPC" in existingFields:
                sql = sql.replace('LEADSPC', 'OLEADSPC')

        # Select and calcualte field
        arcpy.AddMessage("%s - SQL used:  %s"%(v[0],sql))
        try:
            arcpy.SelectLayerByAttribute_management("templyr", "NEW_SELECTION", sql)
        except:
            arcpy.AddError("\nThere was an error during Select By Attribute process. Make sure that you've run the SPCOMP Parser previous to running this tool.\n")
            raise Exception("There was an error during Select By Attribute process. Make sure that you've run the SPCOMP Parser previous to running this tool.")            

        # quick count
        selection_count = arcpy.GetCount_management("templyr")
        arcpy.AddMessage('%s - records selected: %s\n'%(v[0], selection_count))

        # populating the new forest unit
        arcpy.CalculateField_management("templyr", newSFU_Field, "'" + v[0] + "'", "PYTHON_9.3")

    # clear selection
    arcpy.SelectLayerByAttribute_management("templyr", "CLEAR_SELECTION")

    # final count and area
    arcpy.AddMessage('Summarizing the results...')
    sfu_set = set([v[0] for k, v in fuType.items()]) # using set because some sfu such as LH1 is calculated more than once in Boreal SFU.
    summary_dict = {}
    for sfu in sfu_set:
        sql = '"' + newSFU_Field + '" = ' + "'" + sfu + "'"
        count = 0
        area = 0.0

        with arcpy.da.SearchCursor("templyr",["Shape_Area"],sql) as cursor:
            for row in cursor:
                count += 1
                area += row[0]

        summary_dict[sfu] = [count, int(area)]

    # printing out the final count
    arcpy.AddMessage('SFU, Count, Area')
    for k,v in summary_dict.items():
        arcpy.AddMessage('%s, %s, %s'%(k,v[0],v[1]))

    # clear selection
    arcpy.SelectLayerByAttribute_management("templyr", "CLEAR_SELECTION")

    arcpy.AddMessage("\nExamine the %s field to see the new forest units generated by this tool.\n"%newSFU_Field)




def rand_alphanum_gen(length):
    """
    Generates a random string (with specified length) that consists of A-Z and 0-9.
    """
    import random, string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))



if __name__ == '__main__':
    arcinputfc = arcpy.GetParameterAsText(0)                # toolbox input feature class
    arcoutputfc = arcpy.GetParameterAsText(1)               # toolbox output feature class
    arcforestunittype = str(arcpy.GetParameterAsText(2))    # selection of the forest unit SQL criteria suite (see "typeLookup" above)
    arcOSCfield = str(arcpy.GetParameterAsText(3)).upper()        # selection of a custom site class field from the input feature class
    arcOSTKGfield = str(arcpy.GetParameterAsText(4)).upper()        # optional: not mandatory if boreal SFU. selection of a custom stocking field from the input feature class
    arcuseecosite = str(arcpy.GetParameterAsText(5))        # use the parameter type "boolean" in arc tool - it will give 'true' or 'false'
    try:
        arcAGEfield = str(arcpy.GetParameterAsText(6)).upper()          # optional: selection of a custom age field from the input feature class
    except:
        raise Exception("You may not be using the most recent version of the tool. Try restarting your ArcMap to load the most recent version.")

    main(arcinputfc, arcoutputfc, arcforestunittype, arcOSCfield, arcOSTKGfield, arcuseecosite, arcAGEfield)

