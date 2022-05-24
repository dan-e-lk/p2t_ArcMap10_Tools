version = '2022.05'
# Area-capped and area-weighted random block selection tool.
# Area-capped means instead of selecting a target number of records, the tool selects 
# 	a number of record until the sum of the selected area meets the target area.
# Area-weighted means the greater the area, the greater the chance that it will be picked.
# Usually the target area is 10% of the total area of all records
# 
# Workflow
# 1.	Input: shapefile or geodatabase that contains FTG-AR block spatial data. Export this data into a feature class.
# 2.	Calculate the total area of all blocks.
# 3.	Calculate the Target Area (10% of the Total Area)
# 4.	Test if the selection can meet the target area after filtering out the polygons that does not meet minimum area
# 5.	Start randomly selecting (while giving area-weighted discrimination) FTG-AR blocks until the cumulative area of selected blocks reach the target area.
#		note that random.choices() couldn't be used because this is python v2. Instead, the cumulative weight of each polygon is assigned.
# 6.	Fill out the selection result in the "RAP_rand_select" field.
#
# Prerequisites
# 1. Number of records must be greater than 5 (the script will check this)
# 2. The input must be shp or, preferably, fc, and must have "Shape_Area" field with values filled out in sq meter (the script will check this).
#
# the initial version of this tool was developed on Jan 2022 by Daniel Kim
# v2 update (Mar 2022) includes the option for the end users to create a subset (priority area) where 
#   the tool selects records only from that subset.


import arcpy
import random, os, traceback

def rand_select(input_shape, output_fc, target_area_perc, minimum_area, selection_sql):
	"""This is the main function of this script.
	by default, target area should be 10 (meaning 10% of the total area)
	"""
	arcprint("\n### Executing RAP Random Selection Tool v.%s ###\n"%version)
	arcprint(" Input file: %s"%input_shape)
	target_area_perc = float(target_area_perc)
	minimum_area = float(minimum_area) # !!! note that this number is in hectare!!


	### make sure selection SQL is a valid SQL. We do this by try selecting the records and make sure more than 1 records are selected.
	if len(selection_sql) > 0:
		arcprint("\n  Checking the Priority Area Selection SQL...")
		arcprint("    %s"%selection_sql)
		arcpy.MakeFeatureLayer_management(input_shape, "temp_lyr")
		try:
			arcpy.SelectLayerByAttribute_management("temp_lyr", "NEW_SELECTION", selection_sql)
		except:
			arcprint("\nThere's an issue with Priority Area Selection SQL. Please 'Verify' the SQL in its Query Builder.", 'err')
			raise Exception("Error on the syntax of Priority Area Selection SQL")

		count = int(arcpy.GetCount_management("temp_lyr")[0]) # this is the typical arcgis bs. count result comes out as a string not a number.
		arcprint("    %s records selected"%count)
		if count<1:
			arcprint("\nThere's an issue with Priority Area Selection SQL. Make sure your SQL selects at least one record.", 'warn')
			raise Exception("The SQL expression was verified successfully, but no records were selected")

		# clear selection
		arcpy.SelectLayerByAttribute_management("temp_lyr", "CLEAR_SELECTION")			



	### export
	arcprint("\nExporting...")
	arcpy.FeatureClassToFeatureClass_conversion(in_features=input_shape, out_path=os.path.split(output_fc)[0], out_name=os.path.split(output_fc)[1])

	try:
		### examining the data
		arcprint("\nExamining the data...")
		sr = arcpy.Describe(output_fc).spatialReference
		arcprint(" Spatial Reference: %s, %s"%(sr.name, sr.type))
		lin_unit = sr.linearUnitName
		arcprint(" Linear Unit: %s"%lin_unit) # returns "Meter" if Shape_Area is measured in meter sq, it will return empty string if measured with angle
		# end the script if the area is not measured in meters.
		if lin_unit != 'Meter':
			arcprint("Your input's linear unit is not in Meter. Save(export) your input data as feature class using a projected coordinate system and re-run the tool." ,'err')

		existingFields = [str(f.name) for f in arcpy.ListFields(output_fc)]
		arcprint(" List of fields: %s"%existingFields)
		# end the script if there's no "Shape_Area" field
		if "Shape_Area" not in existingFields:
			arcprint("'Shape_Area' field not found. Save(export) your input data as feature class using a projected coordinate system and re-run the tool." ,'err')
		# need Object ID field
		OID_fieldname = arcpy.Describe(output_fc).OIDFieldName # usually 'FID' for shapefile and 'OBJECTID' for fc
		arcprint(" ObjectID Fieldname: %s"%OID_fieldname)


		### grab data - we just need the OID and Shape_Area
		arcprint("\nGrabbing data...")
		records = [{OID_fieldname: row[0], "Shape_Area": row[1]} for row in arcpy.da.SearchCursor(output_fc, [OID_fieldname, "Shape_Area"])]
		num_records = len(records)
		if num_records < 5:
			arcprint("Only %s records found. You should have at least 5 records to have this tool run properly."%num_records,'err')
		arcprint("Total number of records: %s"%num_records)

		# if priority area selection is provided...
		if len(selection_sql) > 0:
			p_records = [{OID_fieldname: row[0], "Shape_Area": row[1]} for row in arcpy.da.SearchCursor(output_fc, [OID_fieldname, "Shape_Area"], selection_sql)]
			p_num_records = len(p_records)
			arcprint("Number of priority area selection records: %s"%p_num_records)


		### calculate the total area and target area
		arcprint("\nCalculating Areas...")	
		total_area = sum([rec["Shape_Area"] for rec in records]) # value in m2
		total_area_ha = total_area/10000  # value in hectare
		arcprint(" Total Area: %s ha"%total_area_ha)
		target_area = total_area*target_area_perc/100 # in m2
		target_area_ha = target_area/10000 # in hectare
		arcprint(" Target Area = Total Area x %s%% = %s ha"%(target_area_perc, target_area_ha))

		# if priority area selection is provided...
		if len(selection_sql) > 0:
			p_total_area = sum([rec["Shape_Area"] for rec in p_records]) # value in m2
			p_total_area_ha = p_total_area/10000  # value in hectare


		### Check if there are enough records greater than the minimum area to meet the target area requirement
		if minimum_area > 0:
			# selecting only those areas that are greater than minimum area requirement
			if len(selection_sql) > 0:
				areas_over_min_area = [rec["Shape_Area"] for rec in p_records if rec["Shape_Area"] > minimum_area*10000]
				arcprint(" %s of %s priority selection area records meet the minimum area requirement of %s ha."%(len(areas_over_min_area), p_num_records, minimum_area))
			else:
				areas_over_min_area = [rec["Shape_Area"] for rec in records if rec["Shape_Area"] > minimum_area*10000]
				arcprint(" %s of %s records meet the minimum area requirement of %s ha."%(len(areas_over_min_area), num_records, minimum_area))
			if sum(areas_over_min_area)*0.9<target_area:
				# sum of the areas that meets the minimum area req should be much greater than the target area.
				arcprint("There are not enough polygons greater than the minimum area requirement to reach the target area.", 'err')
				raise Exception("The sum of the areas that meets the minimum area req should be much greater than the target area.")


		### Add cumulative weight (proportional to the area) to each records.
		arcprint("\nAdding cumulative weights proportional to each area...")	
		cum_area = 0 # number between 0 and total area
		# if priority area selection is provided, reassign the values of 'records' with that of 'p_records'
		if len(selection_sql) > 0:
			records = p_records
			num_records = p_num_records
		# assign cumulative weight values to each record
		for rec in records:
			rec_area = rec['Shape_Area']
			cum_area += rec_area
			if len(selection_sql) > 0:
				cum_weight = cum_area/p_total_area # will always be a number between 0 and 1
			else:
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


		# adding a new field to show the selection results
		newfieldname = 'RAP_rand_select' # the name of the new field filled with values 1 or 0.
		if newfieldname in existingFields: # just in case that fieldname already exists
			newfieldname = newfieldname + rand_alphanum_gen(4)
		arcprint(" Adding a new field called %s"%newfieldname)
		arcpy.AddField_management(in_table = output_fc, field_name = newfieldname, field_type = "SHORT")

		# update the new field with selection results
		arcprint("\nFilling out the %s field with the selection results..."%newfieldname)
		with arcpy.da.UpdateCursor(output_fc, [OID_fieldname, newfieldname]) as cursor:
		    # For each row, if the objectid matches with that of the selected records,
		    # fill out the new field with 1. if no match, fill it out with 0
		    for row in cursor:
		        if row[0] in selected_recs:
		        	row[1] = 1
		        else:
		        	row[1] = 0
		        cursor.updateRow(row)

	except Exception:
		arcprint(traceback.format_exc(), 'err')
		# delete the output if the run was unsuccessful
		try:
			arcprint("Cleaning up...")
			arcpy.Delete_management(output_fc)
		except:
			pass





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



def rand_alphanum_gen(length):
    """
    Generates a random string (with specified length) that consists of A-Z and 0-9.
    """
    import random, string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))



if __name__ == '__main__':
    input_shape = arcpy.GetParameterAsText(0) # this should be AR's FTG file in shp or fc
    output_fc = arcpy.GetParameterAsText(1) # user specified path and name of the output fc
    target_area_perc = arcpy.GetParameterAsText(2)
    minimum_area = arcpy.GetParameterAsText(3) # minimum area in hectares. 8ha should be the minimum area.
    selection_sql = arcpy.GetParameterAsText(4) # optional. select SQL

    rand_select(input_shape, output_fc, target_area_perc, minimum_area, selection_sql)
