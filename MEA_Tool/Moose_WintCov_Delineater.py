#-------------------------------------------------------------------------------
# Name:        Moose Winter Cover Delineater
# Date Created: 2018 05 28
#
# Author:      kimdan
#
# Workflow:
#   1. copies the input fc to the output location (selecting only where POLYTYPE = FOR)
#   2. create a new text field with user provided field name (such as MooseWinterCover)
#   3. Select using SQLi and populated the new field with Valuei where i is 1, 2... 5.
#   4. Note that SQL2 will over-ride SQL1 and SQL3 will over-ride SQL2 and so on.
#
# Note:
#   By default, the crown closure used is OCCLO. This might need to be changed to CCLO (although this may not be available in the early stage of BMI).
#-------------------------------------------------------------------------------

import arcpy
import os, re
# from library import ForestUnit_SQL as libSQL


def main(inputfc, outputfc, newfieldname, Value1, SQL1, Value2, SQL2, Value3, SQL3, Value4, SQL4, Value5, SQL5, exclude_SQL):

    ##### examining inputs...

    # newfieldname cannot have special characters or a blank space
    if re.match("^[\w\d_]*$",newfieldname):
        if len(newfieldname) < 30:
            pass
        else:
            raise Exception("!! Your new field name is too long !!")
    else:
        raise Exception("!! Your new field name contains spaces or special characters !!")

    # Values and SQLs
    val_list = [Value1,Value2,Value3,Value4,Value5]
    SQL_list = [SQL1,SQL2,SQL3,SQL4,SQL5]

    sql_dict = {}
    for num, val in enumerate(val_list):
        if val != '':
            if SQL_list[num] != '':
                try:
                    sql_dict[num + 1] = [val, SQL_list[num]] # for example, sql_dict would look like {1: ['HVHC', " CE + HE + BF + SW ......."], 2: ['HVLC', " CE + BF + ...." ]}
                except:
                    pass

    arcpy.AddMessage("\nUser SQL inputs as follows:\n%s"%sql_dict)
    if len(exclude_SQL.strip()) > 1:
        arcpy.AddMessage("\nWith the exception of the following area (exclusion from Winter Cover):\n%s"%exclude_SQL)

    ##### done with examining inputs.



    existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]

    if 'POLYTYPE' not in existingFields:
        arcpy.AddError("\nPOLYTYPE field does not exist in your input data.\n")
        raise Exception("POLYTYPE field not found in the input table.")

    # Copy the feature class to the ouput location
    arcpy.AddMessage("\nCopying the input the the output location (only those records with POLYTYPE = FOR will be copied over) ...")
    outpath = os.path.split(outputfc)[0]
    outname = os.path.split(outputfc)[1]
    expression = """ "POLYTYPE" = 'FOR' """
    arcpy.FeatureClassToFeatureClass_conversion(inputfc,outpath,outname,expression)


    # create a temporary layer file - this layer will be used for selecting and calculating field until finally being exported to a real feature class.
    arcpy.AddMessage("\nCreating a temporary layer...")
    arcpy.MakeFeatureLayer_management(outputfc,"templyr")


    # create a new field
    arcpy.AddMessage("Creating a new field: %s"%newfieldname)
    arcpy.AddField_management(in_table = "templyr", field_name = newfieldname, field_type = "TEXT", field_length = "250")


    # select by attribute and calculate field
    arcpy.AddMessage("Selecting and calculating %s field..."%newfieldname)
    for k, v in sql_dict.items():

        value = v[0] # for example, 'HVHC'
        sql = v[1] # for example,  " CE + HE + BF + SW .. > 50"


        # Select and calcualte field
        arcpy.AddMessage("\n%s. Calculating %s: %s"%(k, value, sql))

        try:
            arcpy.SelectLayerByAttribute_management("templyr", "NEW_SELECTION", sql)
        except:
            arcpy.AddError("\nERROR while calculating %s.\nPlease double check the following SQL:\n%s"%(value, sql))
            raise Exception("\nCheck your SQLs and try again.")

        arcpy.CalculateField_management("templyr", newfieldname, "'" + value + "'", "PYTHON_9.3")

    # clear selection
    arcpy.SelectLayerByAttribute_management("templyr", "CLEAR_SELECTION")


    # New in 2023, we've included extra SQL parameter. Areas corresponding to this SQL will be excluded from being winter cover
    if len(exclude_SQL.strip()) > 1:
        arcpy.AddMessage("\nExcluding the area with the following SQL from the Winter Cover selection:\n%s"%exclude_SQL)
        exclude_SQL += ' AND %s IS NOT NULL'%newfieldname
        try:
            arcpy.SelectLayerByAttribute_management("templyr", "NEW_SELECTION", exclude_SQL)
        except:
            arcpy.AddError("\nERROR while calculating %s.\nPlease double check the following SQL:\n%s"%(value, exclude_SQL))
            raise Exception("\nCheck your SQLs and try again.")

        arcpy.CalculateField_management("templyr", newfieldname, "'Excluded from Winter Cover'", "PYTHON_9.3")
        # clear selection
        arcpy.SelectLayerByAttribute_management("templyr", "CLEAR_SELECTION")






if __name__ == '__main__':
    # some of these fields are optional. when the user leaves it blank, it will come out as a blank string: ''
    inputfc = arcpy.GetParameterAsText(0)             # toolbox input feature class
    outputfc = arcpy.GetParameterAsText(1)            # toolbox output feature class
    newfieldname = str(arcpy.GetParameterAsText(2))   # 'MooseWinterCover'
    Value1= str(arcpy.GetParameterAsText(3))  # 'HVHC'        
    SQL1 = str(arcpy.GetParameterAsText(4))   # ("CE"+"HE"+"BF"+"SW") >= ("PW"+"PJ"+"PR"+"SB") AND ("PW"+"PJ"+"PR"+"SB"+"CE"+"HE"+"BF"+"SW")* "OCCLO"/100 >= 60 AND "HT" >= 10
    Value2= str(arcpy.GetParameterAsText(5))  # 'HVLC'          
    SQL2 = str(arcpy.GetParameterAsText(6))   # ("CE"+"HE"+"BF"+"SW") >= ("PW"+"PJ"+"PR"+"SB") AND ("PW"+"PJ"+"PR"+"SB"+"CE"+"HE"+"BF"+"SW")* "OCCLO"/100 >= 30 AND ("PW"+"PJ"+"PR"+"SB"+"CE"+"HE"+"BF"+"SW")* "OCCLO"/100 < 60 AND "HT" >= 10
    Value3= str(arcpy.GetParameterAsText(7))  # 'LVHC'
    SQL3 = str(arcpy.GetParameterAsText(8))   # ("CE"+"HE"+"BF"+"SW") < ("PW"+"PJ"+"PR"+"SB") AND ("PW"+"PJ"+"PR"+"SB"+"CE"+"HE"+"BF"+"SW")* "OCCLO"/100 >= 60 AND "HT" >= 10
    Value4= str(arcpy.GetParameterAsText(9))  # 'LVLC'        
    SQL4 = str(arcpy.GetParameterAsText(10))  # ("CE"+"HE"+"BF"+"SW") < ("PW"+"PJ"+"PR"+"SB") AND ("PW"+"PJ"+"PR"+"SB"+"CE"+"HE"+"BF"+"SW")* "OCCLO"/100 >= 30 AND ("PW"+"PJ"+"PR"+"SB"+"CE"+"HE"+"BF"+"SW")* "OCCLO"/100 < 60 AND "HT" >= 10
    Value5= str(arcpy.GetParameterAsText(11))          
    SQL5 = str(arcpy.GetParameterAsText(12))
    exclude_SQL = str(arcpy.GetParameterAsText(13)) # new in 2023 - by default CE + CW > 0 AND SC in (3,4) AND (PRI_ECO LIKE '%129%' OR PRI_ECO LIKE '%224%')

    # arcpy.AddMessage('%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n'%(inputfc, outputfc, newfieldname, Value1, SQL1, Value2, SQL2, Value3, SQL3, Value4, SQL4, Value5, SQL5))

    main(inputfc, outputfc, newfieldname, Value1, SQL1, Value2, SQL2, Value3, SQL3, Value4, SQL4, Value5, SQL5, exclude_SQL)

