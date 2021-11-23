#-------------------------------------------------------------------------------
# Name:         TechSpec_AR_NEW.py
# Purpose:      This module checkes every validation statements under Annual Report Tech Spec 2017
#
# Author:       NER RIAU, Ministry of Natural Resources and Forestry
#
# Created:      Sept 6, 2018   
# Notes:        Any updates to this script can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog
#
#-------------------------------------------------------------------------------
import arcpy
import os, sys
import Reference as R
import pprint

verbose = True

lyrInfo = {
# Lyr acronym            name                           mandatory fields                                            Data Type   Tech Spec       Tech Spec URL

    "AGG":  ["Forestry Aggregate Pits",                 ['PITID','REHABREQ','REHAB','PITCLOSE','TONNES'],           'point',    '4.3.18',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=116')],
    "EST":  ["Establishment Assessment",                ['ARDSTGRP','SILVSYS','AGEEST','YRDEP','DSTBFU','SGR',
                                                            'TARGETFU','TARGETYD','ESTIND','ESTFU','ESTYIELD',
                                                            'SPCOMP','HT','DENSITY','STKG'],                        'polygon',  '4.3.15',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=89')],

    "FTG":  ["Free-To-Grow",                            ['ARDSTGRP','YRDEP','DSTBFU','SGR','TARGETFU','FTG'],       'polygon',  '4.3.17',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=108')],

    "HRV":  ["Harvest Disturbance",                     ['BLOCKID','HARVCAT','SILVSYS','HARVMTHD','MGMTSTG',
                                                            'ESTAREA','SGR','DSTBFU','TARGETFU','TARGETYD','TRIAL',
                                                            'LOGMTHD'],                                             'polygon',  '4.3.8',        R.findPDF('FIM_AR_TechSpec_2020.pdf#page=31')],

    "NDB":  ["Natural Disturbance",                     ['NDEPCAT','VOLCON','VOLHWD','DSTBFU'],                     'polygon',  '4.3.7',        R.findPDF('FIM_AR_TechSpec_2020.pdf#page=27')],
    "PER":  ["Performance Assessment",                  ['SILVSYS','PERFU','PERYIELD','SPCOMP','BHA','HT',
                                                            'DENSITY','STKG','AGS','UGS'],                          'polygon',  '4.3.16',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=100')],

    "PRT":  ["Protection Treatment",                    ['TRTMTHD1','TRTCAT1'],                                     'polygon',  '4.3.14',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=83')],
    "RDS":  ["Road Construction and Road Use",          ['ROADID','ROADCLAS','CONSTRCT','DECOM','TRANS','ACCESS',
                                                            'MAINTAIN','MONITOR','CONTROL1','CONTROL2'],            'arc',      '4.3.9',        R.findPDF('FIM_AR_TechSpec_2020.pdf#page=46')],

    "RGN":  ["Regeneration Treatment",                  ['TRTMTHD1','TRTCAT1','ESTAREA','SP1','SP2'],               'polygon',  '4.3.11',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=61')],
    "SCT":  ["Slash and Chip Treatment",                ['SLASHPIL','CHIPPIL','BURN','MECHANIC','REMOVAL'],         'arc',      '4.3.20',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=124')],
    "SGR":  ["Silvicultural Ground Rule Update",        ['SGR','TARGETFU','TARGETYD','TRIAL'],                      'polygon',  '4.3.19',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=120')],
    "SIP":  ["Site Preparation Treatment",              ['TRTMTHD1','TRTCAT1'],                                     'polygon',  '4.3.12',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=70')],
    "TND":  ["Tending Treatment",                       ['TRTMTHD1','TRTCAT1'],                                     'polygon',  '4.3.13',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=76')],
    "WTX":  ["Water Crossings",                         ['WATXID','WATXTYPE','CONSTRCT','MONITOR','REMOVE',
                                                            'REPLACE','REVIEW','ROADID','TRANS'],                   'point',    '4.3.10',       R.findPDF('FIM_AR_TechSpec_2020.pdf#page=54')],
    "WSY":  ["Wood Storage Yard",                       ['WSYID','TYPE'],                                           'polygon',  '4.3',          R.findPDF('FIM_AR_TechSpec_2020.pdf#page=129')] # This layer is new in 2020
        }

# vnull is used to check if an item is NULL or blank.
vnull = [None,'',' ']


def run(gdb, summarytbl, year, fmpStartYear, dataformat):  ## eg. summarytbl = {'MU615_15AGG00': ['AGG','Forestry Aggregate Pits','NAD 1983 Lambert Conformal Conic',['PIT_ID', 'REHABREQ', 'REHAB', 'TONNES'],['OBJECTID', 'SHAPE', 'MU615_15AGG00_', 'MU615_15AGG00_ID', 'PITCLOSE']],...}
    lyrList = summarytbl.keys()
    fieldValUpdate = dict(zip(lyrList,['' for i in lyrList]))  ## if we find a record-value-based mandatory field, field validation status should be updated.
    fieldValComUpdate = dict(zip(lyrList,[[] for i in lyrList])) ## if we find a record-value-based mandatory field, field validation comments should be updated.
    recordVal = dict(zip(lyrList,['' for i in lyrList]))  ## recordVal should be either Valid or Invalid for each layer.
    recordValCom = dict(zip(lyrList,[[] for i in lyrList]))  ## recordValCom should be in the form, "1 record(s) where AWS_YR = 2016".
    errorDetail = dict(zip(lyrList,[[] for i in lyrList])) ## this will be used to populate "Error Detail" section of the report.

    for lyr in summarytbl.keys(): # for each layer such as MU110_17SAC10...
        lyrAcro = summarytbl[lyr][0] ## eg. "AGP"
        criticalError = 0
        minorError = 0
        systemError = False
        # summarytbl[lyr][3] is a list of existing mandatory fields and summarytbl[lyr][4] is a list of existing other fields
        f = summarytbl[lyr][4] + summarytbl[lyr][3]  ## f is the list of all fields found in lyr. eg. ['FID', 'SHAPE','PIT_ID', 'PIT_OPEN', 'PITCLOSE', 'CAT9APP', ...]

        # each fieldname is a new variable where the value is its index number - for example, OBJECTID = 0.
        for i in range(len(f)):
            try:
                exec(f[i] + "=" + str(i)) ## POLYID = 0, POLYTYPE = 1, etc.
            except:
                pass # some field names are not valid as a variable name.

        # feature classes have ObjectID, shapefiles and coverages have FID. Search for ObjectID's index value in f, if not possible, search for FID's index value in f. else use whatever field comes first as the ID field.
        id_field = R.find_IdField(f, dataformat) # *23408  This will normally return OBJECTID for feature classes and FID for shapefile and coverage.
        id_field_idx = f.index(id_field)

        cursor = arcpy.da.SearchCursor(lyr,f)
        recordCount = len(list(cursor))
        cursor.reset()

        # Creating a new cursor. The new cursor has no artifact polygons created by donut holes in the coverages.
        artifact_count = 0
        # check for artifact polygons only if the data format is coverage, type is polygon, and if there's more than one mandatory field.
        if lyrInfo[lyrAcro][2] == 'polygon' and dataformat == 'coverage' and len(summarytbl[lyr][3]) > 1: # *23403
            result = R.create_cursor(lyr, summarytbl[lyr][3], f) # summarytbl[lyr][3] is the list of existing mandatory fields.
            if result != None:
                cursor2 = result
                recordCount2 = len(list(cursor2))
                cursor2.reset()
                # if the record count by the new cursor is different from the original cursor, use the new cursor
                if recordCount2 < recordCount:
                    cursor = cursor2
                    artifact_count = recordCount - recordCount2
        arcpy.AddMessage("\n  Checking each record in %s (%s records, %s artifacts)..."%(lyr,recordCount, artifact_count))
        recordValCom[lyr].append("Total %s records (with %s artifacts)."%(recordCount, artifact_count))



#       ######### Going through each layer type in alphabetical order ##########


        ###########################  Checking AGG   ############################

        if lyrAcro == "AGG":
            try: # need try and except block here for cases such as not having mandatory fields.
            # PITID
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: The population of PITID is mandatory (A blank or null value is not a valid code)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[PITID] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of PITID is mandatory (A blank or null value is not a valid code)."%len(errorList))

                # The PITID attribute must contain a unique value
                pitIDList = [cursor[PITID] for row in cursor]
                cursor.reset()
                if len(set(pitIDList)) < len(pitIDList):
                    duplicateCount = len(pitIDList) - len(set(pitIDList))
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The PITID attribute must contain a unique value."%duplicateCount)

            # REHABREQ
                # The attribute population must follow the correct format (must be between 0 and 9.9) 
                errorList = ["Error on %s %s: REHABREQ must be a number of hectares between 0 and 9.9 (Null is not allowed)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REHABREQ] in vnull or cursor[REHABREQ] < 0 or cursor[REHABREQ] > 9.9] # *24b04
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): REHABREQ must be a number of hectares between 0 and 9.9."%len(errorList))

                # If the area requiring rehabilitation is greater than zero (REHABREQ>0) then the pit closure date should be null (PITCLOSE = null)
                if "PITCLOSE" in f:
                    errorList = ["Error on %s %s: PITCLOSE should be null if REHABREQ > 0 (error when both PITCLOSE and REHABREQ are populated)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[REHABREQ] not in vnull
                                    if cursor[REHABREQ] > 0 and cursor[PITCLOSE] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PITCLOSE should be null if REHABREQ > 0 (error when both PITCLOSE and REHABREQ are populated)."%len(errorList))

                # The hectares requiring rehabilitation should be less than or equal to three.
                errorList = ["Warning on %s %s: REHABREQ should be less than or equal to 3."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REHABREQ] not in vnull
                                if cursor[REHABREQ] > 3 ] #*24b10
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): REHABREQ should be less than or equal to 3."%len(errorList))

            # REHAB
                # The attribute population must follow the correct format
                # A zero value is a valid code.
                errorList = ["Error on %s %s: REHAB must be a number of hectares between 0 and 9.9 (Null is not allowed)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REHAB] in vnull or cursor[REHAB] < 0 or cursor[REHAB] > 9.9] # *24b04
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): REHAB must be a number of hectares between 0 and 9.9."%len(errorList))

                # The following validation has been removed in 2020.  *2020.10.009
                # # If the area rehabilitated is zero (REHAB = 0) then the tonnes of aggregate extracted should not be zero (TONNES != 0)
                # errorList = ["Warning on %s %s: If REHAB is zero or null then the TONNES should not be zero or null."%(id_field, cursor[id_field_idx]) for row in cursor
                #                 if cursor[REHAB] in [0, None] and cursor[TONNES] in [0, None]]
                # cursor.reset()
                # if len(errorList) > 0:
                #     errorDetail[lyr].append(errorList)
                #     minorError += 1
                #     recordValCom[lyr].append("Warning on %s record(s): If REHAB is zero or null then the TONNES should not be zero or null."%len(errorList))

                # The hectares rehabilitated should be less than or equal to three.
                errorList = ["Warning on %s %s: REHAB should be less than or equal to 3."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REHAB] not in vnull
                                if cursor[REHAB] > 3 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): REHAB should be less than or equal to 3."%len(errorList))

            # PITCLOSE
                if 'PITCLOSE' in f:
                    # The attribute population must follow the correct format
                    # A blank or null value is a valid code
                    errorList = ["Error on %s %s: PITCLOSE attribute must follow the correct format (a blank or null is valid)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PITCLOSE] not in vnull and R.fimdate(cursor[PITCLOSE]) is None]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PITCLOSE attribute must follow the correct format (a blank or null is valid)."%len(errorList))

                    # The pit closure date should be within the fiscal year
                    errorList = ["Error on %s %s: PITCLOSE date should be within the fiscal year."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PITCLOSE] not in vnull and R.fimdate(cursor[PITCLOSE]) is not None # if PITCLOSE is populated with the correct format
                                    if R.fimdate(cursor[PITCLOSE]) < R.fimdate(str(year) + 'APR01')
                                    or R.fimdate(cursor[PITCLOSE]) > R.fimdate(str(year+1) + 'MAR31')]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PITCLOSE date should be within the fiscal year (%s)."%(len(errorList),year))

                    # The following has been commented out because it's a duplicate check as the one in REHABREQ.
                    # # When the final rehabilitation date is populated (PITCLOSE != null) then the required rehabilitation will be zero (REHABREQ = 0)
                    # errorList = ["Error on %s %s: REHABREQ must be zero or null if PITCLOSE is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                    #                 if cursor[PITCLOSE] not in vnull and R.fimdate(cursor[PITCLOSE]) is not None
                    #                 if cursor[REHABREQ] not in [0, None]]
                    # cursor.reset()
                    # if len(errorList) > 0:
                    #     errorDetail[lyr].append(errorList)
                    #     criticalError += 1
                    #     recordValCom[lyr].append("Error on %s record(s): REHABREQ must be zero or null if PITCLOSE is populated."%len(errorList))

            # TONNES
                # The attribute population must follow the correct format
                # A zero value is a valid code
                errorList = ["Error on %s %s: TONNES must be a number between 0 and 99,999,999."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TONNES] in vnull or cursor[TONNES] < 0 or cursor[TONNES] > 99999999] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TONNES must be a number between 0 and 99,999,999."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1


        ###########################  Checking EST   ############################

        if lyrAcro == "EST":
            try: # need try and except block here for cases such as not having mandatory fields.

            # ARDSTGRP
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: ARDSTGRP must be populated with HARV or NAT, and a blank or null is not a valid code."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ARDSTGRP] not in ['HARV','NAT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ARDSTGRP must be populated with HARV or NAT, and a blank or null is not a valid code."%len(errorList))

                # The annual report disturbance group will be harvest (ARDSTGRP = HARV) where the silviculture system is shelterwood or selection (SILVSYS = SH or SE)
                errorList = ["Error on %s %s: ARDSTGRP must be HARV if SILVSYS is equal to SH or SE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ARDSTGRP] != 'HARV'
                                if cursor[SILVSYS] in ['SH','SE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ARDSTGRP must be HARV if SILVSYS is equal to SH or SE."%len(errorList))

            # SILVSYS
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: SILVSYS must be populated with CC, SE or SH, and a blank or null is not a valid code."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] not in ['CC','SE','SH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be populated with CC, SE or SH, and a blank or null is not a valid code."%len(errorList))

            # AGEEST
                # The population of this attribute is mandatory where SILVSYS != SE *or SILVSYS != SH  *2020.10.007
                errorList = ["Error on %s %s: AGEEST must be greater than zero when SILVSYS is not equal to SE or SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] not in ['SE','SH']
                                if cursor[AGEEST] in vnull or cursor[AGEEST] <= 0 or cursor[AGEEST] > 9999] # having this upper limit check also catches string/unicode values *24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AGEEST must be greater than zero when SILVSYS is not equal to SE or SH."%len(errorList))

            # YRDEP
                # The population of this attribute is mandatory
                # The attribute population must follow the correct format
                # A zero (or null) value is not a valid code
                errorList = ["Error on %s %s: YRDEP must be populated with the correct format (YYYY) and a zero or Null is not a valid value."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[YRDEP] in vnull or cursor[YRDEP] < 1000 or cursor[YRDEP] > 9999]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): YRDEP must be populated with the correct format (YYYY) and a zero or Null is not a valid value."%len(errorList))

            # DSTBFU
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code.
                errorList = ["Error on %s %s: DSTBFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DSTBFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DSTBFU must be populated."%len(errorList))

            # SGR
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code.            
                errorList = ["Error on %s %s: SGR must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SGR] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SGR must be populated."%len(errorList))

            # TARGETFU
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code.            
                errorList = ["Error on %s %s: TARGETFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TARGETFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TARGETFU must be populated."%len(errorList))

            # TARGETYD
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code.            
                errorList = ["Error on %s %s: TARGETYD must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TARGETYD] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TARGETYD must be populated."%len(errorList))

            # ESTIND
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: ESTIND must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ESTIND] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ESTIND must be populated with Y or N."%len(errorList))

            # ESTFU
                # Where ESTIND = Y: The population of this attribute is mandatory
                # Where ESTIND != Y: A blank or null value is a valid code.             
                errorList = ["Error on %s %s: ESTFU must be populated where ESTIND = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ESTFU] in vnull and cursor[ESTIND] == 'Y']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ESTFU must be populated where ESTIND = Y."%len(errorList))

            # ESTYIELD
                # Where ESTIND = Y: The population of this attribute is mandatory
                # Where ESTIND != Y: A blank or null value is a valid code.             
                errorList = ["Error on %s %s: ESTYIELD must be populated where ESTIND = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ESTYIELD] in vnull and cursor[ESTIND] == 'Y']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ESTYIELD must be populated where ESTIND = Y."%len(errorList))

            # ESTIND - Y counter
                estind_y = ["y" for row in cursor if cursor[ESTIND] =='Y']
                cursor.reset()
                estind_y_count = len(estind_y)

            # SPCOMP
                if 'SPCOMP' in f:
                    # The population of this attribute is mandatory where ESTIND = Y
                    errorList = ["Error on %s %s: SPCOMP must be populated when ESTIND = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[ESTIND] == 'Y'
                                    if cursor[SPCOMP] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SPCOMP must be populated when ESTIND = Y."%len(errorList))

                    # The attribute population must follow the correct format
                    ## code to check spcomp (returns no messeage when SPCOMP is blank or null)
                    fieldname = "SPCOMP"
                    e1List, e2List, e3List, e4List, w1List = [],[],[],[],[]
                    for row in cursor:
                        if cursor[f.index(fieldname)] not in vnull:
                            check = R.spcVal(cursor[f.index(fieldname)],fieldname)
                            if check is None: ## when no error found
                                pass
                            elif check[0] == "Error1":
                                e1List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Error2":
                                e2List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Error3":
                                e3List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Error4":
                                e4List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Warning1":
                                w1List.append("Warning on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                    cursor.reset()
                        # summarizing errors
                    if len(e1List + e2List + e3List + e4List) > 0:
                        criticalError += 1
                    for errorlist in [e1List, e2List, e3List, e4List]:
                        if len(errorlist) > 0:
                            errorDetail[lyr].append(errorlist)
                            recordValCom[lyr].append("Error on %s record(s):%s."%(len(errorlist),errorlist[0][errorlist[0].find(':')+1:]))
                        # summarizing warnings
                    if len(w1List) > 0:
                        minorError += 1
                        errorDetail[lyr].append(w1List)
                        recordValCom[lyr].append("Warning on %s record(s):%s."%(len(w1List),w1List[0][w1List[0].find(':')+1:]))

                # The presence of this attribute in the file structure of the layer is mandatory where ESTIND = Y
                elif estind_y_count > 0:
                    fieldValComUpdate[lyr].append("Missing SPCOMP: SPCOMP field is mandatory where ESTIND = Y.")
                    fieldValUpdate[lyr] = 'Invalid'

            # HT
                # The attribute population must follow the correct format (if populated)
                errorList = ["Error on %s %s: HT must be between 0 and 40 if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HT] != None
                                if cursor[HT] < 0 or cursor[HT] > 40] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HT must be between 0 and 40 if populated."%len(errorList))

                # Where ESTIND = Y and SILVSYS = CC:  The population of this attribute is mandatory *2020.10.008
                # Where ESTIND = Y and SILVSYS = CC:  HT must be greater than zero.
                # Where ESTIND = N or SILVSYS = SE or SH:   HT can be zero.
                errorList = ["Error on %s %s: HT must be greater than 0 when ESTIND = Y and SILVSYS = CC."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ESTIND] == 'Y' and cursor[SILVSYS] == 'CC'
                                if cursor[HT] in vnull or cursor[HT] <= 0]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HT must be greater than 0 when ESTIND = Y and SILVSYS = CC."%len(errorList))

            # DENSITY
                # The attribute population must follow the correct format (if populated)
                errorList = ["Error on %s %s: DENSITY must be between 0 and 99999 if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DENSITY] != None
                                if cursor[DENSITY] < 0 or cursor[DENSITY] > 99999] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DENSITY must be between 0 and 99999 if populated."%len(errorList))

            # STKG
                # The attribute population must follow the correct format (if populated)
                errorList = ["Error on %s %s: STKG must be between 0 and 1 if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[STKG] != None
                                if cursor[STKG] < 0 or cursor[STKG] > 1] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): STKG must be between 0 and 99999 if populated."%len(errorList))

            # DENSITY and STKG
                # Where STKG is populated, DENSITY will be equal to zero
                # Where DENSITY is populated, STKG will be equal to zero
                # bascially means STKG and DENSITY cannot be both populated.
                errorList = ["Error on %s %s: STKG and DENSITY cannot be both populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DENSITY] > 0 and cursor[STKG] > 0]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): STKG and DENSITY cannot be both populated."%len(errorList))

                # Either DENSITY or STKG must be populated when ESTIND = Y
                errorList = ["Error on %s %s: Either DENSITY or STKG must be populated when ESTIND = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ESTIND] == 'Y'
                                if cursor[DENSITY] in [None, 0] and cursor[STKG] in [None, 0]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): Either DENSITY or STKG must be populated when ESTIND = Y."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1


        ###########################  Checking FTG   ############################

        if lyrAcro == "FTG":
            try: # need try and except block here for cases such as not having mandatory fields.

            # ARDSTGRP
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: ARDSTGRP must be populated with HARV or NAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ARDSTGRP] not in ['HARV','NAT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ARDSTGRP must be populated with HARV or NAT."%len(errorList))

            # YRDEP
                # The population of this attribute is mandatory
                # The attribute population must follow the correct format
                # A zero (or null) value is not a valid code
                errorList = ["Error on %s %s: YRDEP must be populated with the correct format (YYYY) and a zero or Null is not a valid value."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[YRDEP] in vnull or cursor[YRDEP] < 1000 or cursor[YRDEP] > 9999]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): YRDEP must be populated with the correct format (YYYY) and a zero or Null is not a valid value."%len(errorList))

                # The year of last disturbance should be greater than the annual report start year minus twenty (the error occurs when YRDEP <= ARYEAR - 20)
                errorList = ["Warning on %s %s: YRDEP should be greater than AR year minus 20."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[YRDEP] not in vnull
                                if cursor[YRDEP] > 999 and cursor[YRDEP] <= year - 20 ] # "cursor[YRDEP] > 999" check prevents catching the same error as above
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): YRDEP should be greater than AR year minus 20."%len(errorList))

            # DSTBFU
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code.
                errorList = ["Error on %s %s: DSTBFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DSTBFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DSTBFU must be populated."%len(errorList))

            # SGR
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code.            
                errorList = ["Error on %s %s: SGR must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SGR] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SGR must be populated."%len(errorList))

            # TARGETFU
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code.            
                errorList = ["Error on %s %s: TARGETFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TARGETFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TARGETFU must be populated."%len(errorList))

            # FTG
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: FTG must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[FTG] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FTG must be populated with Y or N."%len(errorList))

            # FTG - Y counter
                ftg_y = ["y" for row in cursor if cursor[FTG] =='Y']
                cursor.reset()
                ftg_y_count = len(ftg_y)

            # FTGFU
                # Where FTG = Y: The population of this attribute is mandatory
                # Where FTG = Y: A blank or null value is not a valid code.             
                if 'FTGFU' in f:
                    errorList = ["Error on %s %s: FTGFU must be populated where FTG = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[FTGFU] in vnull and cursor[FTG] == 'Y']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): FTGFU must be populated where FTG = Y."%len(errorList))

                # The presence of thie attribute in the file structure of the layer is mandatory (where FTG=Y)
                elif ftg_y_count > 0:
                    fieldValComUpdate[lyr].append("Missing FTGFU: FTGFU field is mandatory where FTG = Y.")
                    fieldValUpdate[lyr] = 'Invalid'

            # SPCOMP
                if 'SPCOMP' in f:
                    # The population of this attribute is mandatory where FTG = Y
                    errorList = ["Error on %s %s: SPCOMP must be populated when FTG = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[FTG] == 'Y'
                                    if cursor[SPCOMP] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SPCOMP must be populated when FTG = Y."%len(errorList))

                    # The attribute population must follow the correct format
                    ## code to check spcomp
                    fieldname = "SPCOMP"
                    e1List, e2List, e3List, e4List, w1List = [],[],[],[],[]
                    for row in cursor:
                        if cursor[f.index(fieldname)] not in vnull:
                            check = R.spcVal(cursor[f.index(fieldname)],fieldname)
                            if check is None: ## when no error found
                                pass
                            elif check[0] == "Error1":
                                e1List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Error2":
                                e2List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Error3":
                                e3List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Error4":
                                e4List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Warning1":
                                w1List.append("Warning on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                    cursor.reset()
                        # summarizing errors
                    if len(e1List + e2List + e3List + e4List) > 0:
                        criticalError += 1
                    for errorlist in [e1List, e2List, e3List, e4List]:
                        if len(errorlist) > 0:
                            errorDetail[lyr].append(errorlist)
                            recordValCom[lyr].append("Error on %s record(s):%s."%(len(errorlist),errorlist[0][errorlist[0].find(':')+1:]))
                        # summarizing warnings
                    if len(w1List) > 0:
                        minorError += 1
                        errorDetail[lyr].append(w1List)
                        recordValCom[lyr].append("Warning on %s record(s):%s."%(len(w1List),w1List[0][w1List[0].find(':')+1:]))

                # The presence of this attribute in the file structure of the layer is mandatory where FTG = Y
                elif ftg_y_count > 0:
                    fieldValComUpdate[lyr].append("Missing SPCOMP: SPCOMP field is mandatory where FTG = Y.")
                    fieldValUpdate[lyr] = 'Invalid'

            # HT
                if 'HT' in f:
                    # The attribute population must follow the correct format
                    errorList = ["Error on %s %s: HT must be between 0 and 40 if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[HT] != None
                                    if cursor[HT] < 0 or cursor[HT] > 40] #*24b09
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): HT must be between 0 and 40 if populated."%len(errorList))

                    # Where FTG = Y: The population of this attribute is mandatory
                    # Where FTG = Y: A zero (or null) value is not a valid code
                    # Where FTG = Y: When the free-to-grow indicator is yes (FTG = Y) then the height must be greater than or equal ot 80cm
                    errorList = ["Error on %s %s: HT must be greater than or equal to 0.8 when FTG = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[FTG] == 'Y'
                                    if cursor[HT] == None or cursor[HT] < 0.8] #*24b09
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): HT must be greater than or equal to 0.8 when FTG = Y."%len(errorList))

                # Where FTG = Y: The presence of this attribute in the file structure of the layer is mandatory
                elif ftg_y_count > 0:
                    fieldValComUpdate[lyr].append("Missing HT: HT field is mandatory where FTG = Y.")
                    fieldValUpdate[lyr] = 'Invalid'

            # STKG
                if 'STKG' in f:
                    # The attribute population must follow the correct format
                    errorList = ["Error on %s %s: STKG must be between 0 and 4 if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[STKG] != None
                                    if cursor[STKG] < 0 or cursor[STKG] > 4] #*24b09
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): STKG must be between 0 and 4 if populated."%len(errorList))

                    # Where FTG = Y: The population of this attribute is mandatory
                    # Where FTG = Y: A zero (or null) value is not a valid code
                    # Where FTG = Y: The stocking must be greater than or equal to forty percent (STKG >= 0.4)
                    errorList = ["Error on %s %s: STKG must be greater than or equal to 0.4 when FTG = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[FTG] == 'Y'
                                    if cursor[STKG] == None or cursor[STKG] < 0.4] #*24b09
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): STKG must be greater than or equal to 0.4 when FTG = Y."%len(errorList))

                # Where FTG = Y: The presence of this attribute in the file structure of the layer is mandatory
                elif ftg_y_count > 0:
                    fieldValComUpdate[lyr].append("Missing STKG: STKG field is mandatory where FTG = Y.")
                    fieldValUpdate[lyr] = 'Invalid'


            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking HRV   ############################

        if lyrAcro == "HRV":
            try: # need try and except block here for cases such as not having mandatory fields.

            #BLOCKID  **new in 2017
                # The population of this attribute is mandatory where plan start year is greater than or equal to 2019
                # A blank or null value is not a valid code where plan start is greater than or equal to 2019
                if fmpStartYear >= 2019:
                    errorList = ["Error on %s %s: BLOCKID must be populated where plan start year is greater than or equal to 2019."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[BLOCKID] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): BLOCKID must be populated where plan start year is greater than or equal to 2019."%len(errorList))


            # HARVCAT
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: HARVCAT must be populated and follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVCAT] not in ['REGULAR','BRIDGING','REDIRECT','ROADROW','ACCELER','FRSTPASS','SCNDPASS','SALVAGE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVCAT must be populated and follow the correct coding scheme."%len(errorList))

                # The following validation has been removed in 2020 **2020.10.003
                # Bridging (HARVCAT = BRIDGING) is only available when the AR start year is equal to the first year of the plan period
                # errorList = ["Error on %s %s: HARVCAT = BRIDGING is the only available when AR year is equal to the first year of the plan period."%(id_field, cursor[id_field_idx]) for row in cursor
                #                 if cursor[HARVCAT] == 'BRIDGING' and year != fmpStartYear]
                # cursor.reset()
                # if len(errorList) > 0:
                #     errorDetail[lyr].append(errorList)
                #     criticalError += 1
                #     recordValCom[lyr].append("Error on %s record(s): HARVCAT = BRIDGING is the only available when AR year is equal to the first year of the plan period."%len(errorList))

            # SILVSYS
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: SILVSYS must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] not in ['CC','SE','SH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be populated with the correct coding scheme."%len(errorList))

            # HARVMTHD
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: HARVMTHD must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVMTHD] not in ['CONVENTION','BLOCKSTRIP','PATCH','SEEDTREE','HARP','THINCOM','UNIFORM','STRIP','GROUPSH','IRREGULR','SINGLETREE','GROUPSE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVMTHD must be populated with the correct coding scheme."%len(errorList))

                # The single-tree (SINGLETREE) and group selection (GROUPSE) are only valid codes when SILVSYS = SE
                errorList = ["Error on %s %s: HARVMTHD = SINGLETREE or GROUPSE is only valid if SILVSYS = SE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVMTHD] in ['SINGLETREE','GROUPSE']
                                if cursor[SILVSYS] != 'SE' ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVMTHD = SINGLETREE or GROUPSE is only valid if SILVSYS = SE."%len(errorList))

                # The uniform (UNIFORM), strip (STRIP) and group shelterwood (GROUPSH) and **IRREGULR are only valide codes when SILVSYS = SH   **2020.10.004
                errorList = ["Error on %s %s: HARVMTHD: UNIFORM, STRIP, GROUPSH or IRREGULR are only valid codes when SILVSYS = SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVMTHD] in ['UNIFORM','STRIP','GROUPSH','IRREGULR']
                                if cursor[SILVSYS] != 'SH' ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): UNIFORM, STRIP, GROUPSH or IRREGULR are only valid codes when SILVSYS = SH."%len(errorList))

                # The conventional, block or strip, patch, seed-tree and harvesting with regeneration protection (CONVENTION, BLOCKSTRIP, PATCH, SEEDTREE, or HARP) are only valid when SILVSYS = CC
                errorList = ["Error on %s %s: HARVMTHD: CONVENTION, BLOCKSTRIP, PATCH, SEEDTREE, or HARP is only available when SILVSYS = CC."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVMTHD] in ['CONVENTION','BLOCKSTRIP','PATCH','SEEDTREE','HARP']
                                if cursor[SILVSYS] != 'CC' ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVMTHD: CONVENTION, BLOCKSTRIP, PATCH, SEEDTREE, or HARP is only available when SILVSYS = CC."%len(errorList))

                # The commercial thinning (THINCOM) is valid for either the clear cut or the shelterwood silviculture system.
                errorList = ["Error on %s %s: HARVMTHD: THINCOM is valid only if SILVSYS is CC or SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVMTHD] == 'THINCOM'
                                if cursor[SILVSYS] not in ['CC','SH'] ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVMTHD: THINCOM is valid only if SILVSYS is CC or SH."%len(errorList))

            # MGMTSTG
                # The population of this attribute is mandatory where SILVSYS = SH (with an exception where HARVMTHD = THINCOM) *24b08
                errorList = ["Error on %s %s: MGMTSTG must be populated if SILVSYS = SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] == 'SH' and cursor[HARVMTHD] != 'THINCOM'
                                if cursor[MGMTSTG] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MGMTSTG must be populated if SILVSYS = SH."%len(errorList))

                # The attribute population must follow the correct coding scheme
                # A blank or null value is a valid code
                errorList = ["Error on %s %s: MGMTSTG must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[MGMTSTG] not in vnull
                                if cursor[MGMTSTG] not in ['PREPCUT','SEEDCUT','IRREGULR','FIRSTCUT','LASTCUT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MGMTSTG must follow the correct coding scheme if populated."%len(errorList))

                # The stage of management will be blank (MGMTSTG = null) when the silviculture system is either selection or clearcut, or the harvest method is commercial thinning. (SILVSYS = SE or CC   OR HARVMTHD = THINCOM)
                errorList = ["Error on %s %s: MGMTSTG must be null if SILVSYS = SE or CC or if HARVMTHD = THINCOM."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] in ['SE','CC'] or cursor[HARVMTHD] == 'THINCOM'
                                if cursor[MGMTSTG] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MGMTSTG must be null if SILVSYS = SE or CC or if HARVMTHD = THINCOM."%len(errorList))

            # ESTAREA
                # the population of this attribute is mandatory where HARVMTH = BLCKSTRIP
                # A zero (or null) value is not a valid code
                # The attibute population must follow the correct format (if populated)
                errorList = ["Error on %s %s: ESTAREA must be between 0.01 and 1 and zero or null is not a valid code."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ESTAREA] == None or cursor[ESTAREA] < 0.01 or cursor[ESTAREA] > 1] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ESTAREA must be between 0.01 and 1 and zero or null is not a valid code."%len(errorList))

            # SGR
                # The population of this attribute is mandatory
                # A blank or null value is a valid code where HARVCAT = ROADROW
                errorList = ["Error on %s %s: SGR must be populated unless HARVCAT = ROADROW."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVCAT] != 'ROADROW'
                                if cursor[SGR] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SGR must be populated unless HARVCAT = ROADROW."%len(errorList))

            # DSTBFU
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code            
                errorList = ["Error on %s %s: DSTBFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DSTBFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DSTBFU must be populated."%len(errorList))

            # TARGETFU
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code
                # A blank or null value is a valid code where HARVCAT = ROADROW **2020.10.005
                errorList = ["Error on %s %s: TARGETFU must be populated (except where HARVCAT = ROADROW)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TARGETFU] in vnull
                                if cursor[HARVCAT] != 'ROADROW']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TARGETFU must be populated (except where HARVCAT = ROADROW)."%len(errorList))

            # TARGETYD
                # The population of this attribute is mandatory where silviculture system is clearcut or shelterwood (SILVSYS = CC or SH)
                # A blank or null value is not a valid code where silviculture system is clearcut or shelterwood (SILVSYS = CC or SH)        
                # A blank or null value is a valid code where HARVCAT = ROADROW **2020.10.006
                errorList = ["Error on %s %s: TARGETYD must be populated where SILVSYS = CC or SH (except where HARVCAT = ROADROW)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] in ['CC','SH']
                                if cursor[HARVCAT] != 'ROADROW'
                                if cursor[TARGETYD] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TARGETYD must be populated where SILVSYS = CC or SH (except where HARVCAT = ROADROW)."%len(errorList))

            # TRIAL
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code            
                errorList = ["Error on %s %s: TRIAL must be populated with Y or N and blank or null value is not a valid code."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRIAL] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRIAL must be populated with Y or N and blank or null value is not a valid code."%len(errorList))                    

            # LOGMTHD
                # The attribute population must follow the correct coding scheme
                # A blank or null value is not a valid code            
                errorList = ["Error on %s %s: LOGMTHD must be populated with FT, CL or TL and blank or null value is not a valid code."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[LOGMTHD] not in ['FT','CL','TL']] #*24b12
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): LOGMTHD must be populated with FT, CL or TL and blank or null value is not a valid code."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking NDB   ############################

        if lyrAcro == "NDB":
            try: # need try and except block here for cases such as not having mandatory fields.

            # NDEPCAT
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: NDEPCAT must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[NDEPCAT] not in ['BLOWDOWN','DISEASE','DROUGHT','FIRE','FLOOD','ICE','INSECTS','SNOW']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): NDEPCAT must be populated with the correct coding scheme."%len(errorList))

            # VOLCON
                # The attribute population must follow the correct format
                errorList = ["Error on %s %s: VOLCON must be between 0 and 9,999,999 if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[VOLCON] != None
                                if cursor[VOLCON] < 0 or cursor[VOLCON] > 9999999 ] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): VOLCON must be between 0 and 9,999,999 if populated."%len(errorList))

            # VOLHWD
                # The attribute population must follow the correct format            
                errorList = ["Error on %s %s: VOLHWD must be between 0 and 9,999,999 if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[VOLHWD] != None
                                if cursor[VOLHWD] < 0 or cursor[VOLHWD] > 9999999 ] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): VOLHWD must be between 0 and 9,999,999 if populated."%len(errorList))

            # DSTBFU
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: DSTBFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DSTBFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DSTBFU must be populated."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1


        ###########################  Checking PER   ############################

        if lyrAcro == "PER":
            try: # need try and except block here for cases such as not having mandatory fields.

            # SILVSYS
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme
                # A blank or null value is not a valid value
                errorList = ["Error on %s %s: SILVSYS must be populated and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] not in ['CC','SE','SH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be populated and must follow the correct coding scheme."%len(errorList))

            # PERFU
                # The population of this attribute is mandatory
                # A blank or null value is not a valid value
                errorList = ["Error on %s %s: PERFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[PERFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PERFU must be populated."%len(errorList))

            # PERYIELD
                # The population of this attribute is mandatory
                # A blank or null value is not a valid value
                errorList = ["Error on %s %s: PERYIELD must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[PERYIELD] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PERYIELD must be populated."%len(errorList))

            # SPCOMP
                # The population of this attribute is mandatory
                # A blank or null value is not a valid value
                errorList = ["Error on %s %s: SPCOMP must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SPCOMP] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SPCOMP must be populated."%len(errorList))

                # The following codeblock checks the format of SPCOMP values:
                current_field = 'SPCOMP'            
                e1List, e2List, e3List, e4List, w1List = [],[],[],[],[]
                for row in cursor:
                    if cursor[f.index(current_field)] not in vnull:
                        check = R.spcVal(cursor[f.index(current_field)],current_field)
                        if check is None: ## when no error found
                            pass
                        elif check[0] == "Error1":
                            e1List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                        elif check[0] == "Error2":
                            e2List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                        elif check[0] == "Error3":
                            e3List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                        elif check[0] == "Error4":
                            e4List.append("Error on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                        elif check[0] == "Warning1":
                            w1List.append("Warning on %s %s: %s"%(id_field, cursor[id_field_idx],check[1]))
                cursor.reset()
                    # summarizing errors
                if len(e1List + e2List + e3List + e4List) > 0:
                    criticalError += 1
                for errorlist in [e1List, e2List, e3List, e4List]:
                    if len(errorlist) > 0:
                        errorDetail[lyr].append(errorlist)
                        recordValCom[lyr].append("Error on %s record(s):%s."%(len(errorlist),errorlist[0][errorlist[0].find(':')+1:]))
                    # summarizing warnings
                if len(w1List) > 0:
                    minorError += 1
                    errorDetail[lyr].append(w1List)
                    recordValCom[lyr].append("Warning on %s record(s):%s."%(len(w1List),w1List[0][w1List[0].find(':')+1:]))

            # BHA
                # The population of this attribute is mandatory where SILVSYS = CC and SH (and zero is not an acceptable value)
                errorList = ["Error on %s %s: BHA must be populated (and zero is not an acceptable value) when SILVSYS is CC or SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] in ['CC','SH']
                                if cursor[BHA] in [0, None]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): BHA must be populated (and zero is not an acceptable value) when SILVSYS is CC or SH."%len(errorList))

                # The attribute population must follow the correct format
                errorList = ["Error on %s %s: BHA must range from 0 to 99."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[BHA] != None
                                if cursor[BHA] < 0 or cursor[BHA] > 99] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): BHA must range from 0 to 99."%len(errorList))

            # HT
                # The population of this attribute is mandatory where SILVSYS = CC and SH (and zero is not an acceptable value)
                errorList = ["Error on %s %s: HT must be populated (and zero is not an acceptable value) when SILVSYS is CC or SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] in ['CC','SH']
                                if cursor[HT] in [0, None]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HT must be populated (and zero is not an acceptable value) when SILVSYS is CC or SH."%len(errorList))

                # The attribute population must follow the correct format
                errorList = ["Error on %s %s: HT must range from 0 to 40."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HT] != None
                                if cursor[HT] < 0 or cursor[HT] > 40] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HT must range from 0 to 40."%len(errorList))

            # DENSITY
                # The population of this attribute is mandatory (where STKG is not populated and) where SILVSYS = CC and SH
                errorList = ["Error on %s %s: DENSITY must be populated where STKG is not populated and SILVSYS is CC or SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] in ['CC','SH'] and cursor[STKG] in [None, 0] #*24b09
                                if cursor[DENSITY] in [0, None]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DENSITY must be populated where STKG is not populated and SILVSYS is CC or SH."%len(errorList))

                # Where STKG is populated DENSITY will be equal to zero.
                errorList = ["Error on %s %s: DENSITY must be zero or null when STKG is greater than 0."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[STKG] != None and cursor[STKG] > 0
                                if cursor[DENSITY] not in [0, None]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DENSITY must be zero or null when STKG is greater than 0."%len(errorList))

                # (The attribute population must follow the correct format)
                errorList = ["Error on %s %s: DENSITY must range from 0 to 99999."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DENSITY] != None
                                if cursor[DENSITY] < 0 or cursor[DENSITY] > 99999]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DENSITY must range from 0 to 99999."%len(errorList))

            # STKG
                # The population of this attribute is mandatory (where DENSITY is not populated and) where SILVSYS = CC and SH
                errorList = ["Error on %s %s: STKG must be populated where DENSITY is not populated and SILVSYS is CC or SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] in ['CC','SH'] and cursor[DENSITY] in [None, 0] #*24b09
                                if cursor[STKG] in [0, None]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): STKG must be populated where DENSITY is not populated and SILVSYS is CC or SH."%len(errorList))

                # Where STKG is populated STKG will be equal to zero.
                errorList = ["Error on %s %s: STKG must be zero or null when DENSITY is greater than 0."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DENSITY] != None and cursor[DENSITY] > 0
                                if cursor[STKG] not in [0, None]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): STKG must be zero or null when DENSITY is greater than 0."%len(errorList))

                # (The attribute population must follow the correct format)
                errorList = ["Error on %s %s: STKG must range from 0 to 4."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[STKG] != None
                                if cursor[STKG] < 0 or cursor[STKG] > 4]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): STKG must range from 0 to 4."%len(errorList))

            # AGS
                # The attribute population must follow the correct format
                errorList = ["Error on %s %s: AGS must range from 0 to 100."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[AGS] != None
                                if cursor[AGS] < 0 or cursor[AGS] > 100] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AGS must range from 0 to 100."%len(errorList))

                # The population of this attribute is mandatory where SILVSYS = SE
                # A zero or null value is a valid code where SILVSYS != SE
                errorList = ["Error on %s %s: AGS must be populated (and a zero value is not acceptable) where SILVSYS = SE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] == 'SE'
                                if cursor[AGS] in [0, None]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AGS must be populated (and a zero value is not acceptable) where SILVSYS = SE."%len(errorList))

            # UGS
                # The attribute population must follow the correct format
                errorList = ["Error on %s %s: UGS must range from 0 to 100."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[UGS] != None
                                if cursor[UGS] < 0 or cursor[UGS] > 100] #*24b09
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): UGS must range from 0 to 100."%len(errorList))

                # The population of this attribute is mandatory where SILVSYS = SE
                # A zero or null value is a valid code where SILVSYS != SE
                errorList = ["Error on %s %s: UGS must be populated (and a zero value is not acceptable) where SILVSYS = SE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] == 'SE'
                                if cursor[UGS] in [0, None]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): UGS must be populated (and a zero value is not acceptable) where SILVSYS = SE."%len(errorList))


            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1


        ###########################  Checking PRT   ############################

        if lyrAcro == "PRT":
            try: # need try and except block here for cases such as not having mandatory fields.

            # TRTMTHD1
                # The attribute population must follow the correct coding scheme
                errorList = ["Error on %s %s: TRTMTHD1 must follow the correct coding scheme, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] not in vnull + ['PCHEMA','PCHEMG','PMANUAL']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTMTHD1 must follow the correct coding scheme, if populated."%len(errorList))

            # TRTMTHD2
                if 'TRTMTHD2' in f:
                    errorList = ["Error on %s %s: TRTMTHD2 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD2] not in vnull + ['PCHEMA','PCHEMG','PMANUAL']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTMTHD2 must follow the correct coding scheme if populated."%len(errorList))

            # TRTMTHD3
                if 'TRTMTHD3' in f:
                    errorList = ["Error on %s %s: TRTMTHD3 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD3] not in vnull + ['PCHEMA','PCHEMG','PMANUAL']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTMTHD3 must follow the correct coding scheme if populated."%len(errorList))

            # TRTMTHD1, 2 and 3
                # For TRTMTHD1, 2 or 3, the population of one of these attributes is mandatory.
                opt_flds = ['TRTMTHD2','TRTMTHD3'] # optional fields
                command = """errorList = ["Error on %s %s: For TRTMTHD1, TRTMTHD2 and TRTMTHD3, the population of one of these attributes is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD1] in vnull"""
                for opt_fld in opt_flds:
                    if opt_fld in f:
                        command += """ and cursor[""" + opt_fld + """] in vnull"""
                command += ']'
                exec(command)
                cursor.reset()

                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): For TRTMTHD1, TRTMTHD2 and TRTMTHD3, the population of one of these attributes is mandatory."%len(errorList))

            # TRTCAT1
                # The attribute population must follow the correct coding scheme
                # A blank or null value is a valid code
                errorList = ["Error on %s %s: TRTCAT1 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTCAT1] not in ['REG','RET','SUP'] + vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTCAT1 must be populated with the correct coding scheme if populated."%len(errorList))

            # TRTCAT2
                if 'TRTCAT2' in f:
                    errorList = ["Error on %s %s: TRTCAT2 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTCAT2] not in ['REG','RET','SUP'] + vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT2 must be populated with the correct coding scheme if populated."%len(errorList))

            # TRTCAT3
                if 'TRTCAT3' in f:
                    errorList = ["Error on %s %s: TRTCAT3 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTCAT3] not in ['REG','RET','SUP'] + vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT3 must be populated with the correct coding scheme if populated."%len(errorList))

            # TRTMTHD chemical count
                # PRODTYPE, RATE_AI, and APPNUM fields become mandatory fields when any of the TRTMTHD are either PCHEMA or PCHEMG.
                trtmthd1_chem = ['y' for row in cursor if cursor[TRTMTHD1] in ['PCHEMA','PCHEMG']]
                cursor.reset()

                if 'TRTMTHD2' in f:
                    trtmthd2_chem = ['y' for row in cursor if cursor[TRTMTHD2] in ['PCHEMA','PCHEMG']]
                else:
                    trtmthd2_chem = []
                cursor.reset()

                if 'TRTMTHD3' in f:
                    trtmthd3_chem = ['y' for row in cursor if cursor[TRTMTHD3] in ['PCHEMA','PCHEMG']]
                else:
                    trtmthd3_chem = []
                cursor.reset()

                trtmthd_chem_count = len(trtmthd1_chem + trtmthd2_chem + trtmthd3_chem)

            # PRODTYPE
                if 'PRODTYPE' in f:
                    # The product type attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    trt2_check = " or cursor[TRTMTHD2] in ['PCHEMA','PCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] in ['PCHEMA','PCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: PRODTYPE must be populated when any of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PRODTYPE] in vnull
                                    if cursor[TRTMTHD1] in ['PCHEMA','PCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PRODTYPE must be populated when any of the treatment methods are chemical."%len(errorList))

                    # The product type must be null when all the treatment methods are manual (when none of the treatment methods are chemial)
                    trt2_check = " and cursor[TRTMTHD2] not in ['PCHEMA','PCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " and cursor[TRTMTHD3] not in ['PCHEMA','PCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: PRODTYPE must be null when none of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PRODTYPE] not in vnull
                                    if cursor[TRTMTHD1] not in ['PCHEMA','PCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PRODTYPE must be null when none of the treatment methods are chemical."%len(errorList))

                elif trtmthd_chem_count > 0:
                    # The product type attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    fieldValComUpdate[lyr].append("Missing PRODTYPE: The presence of PRODTYPE field is mandatory when any of the treatment methods are chemical.")
                    fieldValUpdate[lyr] = 'Invalid'

            # RATE_AI
                if 'RATE_AI' in f:
                    # The product quantity attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    trt2_check = " or cursor[TRTMTHD2] in ['PCHEMA','PCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] in ['PCHEMA','PCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: RATE_AI must be greater than 0 and less than or equal to 9.99 when any of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[RATE_AI] == None or cursor[RATE_AI] <= 0 or cursor[RATE_AI] > 9.99
                                    if cursor[TRTMTHD1] in ['PCHEMA','PCHEMG']""" + trt2_check + trt3_check + "]" #*24b09
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): RATE_AI must be greater than 0 and less than or equal to 9.99 when any of the treatment methods are chemical."%len(errorList))

                    # The product quantity must be zero (or null) when all the treatment methods are manual (when none of the treatment methods are chemial)
                    trt2_check = " and cursor[TRTMTHD2] not in ['PCHEMA','PCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " and cursor[TRTMTHD3] not in ['PCHEMA','PCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: RATE_AI must be zero or null when none of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[RATE_AI] not in [None, 0]
                                    if cursor[TRTMTHD1] not in ['PCHEMA','PCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): RATE_AI must be zero or null when none of the treatment methods are chemical."%len(errorList))

                elif trtmthd_chem_count > 0:
                    # The product quantity attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    fieldValComUpdate[lyr].append("Missing RATE_AI: The presence of RATE_AI field is mandatory when any of the treatment methods are chemical.")
                    fieldValUpdate[lyr] = 'Invalid'

            # APPNUM
                if 'APPNUM' in f:
                    # The number of application attribute must be present and greater than 0 when any of the treatment methods are aerial or ground chemial
                    trt2_check = " or cursor[TRTMTHD2] in ['PCHEMA','PCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] in ['PCHEMA','PCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: APPNUM must be greater than 0 and less than or equal to 9 when any of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[APPNUM] == None or cursor[APPNUM] <= 0 or cursor[APPNUM] > 9
                                    if cursor[TRTMTHD1] in ['PCHEMA','PCHEMG']""" + trt2_check + trt3_check + "]" #*24b09
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): APPNUM must be greater than 0 and less than or equal to 9 when any of the treatment methods are chemical."%len(errorList))

                    # The number of application must be zero (or null) when all the treatment methods are manual (when none of the treatment methods are chemial)
                    trt2_check = " and cursor[TRTMTHD2] not in ['PCHEMA','PCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " and cursor[TRTMTHD3] not in ['PCHEMA','PCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: APPNUM must be zero or null when none of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[APPNUM] not in [None, 0]
                                    if cursor[TRTMTHD1] not in ['PCHEMA','PCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): APPNUM must be zero or null when none of the treatment methods are chemical."%len(errorList))

                elif trtmthd_chem_count > 0:
                    # The number of application attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    fieldValComUpdate[lyr].append("Missing APPNUM: The presence of APPNUM field is mandatory when any of the treatment methods are chemical.")
                    fieldValUpdate[lyr] = 'Invalid'

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking RDS   ############################

        if lyrAcro == "RDS":
            try: # need try and except block here for cases such as not having mandatory fields.

            # ROADID
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: The population of ROADID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ROADID] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of ROADID is mandatory."%len(errorList))

            # ROADCLAS
                # The population of this attribute is mandatory where CONSTRUCT = Y
                # A blank or null value IS A VALID code
                errorList = ["Error on %s %s: ROADCLAS must be populated where CONSTRCT = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[CONSTRCT] == 'Y'
                                if cursor[ROADCLAS] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADCLAS must be populated where CONSTRCT = Y."%len(errorList))

                # The attribute population must follow the correct coding scheme.
                errorList = ["Error on %s %s: ROADCLAS must follow the correct coding scheme (if populated)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ROADCLAS] not in vnull
                                if cursor[ROADCLAS] not in ['B','O','P']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADCLAS must follow the correct coding scheme (if populated)."%len(errorList))

            # CONSTRCT
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.
                errorList = ["Error on %s %s: CONSTRCT must be populated and must be Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[CONSTRCT] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONSTRCT must be populated and must be Y or N."%len(errorList))

            # DECOM
                # The attribute population must follow the correct coding scheme.
                # A blank or null value IS A VALID code.       
                errorList = ["Error on %s %s: DECOM must follow the correct coding scheme, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DECOM] not in vnull
                                if cursor[DECOM] not in ['BERM','SCAR','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DECOM must follow the correct coding scheme, if populated."%len(errorList))

            # TRANS
                # The attribute population must follow the correct format
                # A zero value is a valid code
                # The value must be greater than or equal to the 10 year plan period start year.
                errorList = ["Error on %s %s: TRANS must be greater than or equal to the 10 year plan period start year, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRANS] not in [0, None]
                                if cursor[TRANS] < fmpStartYear or cursor[TRANS] > 9999]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRANS must be greater than or equal to the 10 year plan period start year, if populated."%len(errorList))

            # ACCESS
                # The attribute population must follow the correct coding scheme.
                # A blank or null value IS A VALID code.
                errorList = ["Error on %s %s: ACCESS must follow the correct coding scheme, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ACCESS] not in ['APPLY','REMOVE','BOTH'] + vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must follow the correct coding scheme, if populated."%len(errorList))
                
                # other ACCESS validations can be found under CONTROL1 & 2 validation below.

            # MAINTAIN
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.            
                errorList = ["Error on %s %s: MAINTAIN must be populated and must be Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[MAINTAIN] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MAINTAIN must be populated and must be Y or N."%len(errorList))

            # MONITOR
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.            
                errorList = ["Error on %s %s: MONITOR must be populated and must be Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[MONITOR] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MONITOR must be populated and must be Y or N."%len(errorList))

            # CONSTRCT DECOM ACCESS MAINTAIN and MONITOR
                # At minimum, one of Construction, Decommissioning, Maintenance, Monitoring or Access Control must occur for each record.
                errorList = ["Error on %s %s: At minimum, one of Construction, Decom, Maintenance, Monitoring or Access Control must occur."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[CONSTRCT] != 'Y' and cursor[DECOM] not in ['BERM','SCAR','SLSH','WATX'] and cursor[MAINTAIN] != 'Y' and cursor[MONITOR] != 'Y' and cursor[ACCESS] not in ['APPLY','REMOVE','BOTH'] ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): At minimum, one of Construction, Decom, Maintenance, Monitoring or Access Control must occur."%len(errorList))            

            # CONTROL1
                # The attribute population must follow the correct coding scheme.
                # A blank or null value IS A VALID code.            
                errorList = ["Error on %s %s: CONTROL1 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[CONTROL1] not in ['BERM','GATE','PRIV','SCAR','SIGN','SLSH','WATX'] + vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 must follow the correct coding scheme if populated."%len(errorList))

            # CONTROL2
                # The attribute population must follow the correct coding scheme.
                # A blank or null value IS A VALID code.             
                errorList = ["Error on %s %s: CONTROL2 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[CONTROL2] not in ['BERM','GATE','PRIV','SCAR','SIGN','SLSH','WATX'] + vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL2 must follow the correct coding scheme if populated."%len(errorList))

            # CONTROL 1 and 2
                # When the road access control status is apply or both, then the control type must be a code other than null (CONTROL1 or CONTROL2 is not null)
                errorList = ["Error on %s %s: CONTROL1 or 2 must be populated with the correct coding scheme where ACCESS is 'APPLY' or 'BOTH'."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ACCESS] in ['APPLY','BOTH']
                                if cursor[CONTROL1] not in ['BERM','GATE','PRIV','SCAR','SIGN','SLSH','WATX'] and cursor[CONTROL2] not in ['BERM','GATE','PRIV','SCAR','SIGN','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 or 2 must be populated with the correct coding scheme where ACCESS is 'APPLY' or 'BOTH'."%len(errorList))

                # Stage 2: When the road access control status is remove, then the control type should be null (CONTROL1 = null and CONTROL2 = null)
                errorList = ["Warning on %s %s: CONTROL1 and CONTROL2 should be null when ACCESS = REMOVE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ACCESS] == 'REMOVE'
                                if cursor[CONTROL1] not in vnull or cursor[CONTROL2] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): CONTROL1 and CONTROL2 should be null when ACCESS = REMOVE."%len(errorList))                


            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1


        ###########################  Checking RGN   ############################

        if lyrAcro == "RGN":
            try:

            # TRTMTHD1
                # The attribute population must follow the coding scheme
                errorList = ["Error on %s %s: TRTMTHD1 must follow the correct coding scheme, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] not in ['CLAAG','NATURAL','HARP','PLANT','SCARIFY','SEED','SEEDSIP','SEEDTREE','STRIPCUT'] + vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTMTHD1 must follow the correct coding scheme, if populated."%len(errorList))

            # TRTMTHD2
                # The attribute population must follow the coding scheme
                if 'TRTMTHD2' in f:
                    errorList = ["Error on %s %s: TRTMTHD2 must follow the correct coding scheme, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD2] not in ['CLAAG','NATURAL','HARP','PLANT','SCARIFY','SEED','SEEDSIP','SEEDTREE','STRIPCUT'] + vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTMTHD2 must follow the correct coding scheme, if populated."%len(errorList))

            # TRTMTHD3
                # The attribute population must follow the coding scheme
                if 'TRTMTHD3' in f:
                    errorList = ["Error on %s %s: TRTMTHD3 must follow the correct coding scheme, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD3] not in ['CLAAG','NATURAL','HARP','PLANT','SCARIFY','SEED','SEEDSIP','SEEDTREE','STRIPCUT'] + vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTMTHD3 must follow the correct coding scheme, if populated."%len(errorList))
                        
            # TRTMTHD1, 2 and 3
                # For TRTMTHD1, 2 or 3, the population of one of these attributes is mandatory.
                opt_flds = ['TRTMTHD2','TRTMTHD3'] # optional fields
                command = """errorList = ["Error on %s %s: For TRTMTHD1, TRTMTHD2 and TRTMTHD3, the population of one of these attributes is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD1] in vnull"""
                for opt_fld in opt_flds:
                    if opt_fld in f:
                        command += """ and cursor[""" + opt_fld + """] in vnull"""
                command += ']'
                exec(command)
                cursor.reset()

                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): For TRTMTHD1, TRTMTHD2 and TRTMTHD3, the population of one of these attributes is mandatory."%len(errorList))

            # TRTCAT1
                # The attribute population must follow the correct coding scheme
                # A blank or null value is a valid code
                errorList = ["Error on %s %s: TRTCAT1 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTCAT1] not in ['REG','RET','SUP'] + vnull] #*24b15
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTCAT1 must be populated with the correct coding scheme if populated."%len(errorList))

            # TRTCAT2
                if 'TRTCAT2' in f:
                    errorList = ["Error on %s %s: TRTCAT2 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTCAT2] not in ['REG','RET','SUP'] + vnull] #*24b15
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT2 must be populated with the correct coding scheme if populated."%len(errorList))

            # TRTCAT3
                if 'TRTCAT3' in f:
                    errorList = ["Error on %s %s: TRTCAT3 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTCAT3] not in ['REG','RET','SUP'] + vnull] #*24b15
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT3 must be populated with the correct coding scheme if populated."%len(errorList))

            # TRTCAT1 and TRTMTHD1
                # If the treatment method is populated (TRTMTHD# != Null) then the associated treatment category must also be populated.
                # The attribute population must follow the correct coding scheme.
                errorList = ["Error on %s %s: TRTCAT1 must be populated and must follow the correct coding scheme if TRTMTHD1 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] not in vnull
                                if cursor[TRTCAT1] not in ['REG','RET','SUP']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTCAT1 must be populated and must follow the correct coding scheme if TRTMTHD1 is populated."%len(errorList))

                errorList = ["Error on %s %s: TRTMTHD1 must be PLANT or SEED if TRTCAT1 = RET."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTCAT1] == 'RET'
                                if cursor[TRTMTHD1] not in ['PLANT','SEED']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTMTHD1 must be PLANT or SEED if TRTCAT1 = RET."%len(errorList))

                errorList = ["Error on %s %s: TRTMTHD1 must be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT1 = SUP."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTCAT1] == 'SUP'
                                if cursor[TRTMTHD1] not in ['PLANT','SEED','SCARIFY','SEEDSIP']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTMTHD1 must be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT1 = SUP."%len(errorList))

            # TRTCAT2 and TRTMTHD2
                # If the treatment method is populated (TRTMTHD# != Null) then the associated treatment category must also be populated.
                if 'TRTMTHD2' in f:
                    if 'TRTCAT2' in f:
                        errorList = ["Error on %s %s: TRTCAT2 must be populated and must follow the correct coding scheme if TRTMTHD2 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTMTHD2] not in vnull
                                        if cursor[TRTCAT2] not in ['REG','RET','SUP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTCAT2 must be populated and must follow the correct coding scheme if TRTMTHD2 is populated."%len(errorList))

                        errorList = ["Error on %s %s: TRTMTHD2 should be PLANT or SEED if TRTCAT2 = RET."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTCAT2] == 'RET'
                                        if cursor[TRTMTHD2] not in ['PLANT','SEED']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTMTHD2 should be PLANT or SEED if TRTCAT2 = RET."%len(errorList))

                        errorList = ["Error on %s %s: TRTMTHD2 should be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT2 = SUP."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTCAT2] == 'SUP'
                                        if cursor[TRTMTHD2] not in ['PLANT','SEED','SCARIFY','SEEDSIP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTMTHD2 should be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT2 = SUP."%len(errorList))
                    else:
                        fieldValComUpdate[lyr].append("Missing TRTCAT2: The presence of TRTCAT2 field is mandatory if TRTMTHD2 exists.")
                        fieldValUpdate[lyr] = 'Invalid'          

            # TRTCAT3 and TRTMTHD3
                # If the treatment method is populated (TRTMTHD# != Null) then the associated treatment category must also be populated.
                if 'TRTMTHD3' in f:
                    if 'TRTCAT3' in f:
                        errorList = ["Error on %s %s: TRTCAT3 must be populated and must follow the correct coding scheme if TRTMTHD3 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTMTHD3] not in vnull
                                        if cursor[TRTCAT3] not in ['REG','RET','SUP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTCAT3 must be populated and must follow the correct coding scheme if TRTMTHD3 is populated."%len(errorList))

                        errorList = ["Error on %s %s: TRTMTHD3 should be PLANT or SEED if TRTCAT3 = RET."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTCAT3] == 'RET'
                                        if cursor[TRTMTHD3] not in ['PLANT','SEED']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTMTHD3 should be PLANT or SEED if TRTCAT3 = RET."%len(errorList))

                        errorList = ["Error on %s %s: TRTMTHD3 should be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT3 = SUP."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTCAT3] == 'SUP'
                                        if cursor[TRTMTHD3] not in ['PLANT','SEED','SCARIFY','SEEDSIP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTMTHD3 should be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT3 = SUP."%len(errorList))
                    else:
                        fieldValComUpdate[lyr].append("Missing TRTCAT3: The presence of TRTCAT3 field is mandatory if TRTMTHD3 exists.")
                        fieldValUpdate[lyr] = 'Invalid'          


            # TRTMTHD1,2,3 plant count
                trtmthd1_plant = ['y' for row in cursor if cursor[TRTMTHD1] == 'PLANT']
                cursor.reset()

                if 'TRTMTHD2' in f:
                    trtmthd2_plant = ['y' for row in cursor if cursor[TRTMTHD2] == 'PLANT']
                else:
                    trtmthd2_plant = []
                cursor.reset()

                if 'TRTMTHD3' in f:
                    trtmthd3_plant = ['y' for row in cursor if cursor[TRTMTHD3] == 'PLANT']
                else:
                    trtmthd3_plant = []
                cursor.reset()

                trtmthd_plant_count = len(trtmthd1_plant + trtmthd2_plant + trtmthd3_plant)

            # TRTMTHD1,2,3 STRIPCUT count
                trtmthd1_stripcut = ['y' for row in cursor if cursor[TRTMTHD1] == 'STRIPCUT']
                cursor.reset()

                if 'TRTMTHD2' in f:
                    trtmthd2_stripcut = ['y' for row in cursor if cursor[TRTMTHD2] == 'STRIPCUT']
                else:
                    trtmthd2_stripcut = []
                cursor.reset()

                if 'TRTMTHD3' in f:
                    trtmthd3_stripcut = ['y' for row in cursor if cursor[TRTMTHD3] == 'STRIPCUT']
                else:
                    trtmthd3_stripcut = []
                cursor.reset()

                trtmthd_stripcut_count = len(trtmthd1_stripcut + trtmthd2_stripcut + trtmthd3_stripcut)

            # ESTAREA
                # The attribute population must follow the correct format.
                # A zero (or null) value is not a valid code
                errorList = ["Error on %s %s: ESTAREA must be between 0.01 and 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                 if cursor[ESTAREA] == None or cursor[ESTAREA] < 0.01 or cursor[ESTAREA] > 1.0]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ESTAREA must be between 0.01 and 1."%len(errorList))


                # ESTAREA must be > 0 and < 1 if TRTMTHD1, 2 or 3 is STRIPCUT (TRTMTHD2 and 3 are non-mandatory fields)
                # (ESTAREA cannot be zero anyways, so it's redundant to check if ESTAREA is greater than zero)
                trt2_check = " or cursor[TRTMTHD2] == 'STRIPCUT'" if "TRTMTHD2" in f else ""
                trt3_check = " or cursor[TRTMTHD3] == 'STRIPCUT'" if "TRTMTHD3" in f else ""
                command = """errorList = ["Error on %s %s: ESTAREA must be less than 1 when any of the TRTMTHD1, 2 or 3 is STRIPCUT."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] == 'STRIPCUT'""" + trt2_check + trt3_check + " \
                                if cursor[ESTAREA] == 1.0]"
                exec(command)
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ESTAREA must be less than 1 when any of the TRTMTHD1, 2 or 3 is STRIPCUT."%len(errorList))

                # ESTAREA must be < 1 if TRTMTHD1, 2 or 3 is PLANT (TRTMTHD2 and 3 are non-mandatory fields) and both SP1 and SP2 are populated.
                # (ESTAREA cannot be zero anyways, so it's redundant to check if ESTAREA is greater than zero)
                trt2_check = " or cursor[TRTMTHD2] == 'PLANT'" if "TRTMTHD2" in f else ""
                trt3_check = " or cursor[TRTMTHD3] == 'PLANT'" if "TRTMTHD3" in f else ""
                command = """errorList = ["Error on %s %s: ESTAREA must be less than 1 when any of the TRTMTHD1, 2 or 3 is PLANT and both SP1 and SP2 are populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] == 'PLANT'""" + trt2_check + trt3_check + " \
                                if cursor[SP1] not in vnull and cursor[SP2] not in vnull \
                                if cursor[ESTAREA] == 1.0]"
                exec(command)                    
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ESTAREA must be less than 1 when any of the TRTMTHD1, 2 or 3 is PLANT and both SP1 and SP2 are populated."%len(errorList))

                # ESTAREA must be 1 if TRTMTHD# is neither PLANT nor STRIPCUT.
                trt2_check = " and cursor[TRTMTHD2] not in ['PLANT','STRIPCUT']" if "TRTMTHD2" in f else ""
                trt3_check = " and cursor[TRTMTHD3] not in ['PLANT','STRIPCUT']" if "TRTMTHD3" in f else ""
                command = """errorList = ["Error on %s %s: ESTAREA must be 1 if all of the Treatment Methods (TRTMTHD#) are neither PLANT nor STRIPCUT."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] not in ['PLANT','STRIPCUT']""" + trt2_check + trt3_check + " \
                                if cursor[ESTAREA] != 1]"
                exec(command)
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ESTAREA must be 1 if all of the Treatment Methods (TRTMTHD#) are neither PLANT nor STRIPCUT."%len(errorList))


            # SP1 and SP2
                # The presence of this attribute in the file structure of the layer is mandatory for SP1 and SP2
                # The attribute population must follow the correct coding scheme.
                errorList = ["Error on %s %s: SP1 must use the coding list from OSPCOMP in the FIM FRI Tech Spec, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                 if cursor[SP1] not in vnull
                                 if cursor[SP1].upper() not in R.SpcListInterp + R.SpcListOther]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SP1 must use the coding list from OSPCOMP in the FIM FRI Tech Spec, if populated."%len(errorList))

                errorList = ["Error on %s %s: SP2 must use the coding list from OSPCOMP in the FIM FRI Tech Spec, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                 if cursor[SP2] not in vnull
                                 if cursor[SP2].upper() not in R.SpcListInterp + R.SpcListOther]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SP2 must use the coding list from OSPCOMP in the FIM FRI Tech Spec, if populated."%len(errorList))

                # SP2 must be null if the treatment method is not planting (TRTMTHD# != PLANT)
                trt2_check = " and cursor[TRTMTHD2] != 'PLANT'" if "TRTMTHD2" in f else ""
                trt3_check = " and cursor[TRTMTHD3] != 'PLANT'" if "TRTMTHD3" in f else ""
                command = """errorList = ["Error on %s %s: SP2 must be null if none of the Treatment Methods (TRTMTHD#) is PLANT."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] != 'PLANT'""" + trt2_check + trt3_check + " \
                                if cursor[SP2] not in vnull]"
                exec(command)
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SP2 must be null if none of the Treatment Methods (TRTMTHD#) is PLANT."%len(errorList))

                # SP1 must be populated if any of the treatment methods are planting (TRTMTHD# = PLANT)
                trt2_check = " or cursor[TRTMTHD2] == 'PLANT'" if "TRTMTHD2" in f else ""
                trt3_check = " or cursor[TRTMTHD3] == 'PLANT'" if "TRTMTHD3" in f else ""
                command = """errorList = ["Error on %s %s: SP1 must be populated if any of the Treatment Methods (TRTMTHD#) are PLANT."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] == 'PLANT'""" + trt2_check + trt3_check + " \
                                if cursor[SP1] in vnull]"
                exec(command)
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SP1 must be populated if any of the Treatment Methods (TRTMTHD#) are PLANT."%len(errorList))

                # The first species field may be populated if the treatment method is SEED or SEEDSIP.
                # The species fields (SP1 and SP2) should be null if all of the treatment methods are CLAAG, NATURAL, HARP, SCARIFY, STRIPCUT or SEEDTREE or Null (or if none of the treatment methods is PLANT, SEED or SEEDSIP)
                trt2_check = " and cursor[TRTMTHD2] not in ['PLANT','SEED','SEEDSIP']" if "TRTMTHD2" in f else ""
                trt3_check = " and cursor[TRTMTHD3] not in ['PLANT','SEED','SEEDSIP']" if "TRTMTHD3" in f else ""
                command = """errorList = ["Warning on %s %s: SP1 and SP2 should be null if none of the treatment methods is PLANT, SEED or SEEDSIP."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] not in ['PLANT','SEED','SEEDSIP']""" + trt2_check + trt3_check + " \
                                if cursor[SP1] not in vnull or cursor[SP2] not in vnull]"
                exec(command)
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): SP1 and SP2 should be null if none of the treatment methods is PLANT, SEED or SEEDSIP."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking SCT   ############################

        if lyrAcro == "SCT":
            try:

            # SLASHPIL
                # The population of this attribute is mandatory
                # The attribute population must follow the coding scheme
                errorList = ["Error on %s %s: SLASHPIL must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SLASHPIL] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SLASHPIL must be populated with Y or N."%len(errorList))

            # CHIPPIL
                # The population of this attribute is mandatory
                # The attribute population must follow the coding scheme
                errorList = ["Error on %s %s: CHIPPIL must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[CHIPPIL] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CHIPPIL must be populated with Y or N."%len(errorList))

            # BURN
                # The population of this attribute is mandatory
                # The attribute population must follow the coding scheme
                errorList = ["Error on %s %s: BURN must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[BURN] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): BURN must be populated with Y or N."%len(errorList))

            # MECHANIC
                # The population of this attribute is mandatory
                # The attribute population must follow the coding scheme
                errorList = ["Error on %s %s: MECHANIC must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[MECHANIC] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MECHANIC must be populated with Y or N."%len(errorList))

            # REMOVAL
                # The population of this attribute is mandatory
                # The attribute population must follow the coding scheme
                errorList = ["Error on %s %s: REMOVAL must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REMOVAL] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): REMOVAL must be populated with Y or N."%len(errorList))                    

            # SLASHPIL, CHIPPIL, BURN, MECHANIC and REMOVAL
                # At minimum, one of Slash Piling, Chip Piling, Slash Burning, Onsite MEchanical PRocessing or Removal Offsite for Processing must occur for each record.
                errorList = ["Error on %s %s: At minimum, one of SLASHPIL, CHIPPIL, BURN, MECHANIC and REMOVAL must occur."%(id_field, cursor[id_field_idx]) for row in cursor
                                if 'Y' not in [cursor[SLASHPIL], cursor[CHIPPIL], cursor[BURN], cursor[MECHANIC], cursor[REMOVAL]]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): At minimum, one of SLASHPIL, CHIPPIL, BURN, MECHANIC and REMOVAL must occur."%len(errorList))     

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking SGR   ############################

        if lyrAcro == "SGR":
            try:

            # SGR
                # A blank or null value is not a valid value.
                errorList = ["Error on %s %s: SGR must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SGR] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SGR must be populated."%len(errorList))

            # TARGETFU
                # A blank or null value is not a valid value.
                errorList = ["Error on %s %s: TARGETFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TARGETFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TARGETFU must be populated."%len(errorList))

            # TARGETYD
                # A blank or null value is not a valid value.
                errorList = ["Error on %s %s: TARGETYD must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TARGETYD] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TARGETYD must be populated."%len(errorList))

            # TRIAL
                # The population of this attribute is mandatory
                # The attribute population must follow the coding scheme
                errorList = ["Error on %s %s: TRIAL must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRIAL] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRIAL must be populated with Y or N."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1


        ###########################  Checking SIP   ############################

        if lyrAcro == "SIP":
            try: # need try and except block here for cases such as not having mandatory fields.

            # TRTMTHD1
                # The attribute population must follow the correct coding scheme
                errorList = ["Error on %s %s: TRTMTHD1 must follow the correct coding scheme, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] not in vnull + ['SIPMECH','SIPCHEMA','SIPCHEMG','SIPPB']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTMTHD1 must follow the correct coding scheme, if populated."%len(errorList))

            # TRTMTHD2
                # The attribute population must follow the correct coding scheme
                if 'TRTMTHD2' in f:
                    errorList = ["Error on %s %s: TRTMTHD2 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD2] not in vnull + ['SIPMECH','SIPCHEMA','SIPCHEMG','SIPPB']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTMTHD2 must follow the correct coding scheme if populated."%len(errorList))

            # TRTMTHD3
                # The attribute population must follow the correct coding scheme
                if 'TRTMTHD3' in f:
                    errorList = ["Error on %s %s: TRTMTHD3 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD3] not in vnull + ['SIPMECH','SIPCHEMA','SIPCHEMG','SIPPB']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTMTHD3 must follow the correct coding scheme if populated."%len(errorList))

            # TRTMTHD1, 2 and 3
                # For TRTMTHD1, 2 or 3, the population of one of these attributes is mandatory.
                opt_flds = ['TRTMTHD2','TRTMTHD3'] # optional fields
                command = """errorList = ["Error on %s %s: For TRTMTHD1, TRTMTHD2 and TRTMTHD3, the population of one of these attributes is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD1] in vnull"""
                for opt_fld in opt_flds:
                    if opt_fld in f:
                        command += """ and cursor[""" + opt_fld + """] in vnull"""
                command += ']'
                exec(command)
                cursor.reset()

                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): For TRTMTHD1, TRTMTHD2 and TRTMTHD3, the population of one of these attributes is mandatory."%len(errorList))

            # TRTCAT1
                # The attribute population must follow the correct coding scheme
                # A blank or null value is a valid code
                errorList = ["Error on %s %s: TRTCAT1 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTCAT1] not in ['REG','RET','SUP'] + vnull] #*24b15
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTCAT1 must be populated with the correct coding scheme if populated."%len(errorList))

            # TRTCAT2
                if 'TRTCAT2' in f:
                    errorList = ["Error on %s %s: TRTCAT2 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTCAT2] not in ['REG','RET','SUP'] + vnull] #*24b15
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT2 must be populated with the correct coding scheme if populated."%len(errorList))

            # TRTCAT3
                if 'TRTCAT3' in f:
                    errorList = ["Error on %s %s: TRTCAT3 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTCAT3] not in ['REG','RET','SUP'] + vnull] #*24b15
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT3 must be populated with the correct coding scheme if populated."%len(errorList))

            # TRTCAT1 and TRTMTHD1
                # If the treatment method is populated (TRTMTHD# != Null) then the associated treatment category must also be populated.
                # The attribute population must follow the correct coding scheme.
                errorList = ["Error on %s %s: TRTCAT1 must be populated and must follow the correct coding scheme if TRTMTHD1 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] not in vnull
                                if cursor[TRTCAT1] not in ['REG','RET','SUP']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTCAT1 must be populated and must follow the correct coding scheme if TRTMTHD1 is populated."%len(errorList))

            # TRTCAT2 and TRTMTHD2
                # If the treatment method is populated (TRTMTHD# != Null) then the associated treatment category must also be populated.
                if 'TRTMTHD2' in f:
                    if 'TRTCAT2' in f:
                        errorList = ["Error on %s %s: TRTCAT2 must be populated and must follow the correct coding scheme if TRTMTHD2 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTMTHD2] not in vnull
                                        if cursor[TRTCAT2] not in ['REG','RET','SUP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTCAT2 must be populated and must follow the correct coding scheme if TRTMTHD2 is populated."%len(errorList))
                    else:
                        fieldValComUpdate[lyr].append("Missing TRTCAT2: The presence of TRTCAT2 field is mandatory if TRTMTHD2 exists.")
                        fieldValUpdate[lyr] = 'Invalid'          

            # TRTCAT3 and TRTMTHD3
                # If the treatment method is populated (TRTMTHD# != Null) then the associated treatment category must also be populated.
                if 'TRTMTHD3' in f:
                    if 'TRTCAT3' in f:
                        errorList = ["Error on %s %s: TRTCAT3 must be populated and must follow the correct coding scheme if TRTMTHD3 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTMTHD3] not in vnull
                                        if cursor[TRTCAT3] not in ['REG','RET','SUP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTCAT3 must be populated and must follow the correct coding scheme if TRTMTHD3 is populated."%len(errorList))
                    else:
                        fieldValComUpdate[lyr].append("Missing TRTCAT3: The presence of TRTCAT3 field is mandatory if TRTMTHD3 exists.")
                        fieldValUpdate[lyr] = 'Invalid'  

            # TRTMTHD chemical count
                # PRODTYPE, RATE_AI, and APPNUM fields become mandatory fields when any of the TRTMTHD are either SIPCHEMA or SIPCHEMG.
                trtmthd1_chem = ['y' for row in cursor if cursor[TRTMTHD1] in ['SIPCHEMA','SIPCHEMG']]
                cursor.reset()

                if 'TRTMTHD2' in f:
                    trtmthd2_chem = ['y' for row in cursor if cursor[TRTMTHD2] in ['SIPCHEMA','SIPCHEMG']]
                else:
                    trtmthd2_chem = []
                cursor.reset()

                if 'TRTMTHD3' in f:
                    trtmthd3_chem = ['y' for row in cursor if cursor[TRTMTHD3] in ['SIPCHEMA','SIPCHEMG']]
                else:
                    trtmthd3_chem = []
                cursor.reset()

                trtmthd_chem_count = len(trtmthd1_chem + trtmthd2_chem + trtmthd3_chem)

            # PRODTYPE
                if 'PRODTYPE' in f:
                    # The product type attribute must be present and populated when any of the treatment methods are mechanical or prescribed burn.
                    trt2_check = " or cursor[TRTMTHD2] in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: PRODTYPE must be populated when any of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PRODTYPE] in vnull
                                    if cursor[TRTMTHD1] in ['SIPCHEMA','SIPCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PRODTYPE must be populated when any of the treatment methods are chemical."%len(errorList))

                    # The product type must be null when all the treatment methods are mechanical or prescribed burn. (when none of the treatment methods are chemial)
                    trt2_check = " and cursor[TRTMTHD2] not in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " and cursor[TRTMTHD3] not in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: PRODTYPE must be null when none of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PRODTYPE] not in vnull
                                    if cursor[TRTMTHD1] not in ['SIPCHEMA','SIPCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PRODTYPE must be null when none of the treatment methods are chemical."%len(errorList))

                elif trtmthd_chem_count > 0:
                    # The product type attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    fieldValComUpdate[lyr].append("Missing PRODTYPE: The presence of PRODTYPE field is mandatory when any of the treatment methods are chemical.")
                    fieldValUpdate[lyr] = 'Invalid'

            # RATE_AI
                if 'RATE_AI' in f:
                    # The product quantity attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    trt2_check = " or cursor[TRTMTHD2] in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: RATE_AI must be greater than 0 and less than or equal to 9.99 when any of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[RATE_AI] == None or cursor[RATE_AI] <= 0 or cursor[RATE_AI] > 9.99
                                    if cursor[TRTMTHD1] in ['SIPCHEMA','SIPCHEMG']""" + trt2_check + trt3_check + "]" #*24b09
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): RATE_AI must be greater than 0 and less than or equal to 9.99 when any of the treatment methods are chemical."%len(errorList))

                    # The product quantity must be zero (or null) when all the treatment methods are mechanical or prescribed burn. (when none of the treatment methods are chemial)
                    trt2_check = " and cursor[TRTMTHD2] not in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " and cursor[TRTMTHD3] not in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: RATE_AI must be zero or null when none of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[RATE_AI] not in [None, 0]
                                    if cursor[TRTMTHD1] not in ['SIPCHEMA','SIPCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): RATE_AI must be zero or null when none of the treatment methods are chemical."%len(errorList))

                elif trtmthd_chem_count > 0:
                    # The product quantity attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    fieldValComUpdate[lyr].append("Missing RATE_AI: The presence of RATE_AI field is mandatory when any of the treatment methods are chemical.")
                    fieldValUpdate[lyr] = 'Invalid'

            # APPNUM
                if 'APPNUM' in f:
                    # The number of application attribute must be present and greater than 0 when any of the treatment methods are aerial or ground chemial
                    trt2_check = " or cursor[TRTMTHD2] in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: APPNUM must be greater than 0 and less than or equal to 9 when any of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[APPNUM] == None or cursor[APPNUM] <= 0 or cursor[APPNUM] > 9
                                    if cursor[TRTMTHD1] in ['SIPCHEMA','SIPCHEMG']""" + trt2_check + trt3_check + "]" #*24b09
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): APPNUM must be greater than 0 and less than or equal to 9 when any of the treatment methods are chemical."%len(errorList))

                    # The number of application must be zero (or null) when all the treatment methods are mechanical or prescribed burn. (when none of the treatment methods are chemial)
                    trt2_check = " and cursor[TRTMTHD2] not in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " and cursor[TRTMTHD3] not in ['SIPCHEMA','SIPCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: APPNUM must be zero or null when none of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[APPNUM] not in [None, 0]
                                    if cursor[TRTMTHD1] not in ['SIPCHEMA','SIPCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): APPNUM must be zero or null when none of the treatment methods are chemical."%len(errorList))

                elif trtmthd_chem_count > 0:
                    # The number of application attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    fieldValComUpdate[lyr].append("Missing APPNUM: The presence of APPNUM field is mandatory when any of the treatment methods are chemical.")
                    fieldValUpdate[lyr] = 'Invalid'

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1


        ###########################  Checking TND   ############################

        if lyrAcro == "TND":
            try: # need try and except block here for cases such as not having mandatory fields.

            # TRTMTHD1
                # The attribute population must follow the correct coding scheme
                errorList = ["Error on %s %s: TRTMTHD1 must follow the correct coding scheme, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] not in vnull + ['CLCHEMA','CLCHEMG','CLMANUAL','CLMECH','CLPB','IMPROVE','THINPRE','CULTIVAT','PRUNE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTMTHD1 must follow the correct coding scheme, if populated."%len(errorList))

            # TRTMTHD2
                # The attribute population must follow the correct coding scheme
                if 'TRTMTHD2' in f:
                    errorList = ["Error on %s %s: TRTMTHD2 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD2] not in vnull + ['CLCHEMA','CLCHEMG','CLMANUAL','CLMECH','CLPB','IMPROVE','THINPRE','CULTIVAT','PRUNE']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTMTHD2 must follow the correct coding scheme if populated."%len(errorList))

            # TRTMTHD3
                # The attribute population must follow the correct coding scheme
                if 'TRTMTHD3' in f:
                    errorList = ["Error on %s %s: TRTMTHD3 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD3] not in vnull + ['CLCHEMA','CLCHEMG','CLMANUAL','CLMECH','CLPB','IMPROVE','THINPRE','CULTIVAT','PRUNE']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTMTHD3 must follow the correct coding scheme if populated."%len(errorList))

            # TRTMTHD1, 2 and 3
                # For TRTMTHD1, 2 or 3, the population of one of these attributes is mandatory.
                opt_flds = ['TRTMTHD2','TRTMTHD3'] # optional fields
                command = """errorList = ["Error on %s %s: For TRTMTHD1, TRTMTHD2 and TRTMTHD3, the population of one of these attributes is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD1] in vnull"""
                for opt_fld in opt_flds:
                    if opt_fld in f:
                        command += """ and cursor[""" + opt_fld + """] in vnull"""
                command += ']'
                exec(command)
                cursor.reset()

                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): For TRTMTHD1, TRTMTHD2 and TRTMTHD3, the population of one of these attributes is mandatory."%len(errorList))

            # TRTCAT1, 2 and 3 - The attribute population must follow the correct coding scheme if populated.
                errorList = ["Error on %s %s: TRTCAT1 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTCAT1] not in vnull + ['REG','RET','SUP']] #*24b15
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTCAT1 must be populated and must follow the correct coding scheme if TRTMTHD1 is populated."%len(errorList))

                if 'TRTCAT2' in f:
                    errorList = ["Error on %s %s: TRTCAT2 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTCAT2] not in vnull + ['REG','RET','SUP']] #*24b15
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT2 must be populated and must follow the correct coding scheme if TRTMTHD1 is populated."%len(errorList))

                if 'TRTCAT3' in f:
                    errorList = ["Error on %s %s: TRTCAT3 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTCAT3] not in vnull + ['REG','RET','SUP']] #*24b15
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT3 must be populated and must follow the correct coding scheme if TRTMTHD1 is populated."%len(errorList))

            # TRTCAT1 and TRTMTHD1
                # If the treatment method is populated (TRTMTHD# != Null) then the associated treatment category must also be populated.
                # The attribute population must follow the correct coding scheme.
                errorList = ["Error on %s %s: TRTCAT1 must be populated and must follow the correct coding scheme if TRTMTHD1 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] not in vnull
                                if cursor[TRTCAT1] not in ['REG','RET','SUP']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTCAT1 must be populated and must follow the correct coding scheme if TRTMTHD1 is populated."%len(errorList))

            # TRTCAT2 and TRTMTHD2
                # If the treatment method is populated (TRTMTHD# != Null) then the associated treatment category must also be populated.
                if 'TRTMTHD2' in f:
                    if 'TRTCAT2' in f:
                        errorList = ["Error on %s %s: TRTCAT2 must be populated and must follow the correct coding scheme if TRTMTHD2 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTMTHD2] not in vnull
                                        if cursor[TRTCAT2] not in ['REG','RET','SUP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTCAT2 must be populated and must follow the correct coding scheme if TRTMTHD2 is populated."%len(errorList))
                    else:
                        fieldValComUpdate[lyr].append("Missing TRTCAT2: The presence of TRTCAT2 field is mandatory if TRTMTHD2 exists.")
                        fieldValUpdate[lyr] = 'Invalid'          

            # TRTCAT3 and TRTMTHD3
                # If the treatment method is populated (TRTMTHD# != Null) then the associated treatment category must also be populated.
                if 'TRTMTHD3' in f:
                    if 'TRTCAT3' in f:
                        errorList = ["Error on %s %s: TRTCAT3 must be populated and must follow the correct coding scheme if TRTMTHD3 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTMTHD3] not in vnull
                                        if cursor[TRTCAT3] not in ['REG','RET','SUP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTCAT3 must be populated and must follow the correct coding scheme if TRTMTHD3 is populated."%len(errorList))
                    else:
                        fieldValComUpdate[lyr].append("Missing TRTCAT3: The presence of TRTCAT3 field is mandatory if TRTMTHD3 exists.")
                        fieldValUpdate[lyr] = 'Invalid'  

            # TRTMTHD chemical count
                # PRODTYPE, RATE_AI, and APPNUM fields become mandatory fields when any of the TRTMTHD are either CLCHEMA or CLCHEMG.
                trtmthd1_chem = ['y' for row in cursor if cursor[TRTMTHD1] in ['CLCHEMA','CLCHEMG']]
                cursor.reset()

                if 'TRTMTHD2' in f:
                    trtmthd2_chem = ['y' for row in cursor if cursor[TRTMTHD2] in ['CLCHEMA','CLCHEMG']]
                else:
                    trtmthd2_chem = []
                cursor.reset()

                if 'TRTMTHD3' in f:
                    trtmthd3_chem = ['y' for row in cursor if cursor[TRTMTHD3] in ['CLCHEMA','CLCHEMG']]
                else:
                    trtmthd3_chem = []
                cursor.reset()

                trtmthd_chem_count = len(trtmthd1_chem + trtmthd2_chem + trtmthd3_chem)

            # PRODTYPE
                if 'PRODTYPE' in f:
                    # The product type attribute must be present and populated when any of the treatment methods are mechanical or prescribed burn.
                    trt2_check = " or cursor[TRTMTHD2] in ['CLCHEMA','CLCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] in ['CLCHEMA','CLCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: PRODTYPE must be populated when any of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PRODTYPE] in vnull
                                    if cursor[TRTMTHD1] in ['CLCHEMA','CLCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PRODTYPE must be populated when any of the treatment methods are chemical."%len(errorList))

                    # The product type must be null when all the treatment methods are mechanical or prescribed burn. (when none of the treatment methods are chemial)
                    trt2_check = " and cursor[TRTMTHD2] not in ['CLCHEMA','CLCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " and cursor[TRTMTHD3] not in ['CLCHEMA','CLCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: PRODTYPE must be null when none of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PRODTYPE] not in vnull
                                    if cursor[TRTMTHD1] not in ['CLCHEMA','CLCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PRODTYPE must be null when none of the treatment methods are chemical."%len(errorList))

                elif trtmthd_chem_count > 0:
                    # The product type attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    fieldValComUpdate[lyr].append("Missing PRODTYPE: The presence of PRODTYPE field is mandatory when any of the treatment methods are chemical.")
                    fieldValUpdate[lyr] = 'Invalid'

            # RATE_AI
                if 'RATE_AI' in f:
                    # The product quantity attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    trt2_check = " or cursor[TRTMTHD2] in ['CLCHEMA','CLCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] in ['CLCHEMA','CLCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: RATE_AI must be greater than 0 and less than or equal to 9.99 when any of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[RATE_AI] == None or cursor[RATE_AI] <= 0 or cursor[RATE_AI] > 9.99
                                    if cursor[TRTMTHD1] in ['CLCHEMA','CLCHEMG']""" + trt2_check + trt3_check + "]" #*24b09
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): RATE_AI must be greater than 0 and less than or equal to 9.99 when any of the treatment methods are chemical."%len(errorList))

                    # The product quantity must be zero (or null) when all the treatment methods are mechanical or prescribed burn. (when none of the treatment methods are chemial)
                    trt2_check = " and cursor[TRTMTHD2] not in ['CLCHEMA','CLCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " and cursor[TRTMTHD3] not in ['CLCHEMA','CLCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: RATE_AI must be zero or null when none of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[RATE_AI] not in [None, 0]
                                    if cursor[TRTMTHD1] not in ['CLCHEMA','CLCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): RATE_AI must be zero or null when none of the treatment methods are chemical."%len(errorList))

                elif trtmthd_chem_count > 0:
                    # The product quantity attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    fieldValComUpdate[lyr].append("Missing RATE_AI: The presence of RATE_AI field is mandatory when any of the treatment methods are chemical.")
                    fieldValUpdate[lyr] = 'Invalid'

            # APPNUM
                if 'APPNUM' in f:
                    # The number of application attribute must be present and greater than 0 when any of the treatment methods are aerial or ground chemial
                    trt2_check = " or cursor[TRTMTHD2] in ['CLCHEMA','CLCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] in ['CLCHEMA','CLCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: APPNUM must be greater than 0 and less than or equal to 9 when any of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[APPNUM] == None or cursor[APPNUM] <= 0 or cursor[APPNUM] > 9
                                    if cursor[TRTMTHD1] in ['CLCHEMA','CLCHEMG']""" + trt2_check + trt3_check + "]" #*24b09
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): APPNUM must be greater than 0 and less than or equal to 9 when any of the treatment methods are chemical."%len(errorList))

                    # The number of application must be zero (or null) when all the treatment methods are mechanical or prescribed burn. (when none of the treatment methods are chemial)
                    trt2_check = " and cursor[TRTMTHD2] not in ['CLCHEMA','CLCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " and cursor[TRTMTHD3] not in ['CLCHEMA','CLCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: APPNUM must be zero or null when none of the treatment methods are chemical."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[APPNUM] not in [None, 0]
                                    if cursor[TRTMTHD1] not in ['CLCHEMA','CLCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): APPNUM must be zero or null when none of the treatment methods are chemical."%len(errorList))

                elif trtmthd_chem_count > 0:
                    # The number of application attribute must be present and populated when any of the treatment methods are aerial or ground chemial
                    fieldValComUpdate[lyr].append("Missing APPNUM: The presence of APPNUM field is mandatory when any of the treatment methods are chemical.")
                    fieldValUpdate[lyr] = 'Invalid'

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking WTX   ############################

        if lyrAcro == "WTX":
            try: # need try and except block here for cases such as not having mandatory fields.

            # WATXID
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: The population of WATXID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[WATXID] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of WATXID is mandatory."%len(errorList))

                # The WATXID attribute must contain a unique value # This is no longer the case in 2020 and thereafter. *2020.12.001
                # watxidList = [cursor[WATXID] for row in cursor]
                # cursor.reset()
                # if len(set(watxidList)) < len(watxidList):
                #     duplicateCount = len(watxidList) - len(set(watxidList))
                #     criticalError += 1
                #     recordValCom[lyr].append("Error on %s record(s): The WATXID attribute must contain a unique value."%duplicateCount)

            # WATXTYPE
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: WATXTYPE must follow the correct coding scheme and a blank or null value is not a valid code."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[WATXTYPE] not in ['BRID','TEMP','CULV','MULTI','FORD','ICE','BOX','ARCH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): WATXTYPE must follow the correct coding scheme and a blank or null value is not a valid code."%len(errorList))
             
            # CONSTRCT
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: CONSTRCT must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[CONSTRCT] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONSTRCT must be populated with Y or N."%len(errorList))
             
            # MONITOR
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: MONITOR must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[MONITOR] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MONITOR must be populated with Y or N."%len(errorList))

            # REMOVE
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: REMOVE must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REMOVE] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): REMOVE must be populated with Y or N."%len(errorList))
             
            # REPLACE
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: REPLACE must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REPLACE] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): REPLACE must be populated with Y or N."%len(errorList))

            # CONSTRCT, REMOVE, MONITOR, and REPLACE and TRANS   *24b18
                # At a minimum, one of Construction, Removal, Monitoring or Replacement must occur for each record.
                errorList = ["Error on %s %s: At a minimum, one of Construction, Removal, Monitoring, Replacement, or Transfer must occur for each record."%(id_field, cursor[id_field_idx]) for row in cursor
                                if 'Y' not in [cursor[CONSTRCT], cursor[MONITOR], cursor[REMOVE], cursor[REPLACE], cursor[TRANS]]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): At a minimum, one of Construction, Removal, Monitoring, Replacement, or Transfer must occur for each record."%len(errorList))

            # REVIEW
                # The population of this attribute is mandatory where CONSTRCT = Y or REMOVE = Y or REPLACE = Y.
                errorList = ["Error on %s %s: REVIEW must be populated where CONSTRCT, REMOVE, or REPLACE occurs."%(id_field, cursor[id_field_idx]) for row in cursor
                                if 'Y' in [cursor[CONSTRCT], cursor[REMOVE], cursor[REPLACE]]
                                if cursor[REVIEW] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): REVIEW must be populated where CONSTRCT, REMOVE, or REPLACE occurs."%len(errorList))

                # The attribute population must follow the correct coding scheme (if populated)
                errorList = ["Error on %s %s: REVIEW must follow the correct coding scheme, if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REVIEW] not in ['STANDARD','REVIEW'] + vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): REVIEW must follow the correct coding scheme, if populated."%len(errorList))

            # ROADID
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: The population of ROADID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ROADID] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of ROADID is mandatory."%len(errorList))

            # TRANS
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: TRANS must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRANS] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRANS must be populated with Y or N."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking WSY   ############################
        # This layer is new in 2020

        if lyrAcro == "WSY":
            try: # need try and except block here for cases such as not having mandatory fields.

            # WSYID
                # The population of this attribute is mandatory
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: The population of WSYID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[WSYID] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of WSYID is mandatory."%len(errorList))

            # TYPE
                # The population of this attribute is mandatory
                # The attribute population must follow the correct coding scheme.
                # A blank or null value is not a valid code
                errorList = ["Error on %s %s: TYPE must follow the correct coding scheme and a blank or null value is not a valid code."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TYPE] not in ['THY','TMY','LMY']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TYPE must follow the correct coding scheme and a blank or null value is not a valid code."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1


#    Still in this for loop: "for lyr in summarytbl.keys():"

        if criticalError > 0:
            recordVal[lyr] = "Invalid-Critical"
        elif systemError:
            recordVal[lyr] = "N/A"
        elif minorError > 0:
            recordVal[lyr] = "Invalid-Minor"
        else:
            recordVal[lyr] = "Valid"

        del cursor # kill cursor

        if verbose:
            for errors_flagged in recordValCom[lyr]:
                arcpy.AddMessage('  - ' + errors_flagged)
            arcpy.AddMessage('') # just to add new line.

    return [errorDetail, recordVal, recordValCom, fieldValUpdate, fieldValComUpdate]







# Tester:
if __name__ == '__main__':
    pass