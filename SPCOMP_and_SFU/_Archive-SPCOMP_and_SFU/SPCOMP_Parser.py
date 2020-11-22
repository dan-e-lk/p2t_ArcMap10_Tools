#-------------------------------------------------------------------------------
# Name:         FU_Classifier
# Purpose:      This tool can be used to check the FU.
#               It makes a copy of a BMI or PCI, creates new fields for every possible species,
#               and translates the SPCOMP into species percentages.
#
# Author:      kimdan
#
# Created:     25/09/2017
# Copyright:   (c) kimdan 2017
#-------------------------------------------------------------------------------

import Reference as R # Reference.py should be located in the same folder as this file.
import arcpy, os



### setting the workspace
##arcpy.env.workspace = os.path.split(outputfc)[0]

def spParse(inputfc,outputfc,spfield):
    # Copy the input bmi to the location of choice
    arcpy.AddMessage("Making a copy of the input feature class...")
    arcpy.FeatureClassToFeatureClass_conversion(in_features=inputfc, out_path=os.path.split(outputfc)[0], out_name=os.path.split(outputfc)[1])


    # Create a complete list of species and the corresponding list of field names

    completeSpList = R.SpcListInterp + R.SpcListOther # this is our complete species list.
    completeSpList.sort()

    completeFldList = completeSpList
    completeFldList[completeFldList.index('BY')] = '_BY'
    completeFldList[completeFldList.index('OR')] = '_OR'


    # Creating fields for each species
    existingFields = [str(f.name).upper() for f in arcpy.ListFields(outputfc)]

    for sp in completeFldList:
        if sp not in existingFields:
            arcpy.AddMessage("Creating a new field: %s"%sp)
            arcpy.AddField_management(in_table = outputfc, field_name = sp, field_type = "SHORT")
        else:
            arcpy.AddMessage("Creating a new field: %s - field already exists!"%sp)


    # populate zeros for all the newly created fields

    arcpy.AddMessage("populating the newly created fields with default zero...")
    with arcpy.da.UpdateCursor(outputfc, completeFldList) as cursor:
        for row in cursor:
            for i in range(len(completeFldList)):
                row[i] = 0
            cursor.updateRow(row)  ## Now all the newly populated fields are zero by default


    # Creating other fields
    fieldname = 'SPC_Check'
    completeFldList.append(fieldname)
    if fieldname not in existingFields:
        arcpy.AddMessage("Creating a new field: %s"%fieldname)
        arcpy.AddField_management(in_table = outputfc, field_name = fieldname, field_type = "TEXT", field_length = "150")

    ##fieldname = "NER_FU"
    ##completeFldList.append(fieldname)
    ##if fieldname not in existingFields:
    ##    arcpy.AddMessage("Creating a new field: %s"%fieldname)
    ##    arcpy.AddField_management(in_table = outputfc, field_name = fieldname, field_type = "TEXT", field_length = "20")


    # Check SPCOMP or OSPCOMP field. if passed, populate the fields with percentages  if not passed the check, write the error message to the SPC_Check field

    completeFldList.append(spfield)

    arcpy.AddMessage("Populating species fields with percentage values...")
    f = completeFldList
    with arcpy.da.UpdateCursor(outputfc, f) as cursor:
        for row in cursor:
            if row[f.index(spfield)] not in [None, '', ' ']: ## if SPCOMP field is none, the spcVal function won't work
                ValResult = R.spcVal(row[f.index(spfield)],spfield) ## ValResult example: ["Pass", {'AX':60,'CW':40}]
                if ValResult[0] != "Error":
                    for k, v in ValResult[1].iteritems():
                        try:
                            row[f.index(k)] = v ## for example, k = 'AX' and v = 60
                        except:
                            row[f.index("_" + k)] = v ## for field names such as _BY
                    row[f.index(fieldname)] = "Pass"
                else:
                    row[f.index(fieldname)] = "%s: %s"%(ValResult[0], ValResult[1])
            cursor.updateRow(row)


if __name__ == '__main__':
    arcinputfc = arcpy.GetParameterAsText(0) # this should be bmi or pci
    arcoutputfc = arcpy.GetParameterAsText(1) # where to save your work
    arcspfield = arcpy.GetParameterAsText(2) # 2009 or 2017

    spParse(arcinputfc,arcoutputfc,arcspfield)




