# This script contains information specific to AWS_SHR data.

#			  order	|	  field 	|	length 	| field type 
fields = {
				1:		['AWS_YR',		4,			'SHORT'],
				2:		['BLOCKID',		30,			'TEXT'],
				3:		['SILVSYS',		10,			'TEXT'],
				4:		['HARVCAT',		10,			'TEXT'],
				5:		['FUELWOOD',	10,			'TEXT'],


				-6:		['USER_INPUT_INV_YEAR',	10,	'TEXT'],
				-5:		['USER_INPUT_SUB_ID',	10,	'TEXT'],				
				-4:		['USER_INPUT_FOREST',	50,	'TEXT'], # the additional fields must be either less than 0 or greater than 100
				-3:		['USER_INPUT_INVTYPE',	20,	'TEXT'], # DO NOT CHANGE the names of these additional fields.
				-2:		['AUTOGEN_INVID',		3,	'SHORT'],
				-1:		['AUTOGEN_DATE_APPEND',	20,	'DATE'],	# should be either 2018-01-18 format or 01/18/2018 format
				101:	['AUTOGEN_RECORD_ALTERED',	300, 'TEXT']}  # field 101 will be used to keep record of any changes to the original data




# if the new field does not exist in the old inventory, it will look for the corresponding old field and change the name of the old field into the new one.
fieldname_update = {
	
	# new field  |   old fields
	'BLOCKID':		['BLOCK_ID','BLK_ID'], # an error might occur if one layer has both BLOCK_ID and BLK_ID because it will try to alter both fieldnames to BLOCKID.

}


if __name__ == '__main__':
	fieldList = [v[0] for k,v in fields.items()]
	print fieldList
