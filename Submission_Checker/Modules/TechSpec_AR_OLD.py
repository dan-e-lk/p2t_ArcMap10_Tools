#-------------------------------------------------------------------------------
# Name:         TechSpec_AR.py
# Purpose:      This module checkes every validation statements under appendix 1
#               of Annual Report Tech Spec 2009
#
# Author:       NER RIAU, Ministry of Natural Resources and Forestry
#
# Notes:        To find the validation code, run Search (Ctrl+F) for validation header such as "A1.1.2")
# Created:      Mar 21, 2017
#
#-------------------------------------------------------------------------------
import arcpy
import os, sys
import Reference as R
import pprint

verbose = True

lyrInfo = {
# Lyr acronym            name                           mandatory fields                                            Data Type   Tech Spec       Tech Spec URL

    "AGG":  ["Forestry Aggregate Pits",                 ['PIT_ID','REHABREQ','REHAB','TONNES'],                     'point',    'A1.10',        'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=106'],
    "FTG":  ["Free-To-Grow",                            ['ARDSTGRP','YRDEP','DSTBFU','SGR','TARGETFU','FTG'],       'polygon',  'A1.9',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=99'],
    "HRV":  ["Harvest Disturbance",                     ['HARVCAT','SILVSYS','HARVMTHD','SGR','DSTBFU'],            'polygon',  'A1.2',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=64'],
    "NDB":  ["Natural Disturbance",                     ['NDEPCAT','VOLCON','VOLHWD','DSTBFU'],                     'polygon',  'A1.1',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=61'],
    "PRT":  ["Protection Treatment",                    ['TRTMTHD1'],                                               'polygon',  'A1.8',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=96'],
    "RDS":  ["Road Construction and Road Use",          ['ROADID','CONSTRCT','DECOM','ACCESS','MAINTAIN','MONITOR'],'arc',      'A1.3',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=72'],
    "RGN":  ["Regeneration Treatment",                  ['TRTMTHD1','TRTCAT1'],                                     'polygon',  'A1.5',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=82'],
    "SCT":  ["Slash and Chip Treatment",                ['SLASHPIL','CHIPPIL','BURN','MECHANIC','REMOVAL'],         'arc',      'A1.12',        'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=110'],
    "SGR":  ["Silvicultural Ground Rule Update",        ['SGR'],                                                    'polygon',  'A1.11',        'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=109'],
    "SIP":  ["Site Preparation Treatment",              ['TRTMTHD1'],                                               'polygon',  'A1.6',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=88'],
    "TND":  ["Tending Treatment",                       ['TRTMTHD1'],                                               'polygon',  'A1.7',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=92'],
    "WTX":  ["Water Crossings",                         ['WATXID','WATXTYPE','CONSTRCT','MONITOR','REMOVE','ROADID'],'point',   'A1.4',        'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=78']
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
        f = summarytbl[lyr][4] + summarytbl[lyr][3] ## f is the list of all fields found in lyr. eg. ['PIT_ID', 'PIT_OPEN', 'PITCLOSE', 'CAT9APP', 'OBJECTID', 'MU110_17AGP00_', 'MU110_17AGP00_ID', 'PIT_NAME']

        # each fieldname is a new variable where the value is its index number - for example, OBJECTID = 0.
        for i in range(len(f)):
            try:
                exec(f[i] + "=" + str(i)) ## POLYID = 0, POLYTYPE = 1, etc.
            except:
                pass # some field names are not valid as a variable name.

        # feature classes have ObjectID, shapefiles and coverages have FID. Search for ObjectID's index value in f, if not possible, search for FID's index value in f. else use whatever field comes first as the ID field.
        id_field = R.find_IdField(f, dataformat) # *23408  This will normally return OBJECTID for feature classes and FID for shapefile and coverage.
        id_field_idx = f.index(id_field)

        cursor = arcpy.da.SearchCursor(lyr,f) # this line was missing in version 2.4a *24b03
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
        arcpy.AddMessage("  Checking each record in %s (%s records, %s artifacts)..."%(lyr,recordCount, artifact_count))
        recordValCom[lyr].append("Total %s records (with %s artifacts)."%(recordCount, artifact_count))



#       ######### Going through each layer type in alphabetical order ##########


        ###########################  Checking AGG   ############################

        if lyrAcro == "AGG":
            try: # need try and except block here for cases such as not having mandatory fields.
            # PIT_ID
                errorList = ["Error on %s %s: The population of PIT_ID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[PIT_ID] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of PIT_ID is mandatory (A1.10.1)."%len(errorList))

                pitIDList = [cursor[PIT_ID] for row in cursor]
                cursor.reset()
                if len(set(pitIDList)) < len(pitIDList):
                    duplicateCount = len(pitIDList) - len(set(pitIDList))
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The PIT_ID attribute must contain a unique value (A1.10.1)."%duplicateCount)

            # REHABREQ
                errorList = ["Error on %s %s: REHABREQ must be a number of hectares between 0 and 9.9."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REHABREQ] in vnull
                                or (cursor[REHABREQ] < 0 or cursor[REHABREQ] > 9.9)]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): REHABREQ must be a number of hectares between 0 and 9.9 (A1.10.2)."%len(errorList))

                if "PITCLOSE" in f:
                    errorList = ["Error on %s %s: if REHABREQ > 0, then the pit closure date should be null."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[REHABREQ] > 0 and cursor[PITCLOSE] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Error on %s record(s): if REHABREQ > 0, then the pit closure date should be null (A1.10.2, A1.10.4)."%len(errorList)) # this also applies to A1.10.4

                errorList = ["Error on %s %s: REHABREQ should be less than or equal to 3."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REHABREQ] > 3 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Error on %s record(s): REHABREQ should be less than or equal to 3 (A1.10.2)."%len(errorList))

            # REHAB
                errorList = ["Error on %s %s: REHAB must be a number of hectares between 0 and 9.9."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REHAB] in vnull
                                or (cursor[REHAB] < 0 or cursor[REHAB] > 9.9)]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): REHAB must be a number of hectares between 0 and 9.9 (A1.10.3)."%len(errorList))

                errorList = ["Error on %s %s: If REHAB = 0 then the TONNES should not be zero."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REHAB] == 0 and cursor[TONNES] == 0]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Error on %s record(s): If REHAB = 0 then the TONNES should not be zero (A1.10.3)."%len(errorList))

                errorList = ["Error on %s %s: REHAB should be less than or equal to 3."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[REHAB] > 3 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Error on %s record(s): REHAB should be less than or equal to 3 (A1.10.3)."%len(errorList))

            # PITCLOSE
                if 'PITCLOSE' in f:
                    errorList = ["Error on %s %s: PITCLOSE attribute must follow the correct format (a blank or null is valid)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PITCLOSE] not in vnull and R.fimdate(cursor[PITCLOSE]) is None]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PITCLOSE attribute must follow the correct format (a blank or null is valid) (A1.10.4)."%len(errorList))

                    # "When PITCLOSE is not null, then REHABREQ should be 0" has already been covered in A1.10.2.

                    errorList = ["Error on %s %s: PITCLOSE date should be within the fiscal year."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PITCLOSE] not in vnull and R.fimdate(cursor[PITCLOSE]) is not None ##if PITCLOSE is populated with the correct format
                                    if R.fimdate(cursor[PITCLOSE]) < R.fimdate(str(year) + 'APR01')
                                    or R.fimdate(cursor[PITCLOSE]) > R.fimdate(str(year+1) + 'MAR31')]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Error on %s record(s): PITCLOSE date should be within the fiscal year (%s) (A1.10.4)."%(len(errorList),year))

            # TONNES
                errorList = ["Error on %s %s: TONNES must be a number between 0 and 99,999,999."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TONNES] in vnull
                                or (cursor[TONNES] < 0 or cursor[TONNES] > 99999999)]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PITCLOSE attribute must follow the correct format (A1.10.5)."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking FTG   ############################

        if lyrAcro == "FTG":
            try: # need try and except block here for cases such as not having mandatory fields.

            # ARDSTGRP
                errorList = ["Error on %s %s: ARDSTGRP must be either HARV or NAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ARDSTGRP] not in ['HARV','NAT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ARDSTGRP must be either HARV or NAT (A1.9.1)."%len(errorList))

            # YRDEP
                errorList = ["Error on %s %s: YRDEP must be populated and must not be zero."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[YRDEP] in vnull or cursor[YRDEP] == 0]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): YRDEP must be populated (A1.9.2)."%len(errorList))

                errorList = ["Warning on %s %s: YRDEP should be greater than AR year minus 20."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[YRDEP] not in vnull
                                if int(cursor[YRDEP] or 0) <= year - 20 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): YRDEP should be greater than AR year minus 20 (A1.9.2)."%len(errorList))

            # DSTBFU
                errorList = ["Error on %s %s: DSTBFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DSTBFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DSTBFU must be populated (A1.9.3)."%len(errorList))

            # SGR
                errorList = ["Error on %s %s: SGR must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SGR] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SGR must be populated (A1.9.4)."%len(errorList))

            # TARGETFU
                errorList = ["Error on %s %s: TARGETFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TARGETFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TARGETFU must be populated (A1.9.5)."%len(errorList))

            # FTG
                errorList = ["Error on %s %s: FTG must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[FTG] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FTG must be populated with Y or N (A1.9.6)."%len(errorList))

            # FTG - Y counter
                ftg_y = ["y" for row in cursor if cursor[FTG] =='Y']
                cursor.reset()
                ftg_y_count = len(ftg_y)

            # FTGFU
                if 'FTGFU' in f:
                    errorList = ["Error on %s %s: FTGFU must be populated where FTG = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[FTGFU] in vnull and cursor[FTG] == 'Y']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): FTGFU must be populated where FTG = Y (A1.9.7)."%len(errorList))

                elif ftg_y_count > 0:
                    fieldValComUpdate[lyr].append("Missing FTGFU: FTGFU field is mandatory where FTG = Y.")
                    fieldValUpdate[lyr] = 'Invalid'

            # SPCOMP
                if 'SPCOMP' in f:
                    errorList = ["Error on %s %s: SPCOMP must be populated when FTG = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[FTG] == 'Y'
                                    if cursor[SPCOMP] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SPCOMP must be populated when FTG = Y (A1.9.8)."%len(errorList))

                    # code to check spcomp
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
                elif ftg_y_count > 0:
                    fieldValComUpdate[lyr].append("Missing SPCOMP: SPCOMP field is mandatory where FTG = Y.")
                    fieldValUpdate[lyr] = 'Invalid'

            # HT
                if 'HT' in f:
                    errorList = ["Error on %s %s: HT must be greater than or equal to 0.8 when FTG = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[HT] < 0.8 and cursor[FTG] == 'Y']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): HT must be greater than or equal to 0.8 when FTG = Y (A1.9.9)."%len(errorList))

                    errorList = ["Error on %s %s: HT must be between 0 and 40 if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[HT] not in vnull
                                    if cursor[HT] < 0 or cursor[HT] > 40]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): HT must be between 0 and 40 if populated (A1.9.9)."%len(errorList))

                elif ftg_y_count > 0:
                    fieldValComUpdate[lyr].append("Missing HT: HT field is mandatory where FTG = Y.")
                    fieldValUpdate[lyr] = 'Invalid'

            # STKG
                if 'STKG' in f:
                    errorList = ["Error on %s %s: STKG must be greater than or equal to 0.4 when FTG = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[STKG] < 0.4 and cursor[FTG] == 'Y']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): STKG must be greater than or equal to 0.4 when FTG = Y (A1.9.9)."%len(errorList))

                    errorList = ["Error on %s %s: STKG must be between 0 and 4 if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[STKG] not in vnull
                                    if cursor[STKG] < 0 or cursor[STKG] > 4]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): STKG must be between 0 and 4 if populated (A1.9.9)."%len(errorList))

                elif ftg_y_count > 0:
                    fieldValComUpdate[lyr].append("Missing STKG: STKG field is mandatory where FTG = Y.")
                    fieldValUpdate[lyr] = 'Invalid'


            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking HRV   ############################

        if lyrAcro == "HRV":
            try: # need try and except block here for cases such as not having mandatory fields.
            # HARVCAT
                errorList = ["Error on %s %s: HARVCAT must be populated and follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVCAT] not in ['REGULAR','BRIDGING','REDIRECT','ROADROW','ACCELER','FRSTPASS','SCNDPASS','SALVAGE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVCAT must be populated and follow the correct coding scheme (A1.2.1)."%len(errorList))

                errorList = ["Error on %s %s: HARVCAT = BRIDGING is the only available when AR year is equal to the FMP start year."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVCAT] == 'BRIDGING'
                                if year != fmpStartYear]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): BRIDGING is the only available when AR year is equal to the FMP start year (A1.2.1)."%len(errorList))

            # SILVSYS
                errorList = ["Error on %s %s: SILVSYS must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] not in ['CC','SE','SH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be populated with the correct coding scheme (A1.2.2)."%len(errorList))

            # HARVMTHD
                errorList = ["Error on %s %s: HARVMTHD must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVMTHD] not in ['CONVENTION','BLOCKSTRIP','PATCH','SEEDTREE','HARP','THINCOM','UNIFORM','STRIP','GROUPSH','SINGLETREE','GROUPSE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVMTHD must be populated with the correct coding scheme (A1.2.3)."%len(errorList))

                # SILVSYS = SE
                errorList = ["Error on %s %s: HARVMTHD = SINGLETREE or GROUPSE is only valid if SILVSYS = SE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVMTHD] in ['SINGLETREE','GROUPSE']
                                if cursor[SILVSYS] != 'SE' ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVMTHD = SINGLETREE or GROUPSE is only valid if SILVSYS = SE (A1.2.3)."%len(errorList))

                # SILVSYS = SH
                errorList = ["Error on %s %s: HARVMTHD = UNIFORM, STRIP or GROUPSH is only valid if SILVSYS = SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVMTHD] in ['UNIFORM','STRIP','GROUPSH']
                                if cursor[SILVSYS] != 'SH' ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVMTHD = UNIFORM, STRIP or GROUPSH is only valid if SILVSYS = SH (A1.2.3)."%len(errorList))

                # SILVSYS = CC
                errorList = ["Error on %s %s: HARVMTHD = CONVENTION, BLOCKSTRIP, PATCH, SEEDTREE, or HARP is only available if SILVSYS = CC."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVMTHD] in ['CONVENTION','BLOCKSTRIP','PATCH','SEEDTREE','HARP']
                                if cursor[SILVSYS] != 'CC' ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVMTHD = CONVENTION, BLOCKSTRIP, PATCH, SEEDTREE, or HARP is only available if SILVSYS = CC (A1.2.3)."%len(errorList))

                # HARVMTHD = THINCOM
                errorList = ["Error on %s %s: HARVMTHD = THINCOM is only available if SILVSYS = CC or SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVMTHD] == 'THINCOM'
                                if cursor[SILVSYS] not in ['CC','SH'] ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVMTHD = THINCOM is only available if SILVSYS = CC or SH (A1.2.3)."%len(errorList))

            # count where SILVSYS = SH
                silv_sh_list = ["SH" for row in cursor if cursor[SILVSYS] == 'SH']
                cursor.reset()
                silv_sh_count = len(silv_sh_list)

            # MGMTSTG
                if 'MGMTSTG' in f:
                    errorList = ["Error on %s %s: MGMTSTG must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[MGMTSTG] not in vnull
                                    if cursor[MGMTSTG] not in ['PREPCUT','SEEDCUT','FIRSTCUT','LASTCUT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTSTG must follow the correct coding scheme if populated (A1.2.4)."%len(errorList))

                    errorList = ["Error on %s %s: MGMTSTG must be populated with the correct coding scheme if SILVSYS = SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[SILVSYS] == 'SH'
                                    if cursor[MGMTSTG] not in ['PREPCUT','SEEDCUT','FIRSTCUT','LASTCUT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTSTG must be populated with the correct coding scheme if SILVSYS = SH (A1.2.4)."%len(errorList))

                    errorList = ["Error on %s %s: MGMTSTG must be null if SILVSYS = SE or CC or if HARVMTHD = THINCOM."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[SILVSYS] in ['SE','CC'] or cursor[HARVMTHD] == 'THINCOM'
                                    if cursor[MGMTSTG] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTSTG must be null if SILVSYS = SE or CC or if HARVMTHD = THINCOM (A1.2.4)."%len(errorList))

                elif silv_sh_count > 0:
                   fieldValComUpdate[lyr].append("Missing MGMTSTG: The presence of MGMTSTG field is mandatory where SILVSYS = SH.")
                   fieldValUpdate[lyr] = 'Invalid'

            # count where HARVMTHD = BLOCKSTRIP
                harvm_blkstr_list = ["blk" for row in cursor if cursor[HARVMTHD] == 'BLOCKSTRIP']
                cursor.reset()
                harvm_blkstr_count = len(harvm_blkstr_list)            

            # ESTAREA
                if 'ESTAREA' in f:
                    errorList = ["Error on %s %s: ESTAREA must be between 0.01 and 1 if HARVMTHD = BLOCKSTRIP."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[HARVMTHD] == 'BLOCKSTRIP'
                                    if cursor[ESTAREA] < 0.01 or cursor[ESTAREA] > 1]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ESTAREA must be between 0.01 and 1 if HARVMTHD = BLOCKSTRIP (A1.2.5)."%len(errorList))

                elif harvm_blkstr_count > 0:
                   fieldValComUpdate[lyr].append("Missing ESTAREA: The presence of ESTAREA field is mandatory where HARVMTHD = BLOCKSTRIP.")
                   fieldValUpdate[lyr] = 'Invalid'

            # SGR
                errorList = ["Error on %s %s: SGR must be populated unless HARVCAT = ROADROW."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[HARVCAT] != 'ROADROW'
                                if cursor[SGR] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SGR must be populated unless HARVCAT = ROADROW (A1.2.6)."%len(errorList))

            # DSTBFU
                errorList = ["Error on %s %s: DSTBFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DSTBFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DSTBFU must be populated (A1.2.7)."%len(errorList))


            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1


        ###########################  Checking NDB   ############################

        if lyrAcro == "NDB":
            try: # need try and except block here for cases such as not having mandatory fields.

            # NDEPCAT
                errorList = ["Error on %s %s: NDEPCAT must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[NDEPCAT] not in ['BLOWDOWN','DISEASE','DROUGHT','FIRE','FLOOD','ICE','INSECTS','SNOW']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): NDEPCAT must be populated with the correct coding scheme (A1.1.1)."%len(errorList))

            # VOLCON
                errorList = ["Error on %s %s: VOLCON must be between 0 and 9,999,999."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[VOLCON] < 0 or cursor[VOLCON] > 9999999 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): VOLCON must be between 0 and 9,999,999 (A1.1.2)."%len(errorList))

            # VOLHWD
                errorList = ["Error on %s %s: VOLHWD must be between 0 and 9,999,999."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[VOLHWD] < 0 or cursor[VOLHWD] > 9999999 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): VOLHWD must be between 0 and 9,999,999 (A1.1.3)."%len(errorList))

            # VOLCON and VOLHWD cannot both be zero
                errorList = ["Error on %s %s: VOLCON and VOLHWD cannot both be zero."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[VOLCON] in [0, None] and cursor[VOLHWD] in [0, None]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): VOLCON and VOLHWD cannot both be zero (A1.1.2, A1.1.3)."%len(errorList))

            # DSTBFU
                errorList = ["Error on %s %s: DSTBFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DSTBFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DSTBFU must be populated (A1.1.4)."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1


        ###########################  Checking PRT   ############################

        if lyrAcro == "PRT":
            try: # need try and except block here for cases such as not having mandatory fields.

            # TRTMTHD1
                errorList = ["Error on %s %s: TRTMTHD1 must be populated and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SILVSYS] not in ['PCHEMA','PCHEMG','PMANUAL']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTMTHD1 must be populated and must follow the correct coding scheme (A1.8.1)."%len(errorList))

            # TRTMTHD2
                if 'TRTMTHD2' in f:
                    errorList = ["Error on %s %s: If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme."%cursor[f.index('OBJECTID')] for row in cursor
                                    if (cursor[TRTMTHD1] in vnull and cursor[TRTMTHD2] not in vnull)
                                    or cursor[TRTMTHD2] not in vnull + ['PCHEMA','PCHEMG','PMANUAL']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme (A1.8.1)."%len(errorList))

            # TRTMTHD3
                if 'TRTMTHD3' in f:
                    if 'TRTMTHD2' in f:
                        errorList = ["Error on %s %s: If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme."%cursor[f.index('OBJECTID')] for row in cursor
                                        if ((cursor[TRTMTHD1] in vnull or cursor[TRTMTHD2] in vnull) and cursor[TRTMTHD3] not in vnull)
                                        or cursor[TRTMTHD3] not in vnull + ['PCHEMA','PCHEMG','PMANUAL']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme (A1.8.1)."%len(errorList))
                    else:
                        fieldValUpdate[lyr] = 'Invalid'
                        fieldValComUpdate[lyr].append('TRTMTHD2 is mandatory when TRTMTHD3 is present.')

            # TRTCAT1
                if 'TRTCAT1' in f:
                    errorList = ["Error on %s %s: TRTCAT1 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[SILVSYS] not in ['REG','RET','SUP'] + vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT1 must be populated with the correct coding scheme if populated (A1.8.2)."%len(errorList))

            # TRTCAT2
                if 'TRTCAT2' in f:
                    errorList = ["Error on %s %s: TRTCAT2 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[SILVSYS] not in ['REG','RET','SUP'] + vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT2 must be populated with the correct coding scheme if populated (A1.8.2)."%len(errorList))

            # TRTCAT3
                if 'TRTCAT3' in f:
                    errorList = ["Error on %s %s: TRTCAT3 must be populated with the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[SILVSYS] not in ['REG','RET','SUP'] + vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): TRTCAT3 must be populated with the correct coding scheme if populated (A1.8.2)."%len(errorList))

            # TRTMTHD chemical count
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
                    trt2_check = " or cursor[TRTMTHD2] in ['PCHEMA','PCHEMG']" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] in ['PCHEMA','PCHEMG']" if "TRTMTHD3" in f else ""

                    command = """errorList = ["Error on %s %s: PRODTYPE must be populated where TRTMTHD# = PCHEMA or PCHEMG."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[PRODTYPE] in vnull
                                    if cursor[TRTMTHD1] in ['PCHEMA','PCHEMG']""" + trt2_check + trt3_check + "]"
                    exec(command)

                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PRODTYPE must be populated where TRTMTHD# = PCHEMA or PCHEMG (A1.8.3)."%len(errorList))

                # add PRODTYPE = null when all the trtmthd are manual.

                elif trtmthd_chem_count > 0:
                   fieldValComUpdate[lyr].append("Missing PRODTYPE: The presence of PRODTYPE field is mandatory where TRTMTHD# = PCHEMA or PCHEMG.")
                   fieldValUpdate[lyr] = 'Invalid'


            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking RDS   ############################

        if lyrAcro == "RDS":
            try: # need try and except block here for cases such as not having mandatory fields.

            # ROADID
                errorList = ["Error on %s %s: The population of ROADID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ROADID] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of ROADID is mandatory (A1.3.1)."%len(errorList))

            # count where CONSTRCT = Y
                constrct_y_list = ["y" for row in cursor if cursor[CONSTRCT] == 'Y']
                cursor.reset()
                constrct_y_count = len(constrct_y_list)              

            # ROADCLAS
                if 'ROADCLAS' in f:
                    errorList = ["Error on %s %s: ROADCLAS must be populated with the correct coding scheme where CONSTRCT = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[CONSTRCT] == 'Y'
                                    if cursor[ROADCLAS] not in ['B','O','P']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ROADCLAS must be populated with the correct coding scheme where CONSTRCT = Y (A1.3.2)."%len(errorList))

                    errorList = ["Error on %s %s: ROADCLAS must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[ROADCLAS] not in ['B','O','P'] + vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ROADCLAS must follow the correct coding scheme if populated (A1.3.2)."%len(errorList))

                elif constrct_y_count > 0:
                   fieldValComUpdate[lyr].append("Missing ROADCLAS: The presence of ROADCLAS field is mandatory where CONSTRCT = Y.")
                   fieldValUpdate[lyr] = 'Invalid'

            # CONSTRCT
                errorList = ["Error on %s %s: CONSTRCT must be populated and must be Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[CONSTRCT] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONSTRCT must be populated and must be Y or N (A1.3.3)."%len(errorList))

            # DECOM
                errorList = ["Error on %s %s: DECOM must be populated and must be Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DECOM] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DECOM must be populated and must be Y or N (A1.3.4)."%len(errorList))

            # ACCESS
                errorList = ["Error on %s %s: ACCESS must be APPLY or REMOVE if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[ACCESS] not in ['APPLY','REMOVE'] + vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must be APPLY or REMOVE if populated (A1.3.5)."%len(errorList))
                # other ACCESS validations can be found under CONTROL1 & 2 validation below.

            # MAINTAIN
                errorList = ["Error on %s %s: MAINTAIN must be populated and must be Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[MAINTAIN] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MAINTAIN must be populated and must be Y or N (A1.3.6)."%len(errorList))

            # MONITOR
                errorList = ["Error on %s %s: MONITOR must be populated and must be Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[MONITOR] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MONITOR must be populated and must be Y or N (A1.3.7)."%len(errorList))

            # CONSTRCT DECOM ACCESS MAINTAIN and MONITOR
                errorList = ["Error on %s %s: At minimum, one of Construction, Decom, Maintenance, Monitoring or Access Control must occur."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[CONSTRCT] != 'Y' and cursor[DECOM] != 'Y' and cursor[ACCESS] not in ['APPLY','REMOVE'] and cursor[MAINTAIN] != 'Y' and cursor[MONITOR] != 'Y']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): At minimum, one of Construction, Decom, Maintenance, Monitoring or Access Control must occur (A1.3.7)."%len(errorList))            

            # count where ACCESS = APPLY
                access_y_list = ["a" for row in cursor if cursor[ACCESS] == 'APPLY']
                cursor.reset()
                access_y_count = len(access_y_list)               

            # CONTROL1
                if 'CONTROL1' in f:
                    errorList = ["Error on %s %s: CONTROL1 must be populated with the correct coding scheme where ACCESS = APPLY."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[ACCESS] == 'APPLY'
                                    if cursor[CONTROL1] not in ['BERM','GATE','PRIV','SCAR','SIGN','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL1 must be populated with the correct coding scheme where ACCESS = APPLY (A1.3.8)."%len(errorList))

                    errorList = ["Error on %s %s: CONTROL1 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[CONTROL1] not in ['BERM','GATE','PRIV','SCAR','SIGN','SLSH','WATX'] + vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL1 must follow the correct coding scheme if populated (A1.3.8)."%len(errorList))

                elif access_y_count > 0:
                   fieldValComUpdate[lyr].append("Missing CONTROL1: The presence of CONTROL1 field is mandatory where ACCESS = APPLY.")
                   fieldValUpdate[lyr] = 'Invalid'

            # CONTROL2
                if 'CONTROL2' in f:
                    errorList = ["Error on %s %s: CONTROL2 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[CONTROL2] not in ['BERM','GATE','PRIV','SCAR','SIGN','SLSH','WATX'] + vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL2 must follow the correct coding scheme if populated (A1.3.8)."%len(errorList))

            # CONTROL 1 and 2
                if 'CONTROL2' in f and 'CONTROL1' in f:
                    errorList = ["Error on %s %s: CONTROL2 must be null if CONTROL1 is null."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[CONTROL1] in vnull
                                    if cursor[CONTROL2] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL2 must be null if CONTROL1 is null (A1.3.8)."%len(errorList))

                    errorList = ["Warning on %s %s: CONTROL1 and 2 should be null if ACCESS = REMOVE."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[ACCESS] == 'REMOVE'
                                    if cursor[CONTROL1] not in vnull or cursor[CONTROL2] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): CONTROL1 and 2 should be null if ACCESS = REMOVE (A1.3.5)."%len(errorList))

            except (IndexError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1



        ###########################  Checking RGN   ############################

        if lyrAcro == "RGN":
            try: # need try and except block here for cases such as not having mandatory fields.

            # TRTMTHD1
                errorList = ["Error on %s %s: TRTMTHD1 must be populated and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTMTHD1] not in ['CLAAG','NATURAL','HARP','PLANT','SCARIFY','SEED','SEEDSIP','SEEDTREE','STRIPCUT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTMTHD1 must be populated and must follow the correct coding scheme (A1.5.1)."%len(errorList))

            # TRTMTHD2
                if 'TRTMTHD2' in f:
                    errorList = ["Error on %s %s: If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme."%cursor[f.index('OBJECTID')] for row in cursor
                                    if (cursor[TRTMTHD1] in vnull and cursor[TRTMTHD2] not in vnull)
                                    or cursor[TRTMTHD2] not in vnull + ['CLAAG','NATURAL','HARP','PLANT','SCARIFY','SEED','SEEDSIP','SEEDTREE','STRIPCUT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme (A1.5.1)."%len(errorList))

            # TRTMTHD3
                if 'TRTMTHD3' in f:
                    if 'TRTMTHD2' in f:
                        errorList = ["Error on %s %s: If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme."%cursor[f.index('OBJECTID')] for row in cursor
                                        if ((cursor[TRTMTHD1] in vnull or cursor[TRTMTHD2] in vnull) and cursor[TRTMTHD3] not in vnull)
                                        or cursor[TRTMTHD3] not in vnull + ['CLAAG','NATURAL','HARP','PLANT','SCARIFY','SEED','SEEDSIP','SEEDTREE','STRIPCUT']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme (A1.5.1)."%len(errorList))
                    else:
                        fieldValUpdate[lyr] = 'Invalid'
                        fieldValComUpdate[lyr].append('TRTMTHD2 is mandatory when TRTMTHD3 is present.')

            # TRTCAT1
                errorList = ["Error on %s %s: TRTCAT1 must be populated and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTCAT1] not in ['REG','RET','SUP']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRTCAT1 must be populated and must follow the correct coding scheme (A1.5.2)."%len(errorList))

            # TRTCAT1 and TRTMTHD1
                errorList = ["Warning on %s %s: TRTMTHD1 should be PLANT or SEED if TRTCAT1 = RET."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTCAT1] == 'RET'
                                if cursor[TRTMTHD1] not in ['PLANT','SEED']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): TRTMTHD1 should be PLANT or SEED if TRTCAT1 = RET (A1.5.2)."%len(errorList))

                errorList = ["Warning on %s %s: TRTMTHD1 should be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT1 = SUP."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[TRTCAT1] == 'SUP'
                                if cursor[TRTMTHD1] not in ['PLANT','SEED','SCARIFY','SEEDSIP']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): TRTMTHD1 should be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT1 = SUP (A1.5.2)."%len(errorList))

            # TRTCAT2 and TRTMTHD2
                if 'TRTMTHD2' in f:
                    if 'TRTCAT2' in f:
                        errorList = ["Error on %s %s: TRTCAT2 must be populated and must follow the correct coding scheme if TRTMTHD2 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTMTHD2] not in vnull
                                        if cursor[TRTCAT2] not in ['REG','RET','SUP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTCAT2 must be populated and must follow the correct coding scheme if TRTMTHD2 is populated (A1.5.2)."%len(errorList))

                        errorList = ["Warning on %s %s: TRTMTHD2 should be PLANT or SEED if TRTCAT2 = RET."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTCAT2] == 'RET'
                                        if cursor[TRTMTHD2] not in ['PLANT','SEED']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            minorError += 1
                            recordValCom[lyr].append("Warning on %s record(s): TRTMTHD2 should be PLANT or SEED if TRTCAT2 = RET (A1.5.2)."%len(errorList))

                        errorList = ["Warning on %s %s: TRTMTHD2 should be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT2 = SUP."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTCAT2] == 'SUP'
                                        if cursor[TRTMTHD2] not in ['PLANT','SEED','SCARIFY','SEEDSIP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            minorError += 1
                            recordValCom[lyr].append("Warning on %s record(s): TRTMTHD2 should be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT2 = SUP (A1.5.2)."%len(errorList))
                    else:
                        fieldValComUpdate[lyr].append("Missing TRTCAT2: The presence of TRTCAT2 field is mandatory if TRTMTHD2 exists.")
                        fieldValUpdate[lyr] = 'Invalid'                    

            # TRTCAT3 and TRTMTHD3
                if 'TRTMTHD3' in f:
                    if 'TRTCAT3' in f:
                        errorList = ["Error on %s %s: TRTCAT3 must be populated and must follow the correct coding scheme if TRTMTHD3 is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTMTHD3] not in vnull
                                        if cursor[TRTCAT3] not in ['REG','RET','SUP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): TRTCAT3 must be populated and must follow the correct coding scheme if TRTMTHD3 is populated (A1.5.2)."%len(errorList))

                        errorList = ["Warning on %s %s: TRTMTHD3 should be PLANT or SEED if TRTCAT3 = RET."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTCAT3] == 'RET'
                                        if cursor[TRTMTHD3] not in ['PLANT','SEED']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            minorError += 1
                            recordValCom[lyr].append("Warning on %s record(s): TRTMTHD3 should be PLANT or SEED if TRTCAT3 = RET (A1.5.2)."%len(errorList))

                        errorList = ["Warning on %s %s: TRTMTHD3 should be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT3 = SUP."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTCAT3] == 'SUP'
                                        if cursor[TRTMTHD3] not in ['PLANT','SEED','SCARIFY','SEEDSIP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            minorError += 1
                            recordValCom[lyr].append("Warning on %s record(s): TRTMTHD3 should be PLANT, SCARIFY, SEED, OR SEEDSIP if TRTCAT3 = SUP (A1.5.2)."%len(errorList))
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
                if 'ESTAREA' in f:
                    errorList = ["Error on %s %s: ESTAREA must be between 0 and 1.0."%(id_field, cursor[id_field_idx]) for row in cursor
                                     if cursor[ESTAREA] < 0 or cursor[ESTAREA] > 1.0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ESTAREA must be between 0 and 1.0 (A1.5.3)."%len(errorList))


                # ESTAREA must be > 0 if TRTMTHD1, 2 or 3 is STRIPCUT (TRTMTHD2 and 3 are non-mandatory fields)
                    trt2_check = " or cursor[TRTMTHD2] == 'STRIPCUT'" if "TRTMTHD2" in f else ""
                    trt3_check = " or cursor[TRTMTHD3] == 'STRIPCUT'" if "TRTMTHD3" in f else ""
                    command = """errorList = ["Error on %s %s: ESTAREA must be greater than zero when any of the TRTMTHD1, 2 or 3 is STRIPCUT."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD1] == 'STRIPCUT'""" + trt2_check + trt3_check + " if cursor[ESTAREA] <= 0]"
                    exec(command)                    

                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ESTAREA must be greater than zero when any of the TRTMTHD1, 2 or 3 is STRIPCUT (A1.5.3)."%len(errorList))

                # ESTAREA must be > 0 if TRTMTHD1, 2 or 3 is PLANT (TRTMTHD2 and 3 are non-mandatory fields) and both SP1 and SP2 are populated.
                    if 'SP1' in f and 'SP2' in f:
                        trt2_check = " or cursor[TRTMTHD2] == 'PLANT'" if "TRTMTHD2" in f else ""
                        trt3_check = " or cursor[TRTMTHD3] == 'PLANT'" if "TRTMTHD3" in f else ""
                        command = """errorList = ["Error on %s %s: ESTAREA must be greater than zero when any of the TRTMTHD1, 2 or 3 is PLANT and both SP1 and SP2 are populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[TRTMTHD1] == 'PLANT'""" + trt2_check + trt3_check + " if cursor[SP1] not in vnull and cursor[SP2] not in vnull and cursor[ESTAREA] <= 0]"
                        exec(command)                    

                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): ESTAREA must be greater than zero when any of the TRTMTHD1, 2 or 3 is PLANT and both SP1 and SP2 are populated (A1.5.3)."%len(errorList))

                # ESTAREA must be 0 if TRTMTHD1, 2 or 3 is neither PLANT nor STRIPCUT.
                    trt2_check = " and cursor[TRTMTHD2] not in ['PLANT','STRIPCUT']" if "TRTMTHD2" in f else ""
                    trt3_check = " and cursor[TRTMTHD3] not in ['PLANT','STRIPCUT']" if "TRTMTHD3" in f else ""
                    command = """errorList = ["Error on %s %s: ESTAREA must be 0 if TRTMTHD1, 2 or 3 is neither PLANT nor STRIPCUT."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[TRTMTHD1] not in ['PLANT','STRIPCUT']""" + trt2_check + trt3_check + " if cursor[ESTAREA] != 0]"
                    exec(command)                    

                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ESTAREA must be 0 if TRTMTHD1, 2 or 3 is neither PLANT nor STRIPCUT (A1.5.3)."%len(errorList))

                elif trtmthd_stripcut_count > 0:
                    fieldValComUpdate[lyr].append("Missing ESTAREA: The presence of ESTAREA field is mandatory if TRTMTHD# = STRIPCUT exists.")
                    fieldValUpdate[lyr] = 'Invalid'

            # SP1 and SP2
                if 'SP1' in f:
                    errorList = ["Error on %s %s: SP1 must use coding list from OSPCOMP in the FIM FRI Tech Spec, if populated (A1.5.4)."%(id_field, cursor[id_field_idx]) for row in cursor
                                     if cursor[SP1] not in vnull
                                     if cursor[SP1] not in R.SpcListInterp + R.SpcListOther]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SP1 must use coding list from OSPCOMP in the FIM FRI Tech Spec, if populated (A1.5.4)."%len(errorList))

                if 'SP2' in f:
                    errorList = ["Error on %s %s: SP2 must use coding list from OSPCOMP in the FIM FRI Tech Spec, if populated (A1.5.4)."%(id_field, cursor[id_field_idx]) for row in cursor
                                     if cursor[SP2] not in vnull
                                     if cursor[SP2] not in R.SpcListInterp + R.SpcListOther]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SP2 must use coding list from OSPCOMP in the FIM FRI Tech Spec, if populated (A1.5.4)."%len(errorList))

                    if 'TRTMTHD2' in f:
                        errorList = ["Error on %s %s: SP2 must be null if TRTMTHD# is not PLANT (A1.5.4)."%(id_field, cursor[id_field_idx]) for row in cursor
                                         if cursor[TRTMTHD1] != 'PLANT' and cursor[TRTMTHD2] != 'PLANT'
                                         if cursor[SP2] not in vnull]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): SP2 must be null if TRTMTHD# is not PLANT.(A1.5.4)."%len(errorList))
                    else:
                        errorList = ["Error on %s %s: SP2 must be null if TRTMTHD# is not PLANT (A1.5.4)."%(id_field, cursor[id_field_idx]) for row in cursor
                                         if cursor[TRTMTHD1] != 'PLANT'
                                         if cursor[SP2] not in vnull]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): SP2 must be null if TRTMTHD# is not PLANT (A1.5.4)."%len(errorList))

                if 'SP1' in f:
                    if 'TRTMTHD2' in f:
                        errorList = ["Error on %s %s: SP1 must be populated if TRTMTHD# = PLANT (A1.5.4)."%(id_field, cursor[id_field_idx]) for row in cursor
                                         if cursor[TRTMTHD1] == 'PLANT' or cursor[TRTMTHD2] == 'PLANT'
                                         if cursor[SP1] in vnull]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): SP1 must be populated if TRTMTHD# = PLANT (A1.5.4)."%len(errorList))


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