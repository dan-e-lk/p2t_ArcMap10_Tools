
# So, the logic is that if an inventory does not have all the fields in the req_fields dictionary,
# the tool will create the missing fields and populate it using the corresponding field in the alternate_field dictionary,
#



# list of fields required to run MIST
#			  order	|	  field 	|	length 	| field type
req_fields = {
				1:		['POLYID',		25,			'TEXT'],
				2:		['POLYTYPE',	3,			'TEXT'],
				3:		['OWNER',		1,			'TEXT'],
				6:		['FORMOD',		2,			'TEXT'],
				7: 		['DEVSTAGE',	8,			'TEXT'], # change EST... to FTG..., and change NAT to FTGNAT. There might be more changes needed.
				31:		['ACCESS1',		3,			'TEXT'],
				33:		['MGMTCON1',	4,			'TEXT'],
				37:		['SPCOMP',		120,		'TEXT'],
				39:		['AGE',			3,			'DOUBLE'], # If age > 250 then age = 250. i.e. AGE caps at 250.
				42:		['STKG',		4,			'DOUBLE'], # If STKG > 2.5, then STKG = 2.5
				43:		['SC',			1,			'DOUBLE'],
				46:		['PLANFU',		10,			'TEXT'],
				48:		['AVAIL',		1,			'TEXT'],
				49:		['SILVSYS',		2,			'TEXT'],
				51:		['AREA',		10,			'DOUBLE'], # Create AREA field and populate AREA
				52:		['AGESTR',		1,			'TEXT'], # Create AGESTR field and populate 'E' when POLYTYPE = FOR
				53:		['YRUPD',		4,			'DOUBLE'], # Create YRUPD and populated it with YRSOURCE
				57:		['SI',			5,			'TEXT'], # Create SI from YIELD
				58:		['SISRC',		8,			'TEXT'], # Create SISRC field and populate it with 'ASSIGNED'
				59:		['MGMTSTG',		8,			'TEXT'], # Create MGMTSTG field and populate it with NEXTSTG field.
				60:		['SUBMU',		5,			'TEXT'], # Create SUBMU - user parameter. example: 3E or GCF
				61:		['ECOSITE1',	10,			'TEXT'], # Create ECOSITE1 field and populate it from 'PRI_ECO'
				62:		['ECOSITE2',	10,			'TEXT'], # this is not really required but added to be consistent with ECOSITE1
				63:		['ECOPCT1',		3,			'DOUBLE'],
# If we have both PRI_ECO and SEC_Eco populated
	# put 80 to ECOPCT1 and put 20 to ECOPCT2
# If we only have PRI_ECO populated
	# put 100 to ECOPCT1 and put 0 to ECOPCT2
				64:		['ECOPCT2',		3,			'DOUBLE'], # this is not really required but added to match ECOPCT1
				65:		['WG',			2,			'TEXT'], # Create WG field nad populate it from 'LEADSPC',
															 # and replace Ab to AX, Bd to OH, Cw to Ce, Ew to OH, Ob to OH, Pl to PO, Pt to PO, and Sn to SX.
				66:		['OMZ',			8,			'TEXT'], # This is hidden required field in MIST. Populate it the same way we populat SUBMU.

				# 80:		['AGS',			0,			'DOUBLE'], # these fields (#80-92) are not listed as mandatory, but may be essential to manipulate yield curves
				# 81:		['AGS_LGE',		0,			'DOUBLE'],
				# 82:		['AGS_MED',		0,			'DOUBLE'],
				# 83:		['AGS_POLE',	0,			'DOUBLE'],
				# 84:		['AGS_SML',		0,			'DOUBLE'],
				# 85:		['AGSP',		0,			'DOUBLE'],
				# 86:		['DEFER',		0,			'DOUBLE'],
				# 87:		['UGS',			0,			'DOUBLE'],
				# 88:		['UGS_LGE',		0,			'DOUBLE'],
				# 89:		['UGS_MED',		0,			'DOUBLE'],
				# 90:		['UGS_POLE',	0,			'DOUBLE'],
				# 91:		['UGS_SML',		0,			'DOUBLE'],
				# 92:		['UGSP',		0,			'DOUBLE'],
				}



# optional fields are not required but will be exported to the final output.
# fields not included here will be gone in the final output.
#			  order	|	  field 	|	length 	| field type
optional_fields = {

				5:		['SOURCE',		8,			'TEXT'],
				8:		['YRDEP',		4,			'DOUBLE'],
				9:		['DEPTYPE',		8,			'TEXT'],
				18:		['UYRORG',		4,			'DOUBLE'],
				19:		['USPCOMP',		120,		'TEXT'],
				24:		['USTKG',		4,			'DOUBLE'],
				25:		['USC',			1,			'DOUBLE'],
				27:		['VERT',		2,			'TEXT'],
				28:		['HORIZ',		2,			'TEXT'],
				36:		['YRORG',		4,			'DOUBLE'],
				40:		['HT',			4,			'DOUBLE'],
				50:		['NEXTSTG',		8,			'TEXT'],
				54:		['ECOSRC',		8,			'TEXT'],
				70:		['OCCLO',		3,			'DOUBLE'],
				71:		['UCCLO',		3,			'DOUBLE'],
				72:		['CCLO',		3,			'DOUBLE'],


				}


# it's okay not to have the required field as long as its corresponding alternate field exists (except for AREA field)
alternate_field = {

# 	MIST fields  |   existing fields
	'WG': 			'LEADSPC',
	'ECOSITE2': 	'SEC_ECO',
	'ECOSITE1': 	'PRI_ECO',
	'SI': 			'YIELD',
	'HORZ': 		'HORIZ',
	'MGMTSTG': 		'NEXTSTG',
	'YRUPD': 		'YRSOURCE'
}


if __name__ == '__main__':
	newdict = {v:k for k,v in alternate_field.items()}
	print(newdict)

