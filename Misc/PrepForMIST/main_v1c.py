# this is the main python script for "BMI to MIST" ArcMap Tool.
version = '1c'

# Workflow:
# 1. copies the input bmi to an output location. it selects certain polytype, ownership and devstage.
# 2. if there are missing mandatory fields, this tool creates them
# 3. populates mandatory fields and corrects each record to mimic old BMI.

print("importing arcpy...")
import os, arcpy, datetime
import lut



def main(input_bmi, output_folder, submu):
	"""
	input_bmi = path to the bmi feature class.
	output_folder = where you want to save your output MIST-ready file. Must be the path to an existing folder.
	submu = an existing field within the input_bmi the value of which will be used to populate SUBMU field in the output dbf file. (submu will most likely be OMZ or SMZ.)
	"""

	###########################      House-keeping Stuff      #################################

	datetime_today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M') # eg. '2018-29-09 15:29'
	unique_suffix = datetime.datetime.now().strftime('%Y%m%d%H%M') # eg. '201801181529'
	submu = submu.upper()

	# creating a new output folder
	output_folder = os.path.join(output_folder,'BMI4MIST_' + unique_suffix)
	try:
		os.makedirs(output_folder)
	except:
		raise Exception('%s  already exists. Delete the existing folder and try again.'%output_folder)

	# creating a log text file
	logfilename = os.path.join(output_folder,'logfile.txt')
	log = open(logfilename,'w')

	# any msg that's generated throughout this script will be appended to msg variable.
	arcpy.AddMessage('Tool version = %s'%version)
	logmsg = 'Log File for Mist Prep Tool version %s'%version
	logmsg += '\n\nDate and Time: %s'%datetime_today
	logmsg += '\n\nUser Inputs:\n\tInput BMI: %s\n\tOutput Folder: %s\n\tSub Unit: %s\n\n'%(input_bmi,output_folder,submu)

	# End of the house keeping stuff.


	########################      Copying and Editing the BMI     #############################

	try:
		# Creating a new workspace gdb
		logmsg += print2("Creating a new gdb in the output folder...")

		out_gdb_name = 'BMI4MIST_' + unique_suffix
		arcpy.CreateFileGDB_management(out_folder_path=output_folder, out_name=out_gdb_name, out_version="CURRENT")
		out_gdb_path = os.path.join(output_folder,out_gdb_name + '.gdb')

		# Copying the original to the new workspace
		logmsg += print2("\n**Selecting OWNER = 1 and POLYTYPE = FOR and DEVSTAGE NOT IN ('DEPHARV','DEPNAT','NEWNAT','NEWPLANT','NEWSEED') and AVAIL = 'A'. \n\nCopying over the input to the output gdb...")

		newfc_name = "B4M"
		arcpy.FeatureClassToFeatureClass_conversion(in_features=input_bmi, out_path=out_gdb_path, out_name=newfc_name, where_clause="POLYTYPE = 'FOR' AND OWNER ='1' AND DEVSTAGE NOT IN ('DEPHARV','DEPNAT','NEWNAT','NEWPLANT','NEWSEED') AND AVAIL = 'A' ")
		newfc_path = os.path.join(out_gdb_path,newfc_name) # this is the new fc generated.
		logmsg += print2("New feature class has been created here:\n%s"%newfc_path)

		# list of existing fields
		existingFields = [str(f.name).upper() for f in arcpy.ListFields(newfc_path)]

		# check mandatory fields for MIST
		# if mandatory fields are missing, populate them.
		newly_created_flds = []
		for k,v in lut.req_fields.items():

			req_field_name = v[0]
			fieldtype = v[2]
			if req_field_name not in existingFields:

				# first, checking if the missing field can be populated based on existing fields
				# for example, if wg field is missing, we must check if LEADSPC field exists.
				try:
					alt_field = lut.alternate_field[req_field_name]
					if alt_field not in existingFields:
						logmsg += print2("if both %s and %s fields are missing, the program cannot continue."%(req_field_name,alt_field))
						# terminate the program.
						raise Exception("if both %s and %s fields are missing, the program cannot continue."%(req_field_name,alt_field))
				except KeyError:
					pass


				# creating new field (req_field) only if it doesn't already exist.
				if fieldtype == 'TEXT':
					fieldlength = str(v[1])
				else:
					fieldlength = ""
				logmsg += print2("\n**Adding a new field: %s"%(req_field_name))
				arcpy.AddField_management(in_table=newfc_path, field_name=req_field_name, field_type=fieldtype, field_precision="", field_scale="", field_length=fieldlength)
				newly_created_flds.append(req_field_name)

				# at this point, you've created all the required fields.


		# Populating and re-calculating all the required fields
		to_be_recalculated = ['DEVSTAGE','AREA','AGESTR','ECOPCT1','ECOPCT2','SI','SISRC','MGMTSTG','SUBMU','ECOSITE1','ECOSITE2','WG','AGE','STKG','OMZ','YRUPD'] # these are the required fields that will be repopulated
		other_fields = ['PRI_ECO','SEC_ECO','SHAPE_AREA','NEXTSTG','LEADSPC','YIELD','YRSOURCE'] # these are the fields used to re-calculate the required fields.
		f = to_be_recalculated + other_fields
		if submu not in f: f.append(submu) # submu is most likely be OMZ or SMZ.

		logmsg += print2("""
\n\nMaking the following changes to the inventory...
** DEVSTAGE: changing EST... to FTG..., and changing NAT to FTGNAT.
** AREA: Populating AREA field from SHAPE_AREA - leaving it as meter squared
** AGESTR: Populating AGESTR field with 'E' (where POLYTYPE = FOR)
** ECOPCT1 & 2: if both PRI_ECO and SEC_ECO are populated, ECOPCT1 = 80 and ECOPCT2 = 20
\tif only PRI_ECO is populated, ECOPCT1 = 100 and ECOPCT2 = 0
** SI: Populating SI using the values from YIELD field.
** SISRC: Populating SISRC field with 'ASSIGNED'
** MGMTSTG: Populating MGMTSTG field using the values from NEXTSTG field. If NEXTSTG = 'CONVENT', set MGMTSTG = 'CONVENTN'
** SUBMU: Populating SUBMU using the existing values from %s.
** ECOSTIE1: Populating ECOSITE1 field using the values from PRI_ECO field.
** WG: Populating WG field using the values from LEADSPC field,
\tand replace Ab to AX, Bd to OH, Cw to Ce, Ew to OH, Ob to OH, Pl to PO, Pb to PO, Pt to PO, and Sn to SX.
** AGE: If age > 250 then age = 250. i.e. AGE caps at 250.
** STKG: If STKG > 1, then STKG = 1
** OMZ: OMZ will be populated (over-written) using the user input for SUBMU.
** YRUPD: YRUPD will be populated using YRSOURCE.

			"""%(str(submu)))

		record_count = 0
		area_count = 0.0
		with arcpy.da.UpdateCursor(newfc_path,f) as cursor:
			for row in cursor:

				record_count += 1
				# arcpy.AddMessage(record_count)

				# populating submu using the user-specified field.
				submu_value = str(row[f.index(submu)])
				if len(submu_value) > 5: submu_value = submu_value[:5]
				row[f.index('SUBMU')] = submu_value

				# checking devstage
				devstage = row[f.index('DEVSTAGE')]
				if devstage[:3] == 'EST':
					row[f.index('DEVSTAGE')] = devstage.replace('EST','FTG')
				if devstage == 'NAT':
					row[f.index('DEVSTAGE')] = 'FTGNAT'


				# populating Area field - leaving it as meter squared.
				row[f.index('AREA')] = row[f.index('SHAPE_AREA')]
				area_count += row[f.index('AREA')]


				# Populating AGESTR field with 'E'
				row[f.index('AGESTR')] = 'E' # at this point, all the records are POLYTYPE = FOR


				# Populating ECOSITE1 and 2
				row[f.index('ECOSITE1')] = row[f.index('PRI_ECO')]
				row[f.index('ECOSITE2')] = row[f.index('SEC_ECO')]


				# Populating ECOPCT1 and 2
				ecosite1 = row[f.index('ECOSITE1')]
				ecosite2 = row[f.index('ECOSITE2')]
				if ecosite2 not in [None,'', ' ']:
					row[f.index('ECOPCT1')] = 80
					row[f.index('ECOPCT2')] = 20
				else:
					row[f.index('ECOPCT1')] = 100
					row[f.index('ECOPCT2')] = 0


				# Populating SI from YIELD field. SI can only take up to 5 characters.
				yld = row[f.index('YIELD')]
				if yld != None and len(yld) > 5:
					row[f.index('SI')] = yld[:5]
				else:
					row[f.index('SI')] = yld


				# Populating SISRC with 'ASSIGNED' value
				row[f.index('SISRC')] = 'ASSIGNED'


				# Populating MGMTSTG using NEXTSTG field. If NEXTSTG = 'CONVENT', set MGMTSTG = 'CONVENTN'
				if row[f.index('NEXTSTG')] == 'CONVENT':
					row[f.index('MGMTSTG')] = 'CONVENTN'
				else:
					row[f.index('MGMTSTG')] = row[f.index('NEXTSTG')]


				# Populating WG using LEADSPC field (and using old species codes)
				leadspc = row[f.index('LEADSPC')]
				if leadspc == 'Ab':
					row[f.index('WG')] = 'AX'

				elif leadspc in ['Bd','Ew','Ob']:
					row[f.index('WG')] = 'OH'

				elif leadspc == 'Cw':
					row[f.index('WG')] = 'Ce'

				elif leadspc in ['Pl','Pt','Pb']:
					row[f.index('WG')] = 'PO'

				elif leadspc == 'Sn':
					row[f.index('WG')] = 'SX'

				else:
					row[f.index('WG')] = leadspc

				# AGE caps at 250
				if row[f.index('AGE')] > 250:
					row[f.index('AGE')] = 250

				# STKG caps at 1
				if row[f.index('STKG')] > 1:
					row[f.index('STKG')] = 1



				# # Populating 'AGS','AGS_LGE','AGS_MED','AGS_POLE','AGS_SML','AGSP','DEFER','UGS','UGS_LGE','UGS_MED','UGS_POLE','UGS_SML','UGSP' with zeros
				# for i in [row[f.index('AGS')],row[f.index('AGS_LGE')],row[f.index('AGS_MED')],row[f.index('AGS_POLE')],row[f.index('AGS_SML')],row[f.index('AGSP')],row[f.index('DEFER')],row[f.index('UGS')],row[f.index('UGS_LGE')],row[f.index('UGS_MED')],row[f.index('UGS_POLE')],row[f.index('UGS_SML')],row[f.index('UGSP')]]:
					# i = 0

                # YRUPD: YRUPD will be populated using YRSOURCE.
				row[f.index('YRUPD')] = row[f.index('YRSOURCE')]

				cursor.updateRow(row)
		del cursor

		# Turning off unnecessary fields before exporting it to dbf
		# This part is not necessary, but it's good to have.

		existingFields = [str(f.name).upper() for f in arcpy.ListFields(newfc_path)] # some fields have been newly created, so listing them again.
		req_fields = [v[0] for k,v in lut.req_fields.items()]
		optional_fields = [v[0] for k,v in lut.optional_fields.items()]
		fields2export = [field for field in req_fields + optional_fields if field in existingFields] # exporting all req_fields and optaionl_fields if it exists.
		logmsg += print2("Exporting the following fields:\n%s"%(str(fields2export)))

		# creating field_info text. Turning off or "hiding" fields that's not in fields2export.
		field_info = 'OBJECTID OBJECTID VISIBLE NONE'
		for field in existingFields:
			if field not in fields2export:
				field_info += ';%s %s HIDDEN NONE'%(field,field)

		arcpy.env.workspace = out_gdb_path
		temp_lyr_name = "temp_lyr_" + unique_suffix
		arcpy.MakeFeatureLayer_management(in_features=newfc_path, out_layer=temp_lyr_name, where_clause="", workspace="", field_info=field_info)

		logmsg += print2("Total number of records: %s"%record_count)
		logmsg += print2("Total area in meter sq: %s"%area_count)

		# export to dbf
		logmsg += print2("\nExporting to dbf...")
		out_name = "B4M.dbf" # cant be more than 5 characters....
		arcpy.TableToTable_conversion(in_rows=temp_lyr_name, out_path=output_folder, out_name=out_name)





		del temp_lyr_name

		path2dbf = os.path.join(output_folder,out_name)
		logmsg += print2("\n\n  Complete!!\n\nThe final product is saved here:\n%s\n"%path2dbf)
		logmsg += """\n\nDouble asterisks (**) indicates changes made to the data."""

	except:
		# if something fails, it will write the error msg in the log.
		logmsg += print2("Unexpected error:" + str(sys.exc_info()), msgtype = 'error')
		logmsg += "\n\n  !!!!    THE TOOL FAILED TO RUN    !!!!\n\n"

	# this will run whether something fails or not.
	finally:

		log.write(logmsg)
		log.close()

		os.startfile(output_folder)




def print2(msg, msgtype = 'msg'):
	""" print, arcmap AddMessage and return string all in one!"""
	# print(msg)
	if msgtype == 'msg':
		arcpy.AddMessage(msg)
	elif msgtype == 'warning':
		arcpy.AddWarning(msg)
	elif msgtype == 'error':
		arcpy.AddError(msg)
	return msg + '\n'



if __name__ == '__main__':
	input_bmi = arcpy.GetParameterAsText(0) # should be a feature class or shapefile (full path to them)
	output_folder = arcpy.GetParameterAsText(1) # Spcify any folder.
	submu = arcpy.GetParameterAsText(2) # this should be one of the fields (such as SMZ) in the input_bmi. The value of this field will be used to populate SUBMU field.

	main(input_bmi,output_folder, submu)
