# This script uses Plonski's (MargaretPenner's coefficients) equation to derive Site Index from Site Class and Leading Species.
# originally it was a simple code block in calculated field, but I made it into a tool on ArcMap.
"""
Original form of this script:
in python in ArcMap, (updated 2025-02-11)"""

code_blk = """
def SCtoSI(SC,leadspc):
    leadspc = leadspc.upper()
    if leadspc == 'PW':
        si = -5.354*SC + 24.536
    elif leadspc == 'PR':
        si = -3.31*SC + 23.06
    elif leadspc in ['PJ','PS']:
        si = -3.082*SC + 22.548
    elif leadspc in ['SX','SB','SR','SW','BF','CE','CW','LA']:
        si = -3.084*SC + 15.256
    elif leadspc in ['BW']:
        si = -2.76*SC + 22.14
    elif leadspc in ['PO','PL','PT','PB','WI']:
        si = -3.876*SC + 28.904
    else:
        si = -2.47*SC + 18.78
    return si
""" # make sure this code block is indented with spaces instead of tab (that's the only way arcmap would accept it)

"""
0. If not exist, create PLONSKI_SI field.
1. Open Attribute Table, then Select where POLYTYPE = 'FOR' AND SC IS NOT NULL
2. Right click on the fieldname and Calculate Field
3. Click Python radio button.
4. Click to check the box next to "Show Code Block"
5. Enter the above code (def SCtoSI....) in the code block text box.
6. In the Expression box, enter: SCtoSI(!SC!, !LEADSPC!)
7. Click OK.
"""



def SCtoSI(inputfc,SC_fname,LEADSPC_fname):
	# check field. count records.
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
	count_orig = int(arcpy.management.GetCount(inputfc)[0])

	# if not exist, create PLONSKI_SI field
	SI_fname = "PLONSKI_SI"
	if SI_fname not in existingFields:
		arcpy.AddMessage("Adding Field: %s"%SI_fname)
		arcpy.AddField_management(in_table = inputfc, field_name = SI_fname, field_type = "FLOAT")

	# Make Layer, then Select where SC IS NOT NULL AND LEADSPC IS NOT NULL
	select_sql = "%s IS NOT NULL AND %s NOT IN ('',' ','  ') AND %s IS NOT NULL"%(SC_fname,LEADSPC_fname,LEADSPC_fname)
	arcpy.AddMessage("Selecting where %s"%select_sql)
	arcpy.management.MakeFeatureLayer(inputfc, "temp_lyr")
	arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", select_sql)
	count_select = int(arcpy.management.GetCount(inputfc)[0])
	arcpy.AddMessage("Selected %s out of %srecords"%(count_select,count_orig))

	# Calculate Field with code block.
	arcpy.AddMessage("Calculating Site Index...")
	arcpy.AddMessage(code_blk)
	expression = "SCtoSI(!%s!,!%s!)"%(SC_fname,LEADSPC_fname)
	arcpy.management.CalculateField("temp_lyr", SI_fname, expression, "PYTHON", code_block=code_blk)

	arcpy.AddMessage("SC to SI conversion complete!")



if __name__ == '__main__':
	inputfc = arcpy.GetParameterAsText(0)
	SC_fname = arcpy.GetParameterAsText(1)
	LEADSPC_fname = arcpy.GetParameterAsText(2)

	SCtoSI(inputfc,SC_fname,LEADSPC_fname)