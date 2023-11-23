import FishSpcParser as fsp
import arcpy

version = 'beta1'

#############################          INPUT           ###########################

fc = arcpy.GetParameterAsText(0) # ARA Summary Table
field = arcpy.GetParameterAsText(1)
summarize_only = arcpy.GetParameterAsText(2) # boolean
outputfc = arcpy.GetParameterAsText(3)
max_num_spc = arcpy.GetParameterAsText(4) # must a a positive integer (zero not accepted)
limit_fieldname_to_10char = arcpy.GetParameterAsText(5) # boolean

##################################################################################

summarize_only = True if summarize_only == 'true' else False
limit_fieldname_to_10char = True if limit_fieldname_to_10char == 'true' else False

arcpy.AddMessage('Tool version = %s'%version)
myFish = fsp.FishSpcParser(fc,field)
myFish.summarize_fish()
myFish.print_summary()

if not summarize_only:
	myFish.export(outputfc)
	myFish.create_new_fields(outputfc, max_num_spc, limit_fieldname_to_10char)
	myFish.populate_fields(outputfc)


arcpy.AddMessage('\nCompleted!!\n')
