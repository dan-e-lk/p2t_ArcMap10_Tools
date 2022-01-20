version = '1.0'
# Area-capped and area-weighted random block selection tool.
# Area-capped means instead of selecting a target number of records, the tool selects 
# 	a number of record until the sum of the selected area meets the target area.
# Area-weighted means the greater the area, the greater the chance that it will be picked.
# Usually the target area is 10% of the total area of all records
# 
# Workflow
# 1.	Input: shapefile or geodatabase that contains FTG-AR block spatial data.
# 2.	Calculate the total area of all blocks.
# 3.	Calculate the Target Area (10% of the Total Area)
# 4.	Filter out polygons that does not meet minimum area
# 5.	Start randomly selecting (while giving area-weighted discrimination) FTG-AR blocks until the cumulative area of selected blocks reach the target area.
#		note that random.choices() couldn't be used because this is python v2. Instead, the cumulative weight of each polygon is assigned.
# 6.	Export/output the selected blocks.
#
# Prerequisites
# 1. Number of records must be greater than 5 (the script will check this)
# 2. The input must be shp or, preferably, fc, and must have "Shape_Area" field with values filled out in sq meter (the script will check this).
#
# the initial version of this tool was developed on Jan 2022 by Daniel Kim

import arcpy
import random

def rand_select(input_shape, output_fc, target_area_perc, minimum_area):
	"""This is the main function of this script.
	by default, target area should be 10 (meaning 10% of the total area)
	"""
	arcprint("\n### Executing RAP Random Selection Tool v.%s ###\n"%version)
	arcprint(" Input file: %s"%input_shape)
	target_area_perc = float(target_area_perc)
	minimum_area = float(minimum_area) # !!! note that this number is in hectare!!

	### examine the input
	sr = arcpy.Describe(input_shape).spatialReference
	arcprint(" Spatial Reference: %s, %s"%(sr.name, sr.type))
	lin_unit = sr.linearUnitName
	arcprint(" Linear Unit: %s"%lin_unit) # returns "Meter" if Shape_Area is measured in meter sq, it will return empty string if measured with angle
	# end the script if the area is not measured in meters.
	if lin_unit != 'Meter':
		arcprint("Your input's linear unit is not in Meter. Save(export) your input data as feature class using a projected coordinate system and re-run the tool." ,'err')

	existingFields = [str(f.name) for f in arcpy.ListFields(input_shape)]
	arcprint(" List of fields: %s"%existingFields)
	# end the script if there's no "Shape_Area" field
	if "Shape_Area" not in existingFields:
		arcprint("'Shape_Area' field not found. Save(export) your input data as feature class using a projected coordinate system and re-run the tool." ,'err')
	# need Object ID field
	OID_fieldname = arcpy.Describe(input_shape).OIDFieldName # usually 'FID' for shapefile and 'OBJECTID' for fc
	arcprint(" ObjectID Fieldname: %s"%OID_fieldname)


	### grab data - we just need the OID and Shape_Area
	arcprint("\nGrabbing data...")
	records = [{OID_fieldname: row[0], "Shape_Area": row[1]} for row in arcpy.da.SearchCursor(input_shape, [OID_fieldname, "Shape_Area"])]
	num_records = len(records)
	if num_records < 5:
		arcprint("Only %s records found. You should have at least 5 records to have this tool run properly."%num_records,'err')
	arcprint(" %s records found."%num_records)


	### calculate the total area and target area
	arcprint("\nCalculating Areas...")	
	total_area = sum([rec["Shape_Area"] for rec in records]) # value in m2
	total_area_ha = total_area/10000  # value in hectare
	arcprint(" Total Area: %s ha"%total_area_ha)
	target_area = total_area*target_area_perc/100 # in m2
	target_area_ha = target_area/10000 # in hectare
	arcprint(" Target Area = Total Area x %s%% = %s ha"%(target_area_perc, target_area_ha))


	### Check if there are enough records greater than the minimum area to meet the target area requirement
	if minimum_area > 0:
		# selecting only those areas that are greater than minimum area requirement
		areas_over_min_area = [rec["Shape_Area"] for rec in records if rec["Shape_Area"] > minimum_area*10000]
		arcprint(" %s of %s records meet the minimum area requirement of %s ha."%(len(areas_over_min_area), num_records, minimum_area))
		if sum(areas_over_min_area)*0.8<target_area:
			# sum of the areas over minimum area req should be much greater than target area.
			arcprint("There are not enough polygons greater than the minimum area requirement to reach the target area.", 'err')


	### Add cumulative weight (proportional to the area) to each records.
	arcprint("\nAdding cumulative weights proportional to each area...")	
	cum_area = 0 # number between 0 and total area
	for rec in records:
		rec_area = rec['Shape_Area']
		cum_area += rec_area
		cum_weight = cum_area/total_area # will always be a number between 0 and 1
		rec['cum_weight'] = cum_weight
	
	# print out the weights
	arcprint("\n%s  \tCumulative Weight"%OID_fieldname[:3])
	if num_records < 10:
		for rec in records:
			arcprint("%s \t\t%s"%(rec[OID_fieldname], rec['cum_weight']))
	else:
		for count, rec in enumerate(records):
			if count<5:
				arcprint("%s \t\t%s"%(rec[OID_fieldname], rec['cum_weight']))
			elif count == 5:
				arcprint("...")
			elif count > num_records - 3:
				arcprint("%s \t\t%s"%(rec[OID_fieldname], rec['cum_weight']))


	### random selection - randomly select until it meets the target area
	arcprint("\nRandomly selecting eligible records...")
	selected_recs = [] # list of ObjectIDs
	cum_area = 0
	trial = 1
	max_trial = 10000 # 10,000 trials would take about 0.8 sec if your input is ~300 records, but it shouldn't take more than 100 tries.
	while trial < max_trial and cum_area < target_area:
		rand = random.random() # random number between 0 and 1
		for rec in records:
			if rand < rec["cum_weight"]:
				# This is the selected record
				oid = rec[OID_fieldname]
				area = rec["Shape_Area"]
				if oid not in selected_recs and area > minimum_area*10000:
					# add to the list of selected only if it's not already selected
					selected_recs.append(oid)
					cum_area += area
				break # out of this for loop
		trial += 1
	# report on it
	if cum_area < target_area:
		arcprint("Failed to meet target area after %s tries. "%trial +\
			"This is most likely because there are too many polygons not meeting the minimum area requirement.",'warn')
	else:
		arcprint("\n Successfully selected polygons while meeting all the requirements!\n")

	arcprint(' Total area of selected records: %sha (%s%%)'%(cum_area/10000, cum_area*100/total_area))
	arcprint(' Number of selected records: %s'%len(selected_recs))
	arcprint(' ID of Selected records: %s'%selected_recs)
	arcprint(' Total trials: %s'%trial)







def arcprint(msg, msgtype = 'msg'):
    """ I got lazy typing out arcpy.AddMessage.
    msg = arcpy.AddMessage
    warn = arcpy.AddWarning
    err = arcpy.AddError
    """
    if msgtype == 'msg':
        arcpy.AddMessage(msg)
    elif msgtype == 'warn':
        arcpy.AddWarning(msg)
    elif msgtype == 'err':
        arcpy.AddError(msg)



if __name__ == '__main__':
    input_shape = arcpy.GetParameterAsText(0) # this should be AR's FTG file in shp or fc
    output_fc = arcpy.GetParameterAsText(1) # user specified path and name of the output fc
    target_area_perc = arcpy.GetParameterAsText(2)
    minimum_area = arcpy.GetParameterAsText(3) # minimum area in hectares. 8ha should be the minimum area.


    rand_select(input_shape, output_fc, target_area_perc, minimum_area)
