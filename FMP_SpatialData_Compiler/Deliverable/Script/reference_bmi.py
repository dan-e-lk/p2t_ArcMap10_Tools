# This script contains information specific to BMI/PCI/PCM/OPI/PFOREST data.

#			  order	|	  field 	|	length 	| field type 
fields = {
				1:		['POLYID',		25,			'TEXT'],
				2:		['POLYTYPE',	3,			'TEXT'],
				3:		['OWNER',		1,			'TEXT'],
				4:		['YRSOURCE',	4,			'SHORT'],
				5:		['SOURCE',		8,			'TEXT'],
				6:		['FORMOD',		2,			'TEXT'],
				7: 		['DEVSTAGE',	8,			'TEXT'],
				8:		['YRDEP',		4,			'SHORT'],
				9:		['DEPTYPE',		8,			'TEXT'],
				10:		['OYRORG',		4,			'SHORT'],
				11:		['OSPCOMP',		120,		'TEXT'],
				12:		['OLEADSPC',	3,			'TEXT'],
				13:		['OAGE',		3,			'SHORT'],
				14:		['OHT',			4,			'FLOAT'],
				15:		['OCCLO',		3,			'SHORT'],
				16:		['OSTKG',		4,			'FLOAT'],
				17:		['OSC',			1,			'SHORT'],
				18:		['UYRORG',		4,			'SHORT'],
				19:		['USPCOMP',		120,		'TEXT'],
				20:		['ULEADSPC',	3,			'TEXT'],
				21:		['UAGE',		3,			'SHORT'],
				22:		['UHT',			4,			'FLOAT'],
				23:		['UCCLO',		3,			'SHORT'],
				24:		['USTKG',		4,			'FLOAT'],
				25:		['USC',			1,			'SHORT'],
				26:		['INCIDSPC',	3,			'TEXT'],
				27:		['VERT',		2,			'TEXT'],
				28:		['HORIZ',		2,			'TEXT'],
				29:		['PRI_ECO',		13,			'TEXT'],
				30:		['SEC_ECO',		13,			'TEXT'],
				31:		['ACCESS1',		3,			'TEXT'],
				32:		['ACCESS2',		3,			'TEXT'],
				33:		['MGMTCON1',	4,			'TEXT'],
				34:		['MGMTCON2',	4,			'TEXT'],
				35:		['MGMTCON3',	4,			'TEXT'], 
				36:		['YRORG',		4,			'SHORT'],
				37:		['SPCOMP',		120,		'TEXT'],
				38:		['LEADSPC',		3,			'TEXT'],
				39:		['AGE',			3,			'SHORT'],
				40:		['HT',			4,			'FLOAT'],
				41:		['CCLO',		3,			'SHORT'],
				42:		['STKG',		4,			'FLOAT'],
				43:		['SC',			1,			'SHORT'],
				44:		['MANAGED',		1,			'TEXT'],
				45:		['SMZ',			15,			'TEXT'],
				46:		['PLANFU',		15,			'TEXT'],
				47:		['AU',			25,			'TEXT'],
				48:		['AVAIL',		1,			'TEXT'],
				49:		['SILVSYS',		2,			'TEXT'],
				50:		['NEXTSTG',		8,			'TEXT'],
				51:		['YIELD',		10,			'TEXT'],
				52:		['OMZ',			15,			'TEXT'],
				53:		['SGR',			25,			'TEXT'],


				-6:		['USER_INPUT_INV_YEAR',	10,	'TEXT'],
				-5:		['USER_INPUT_SUB_ID',	50,	'TEXT'],				
				-4:		['USER_INPUT_FOREST',	50,	'TEXT'], # the additional fields must be either less than 0 or greater than 100
				-3:		['USER_INPUT_INVTYPE',	20,	'TEXT'], # DO NOT CHANGE the names of these additional fields.
				-2:		['AUTOGEN_INVID',		3,	'SHORT'],
				-1:		['AUTOGEN_DATE_APPEND',	20,	'DATE'],	# should be either 2018-01-18 format or 01/18/2018 format
				101:	['AUTOGEN_RECORD_ALTERED',	300, 'TEXT']}  # field 101 will be used to keep record of any changes to the original data




# if the new field does not exist in the old inventory, it will look for the corresponding old field and change the name of the old field into the new one.
fieldname_update = {
	
	# new field  |   old fields
	'YRSOURCE':		['YRUPD'],
	'OLEADSPC':		['OWG'],
	'ULEADSPC':		['UWG'],
	'HORIZ':		['HORZ'],
	'PRI_ECO':		['ECOSITE1'],
	'SEC_ECO':		['ECOSITE2'],
	'LEADSPC':		['WG'],
	'YIELD':		['SI'],
}


if __name__ == '__main__':
	fieldList = [v[0] for k,v in fields.items()]
	print fieldList
