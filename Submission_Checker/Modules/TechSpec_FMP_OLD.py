#-------------------------------------------------------------------------------
# Name:         TechSpec_FMP_OLD.py
# Purpose:      This module checkes every validation statements under appendix 1
#               of FMP Tech Spec 2009
#
# Author:       NER RIAU, Ministry of Natural Resources and Forestry
#
# Notes:        This script is complete ONLY for PCM and BMI check (up to and including 2019 plans).
# Created:      Oct, 2017
#
# Updates:  2018 05 29
#           Introduced new lines for catching NameError and ValueError - printing out exactly what the error is.
#           Any further updates can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog
#-------------------------------------------------------------------------------
import arcpy
import os, sys
import Reference as R
import pprint

verbose = True

lyrInfo = {
# Lyr acronym            name                           mandatory fields                                            Data Type   Tech Spec       Tech Spec URL

    # "AOC":  ["Area of Concern",                         ["AOCID","AOCTYPE"],                                        'polygon',    'A1.5',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=169'],
    "BMI":  ["Base Model Inventory",                    ['POLYID','POLYTYPE','OWNER','YRUPD','SOURCE','FORMOD',
                                                        'DEVSTAGE','YRDEP','SPCOMP','YRORG','HT','STKG','SC',
                                                        'ECOSRC','ECOSITE1','ECOPCT1','ACCESS1','MGMTCON1',
                                                        "MANAGED","SMZ","OMZ","PLANFU","AGESTR","AGE","AVAIL",
                                                        "SILVSYS","NEXTSTG","SI","SISRC","SGR"],                    'polygon',  'A1.1, A1.2','https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=113'],

    # "ERU":  ["Existing Road Use Management Strategies", ['ROADID','ROADCLAS','ACYEAR','RESPONS'],                   'arc',        'A1.9',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=181'],
    # "FDP":  ["Forecast Depletions",                     ['FSOURCE','FYRDEP','FDEVSTAGE'],                           'polygon',    'A1.3',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=163'],
    # "ORB":  ["Operational Road Boundaries",             ['ORBID'],                                                  'polygon',    'A1.8',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=180'],
    # "PAG":  ["Planned Aggregate Extraction Areas",      ['AGAREAID'],                                               'polygon',    'A1.10',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=188'],
    # "PCC":  ["Planned Clearcuts",                       ['PCCID'],                                                  'polygon',    'A1.12',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=192'],
    "PCM":  ["Planning Composite",                      ['POLYID','POLYTYPE','OWNER','YRUPD','SOURCE','FORMOD',
                                                        'DEVSTAGE','YRDEP','SPCOMP','YRORG','HT','STKG','SC',
                                                        'ECOSRC','ECOSITE1','ECOPCT1','ACCESS1','MGMTCON1'],        'polygon',  'A1.1',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=113'],

    # "PHR":  ["Planned Harvest",                         ['SILVSYS','HARVCAT','FUELWOOD'],                           'polygon',    'A1.4',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=166'],
    # "PRC":  ["Planned Road Corridors",                  ['TERM','ROADID','ROADCLAS','ACYEAR'],                      'polygon',    'A1.7',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=172'],
    # "PRP":  ["Planned Residual Patches",                ['RESID'],                                                  'polygon',    'A1.6',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=171'],
    # "PRT":  ["Planned Renewal and Tending",             ['TERM'],                                                   'polygon',    'A1.11',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=189']
        }

# vnull is used to check if an item is NULL or blank.
vnull = [None,'',' ']




def run(gdb, summarytbl, year, fmpStartYear, dataformat):  ## eg. summarytbl = {'MU110_17SAC10': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCTYPE', 'AOCID'], ['OBJECTID', 'MU110_17SAC10_', 'MU110_17SAC10_ID']], 'MU110_17SAC11':...}
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
        arcpy.AddMessage("  Checking each record in %s (%s records, %s artifacts)..."%(lyr,recordCount, artifact_count))
        recordValCom[lyr].append("Total %s records (with %s artifacts)."%(recordCount, artifact_count))


#       ######### Going through each layer type. Starts with PCI BMI OPI FDP, then in alphabetical order ##########


        ########################  Checking PCM and BMI   ########################

        if lyrAcro in ["PCM","BMI"]:
            try: # need try and except block here for cases such as not having mandatory fields.
            # POLYID
                errorList = ["Error on %s %s: The population of POLYID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYID] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of POLYID is mandatory."%len(errorList))

                polyIDList = [cursor[POLYID] for row in cursor if cursor[POLYID] not in vnull ]
                cursor.reset()
                numDuplicates = len(polyIDList) - len(set(polyIDList))
                if numDuplicates > 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The POLYID attribute must contain a unique value."%numDuplicates)

            # POLYTYPE
                errorList = ["Error on %s %s: The population of POLYTYPE is mandatory and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] not in ['WAT','DAL','GRS','ISL','UCL','BSH','RCK','TMS','OMS','FOR']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of POLYTYPE is mandatory and must follow the correct coding scheme."%len(errorList))

                ## "If POLYTYPE attribute does not equal FOR, then FORMOD,DEVSTAGE, OYRORG, OSPCOMP..." can be checked on other fields.

            # OWNER
                errorList = ["Error on %s %s: The population of OWNER is mandatory and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if str(cursor[OWNER]) not in ['0','1','2','3','4','5','6','7','8','9']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of OWNER is mandatory and must follow the correct coding scheme."%len(errorList))

#           # AUTHORTY - only in TechSpec 2009
                if "AUTHORTY" in f:
                    errorList = ["Error on %s %s: AUTHORTY must follow the correct coding scheme or should be blank or null."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AUTHORTY')] not in [None, '', ' ', 'SFL','MNR']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AUTHORTY must follow the correct coding scheme or should be blank or null."%len(errorList))

#           # YRUPD - only in TechSpec 2009
                if "YRUPD" in f:
                    errorList = ["Error on %s %s: YRUPD must be an integer."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if not isinstance(cursor[YRUPD],int)]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): YRUPD must be an integer."%len(errorList))

                    errorList = ["Error on %s %s: YRUPD must be between 1975 and the plan start year minus one."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if isinstance(cursor[YRUPD],int)
                                    if cursor[YRUPD] < 1975 or cursor[YRUPD] >= fmpStartYear]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): YRUPD must be between 1975 and the plan start year minus one."%len(errorList))

            # YRSOURCE - only exists in 2017 tech spec
##                errorList = ["Error on %s %s: The YRSOURCE must be a year less than the plan period start year."%(id_field, cursor[id_field_idx]) for row in cursor
##                                if int(cursor[f.index('YRSOURCE')]) > fmpStartYear - 1]
##                cursor.reset()
##                if len(errorList) > 0:
##                    errorDetail[lyr].append(errorList)
##                    criticalError += 1
##                    recordValCom[lyr].append("Error on %s record(s): The population of YRSOURCE is mandatory and must be a year less than the plan period start year."%len(errorList))

            # SOURCE
                errorList = ["Error on %s %s: The population of SOURCE must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SOURCE] not in ['BASECOVR','DIGITALA','DIGITALP','ESTIMATE','FOC','FORECAST','FRICNVRT','INFRARED','MARKING','OCULARA','OCULARG','OPC','PHOTO','PHOTOLS','PHOTOSS','LOTFIXD','PLOTVAR','RADAR','REGENASS','SEMEXTEN','SEMINTEN','SPECTRAL']] # The 2017 also has 'SUPINFO'
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of SOURCE is mandatory and must follow the correct coding scheme."%len(errorList))

                if lyrAcro == "PCM":
                    errorList = ["Error on %s %s: SOURCE must not have the value FORECAST in PCM."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[SOURCE] == 'FORECAST']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SOURCE must not have the value FORECAST in PCM."%len(errorList))

                    # only in 2009
                errorList = ["Warning on %s %s: SOURCE should not equal ESTIMATE if the DEVSTAGE starts with FTG."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DEVSTAGE] not in vnull
                                if cursor[DEVSTAGE][:3] == 'FTG'
                                if cursor[SOURCE] == 'ESTIMATE']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): SOURCE should not equal ESTIMATE if the DEVSTAGE starts with FTG."%len(errorList))

                    # only in 2009
                errorList = ["Warning on %s %s: SOURCE should be ESTIMATE if the DEVSTAGE starts with NEW."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DEVSTAGE] not in vnull
                                if cursor[DEVSTAGE][:3] == 'NEW'
                                if cursor[SOURCE] != 'ESTIMATE']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): SOURCE should be ESTIMATE if the DEVSTAGE starts with NEW."%len(errorList))

            # FORMOD
                errorList = ["Error on %s %s: FORMOD must be null when POLYTYPE is not equal to FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] != 'FOR'
                                if cursor[FORMOD] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FORMOD must be null when POLYTYPE is not equal to FOR."%len(errorList))

                errorList = ["Error on %s %s: The population of FORMOD is mandatory and must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[FORMOD] not in ['RP','MR','PF']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of FORMOD is mandatory and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

                if "SC" in f:
                    errorList = ["Warning on %s %s: FORMOD attribute should be PF when SC equals 4."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if str(cursor[SC]) == '4'
                                    if cursor[FORMOD] != 'PF']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1                      # minor error!!!!
                        recordValCom[lyr].append("Warning on %s record(s): FORMOD attribute should be PF when SC equals 4."%len(errorList))

            # DEVSTAGE
                errorList = ["Error on %s %s: DEVSTAGE must be null when POLYTYPE is not equal to FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] != 'FOR'
                                if cursor[DEVSTAGE] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DEVSTAGE must be null when POLYTYPE is not equal to FOR."%len(errorList))

                    # significant difference here in 2017 spec
                errorList = ["Error on %s %s: The population of DEVSTAGE is mandatory and must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[DEVSTAGE] not in ['DEPHARV', 'DEPNAT','LOWMGMT','LOWNAT','NEWPLANT','NEWSEED','NEWNAT', 'FTGPLANT','FTGSEED','FTGNAT','THINPRE','THINCOM','BLKSTRIP', 'FRSTPASS','PREPCUT','SEEDCUT','FIRSTCUT','THINCOM','IMPROVE','SELECT','SNGLTREE','GROUPSE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of DEVSTAGE is mandatory and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

                errorList = ["Warning on %s %s: DEVSTAGE should be LOWNAT or FTGNAT if YRDEP = 0."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[YRDEP] == 0
                                if cursor[DEVSTAGE] not in ["LOWNAT", "FTGNAT"] ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): DEVSTAGE should be LOWNAT or FTGNAT if YRDEP = 0."%len(errorList))

                errorList = ["Warning on %s %s: DEVSTAGE should be DEPHARV or DEPNAT if STKG = 0."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[STKG] == 0
                                if cursor[DEVSTAGE] not in ["DEPHARV", "DEPNAT"] ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): DEVSTAGE should be DEPHARV or DEPNAT if STKG = 0."%len(errorList))

                    # this is HT check
                errorList = ["Warning on %s %s: HT should be 0.0 when DEVSTAGE is either DEPHARV or DEPNAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DEVSTAGE] in ['DEPHARV','DEPNAT']
                                if cursor[HT] != 0]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s):  HT should be 0.0 when DEVSTAGE is either DEPHARV or DEPNAT."%len(errorList))

                errorList = ["Warning on %s %s: DEVSTAGE should not be DEPHARV if SC = 4."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SC] == 4
                                if cursor[DEVSTAGE] == "DEPHARV" ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): DEVSTAGE should not be DEPHARV if SC = 4."%len(errorList))

            # YRDEP
                errorList = ["Error on %s %s: Warning YRDEP should be at least a year less than the plan start year."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[YRDEP] > fmpStartYear - 1 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): YRDEP should be at least a year less than the plan start year."%len(errorList))

                errorList = ["Error on %s %s: YRDEP must be greater than or equal to 1900 where POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[YRDEP] < 1900 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): YRDEP must be greater than or equal to 1900 where POLYTYPE = FOR."%len(errorList))

                errorList = ["Warning on %s %s: YRDEP should be greater than or equal to YRORG."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[YRDEP] < cursor[YRORG]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): YRDEP should be greater than or equal to YRORG."%len(errorList))

            # SPCOMP
                errorList = ["Error on %s %s: SPCOMP must not be null when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[SPCOMP] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SPCOMP must not be null when POLYTYPE is FOR."%len(errorList))

                    # code to check spcomp
                    fieldname = "SPCOMP"
                    e1List, e2List, e3List, e4List, w1List = [],[],[],[],[]
                    for row in cursor:
                        if cursor[f.index(fieldname)] not in vnull:
                            check = R.spcVal(cursor[f.index(fieldname)],fieldname)
                            if check is None: ## when no error found
                                pass
                            elif check[0] == "Error1":
                                e1List.append("%s on %s %s: %s"%(check[0],id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Error2":
                                e2List.append("%s on %s %s: %s"%(check[0],id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Error3":
                                e3List.append("%s on %s %s: %s"%(check[0],id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Error4":
                                e4List.append("%s on %s %s: %s"%(check[0],id_field, cursor[id_field_idx],check[1]))
                            elif check[0] == "Warning1":
                                w1List.append("%s on %s %s: %s"%(check[0],id_field, cursor[id_field_idx],check[1]))
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
            # WG (this occurs only in 2009 spec)
                if 'WG' in f:
                    errorList = ["Error on %s %s: WG must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[POLYTYPE] == 'FOR'
                                    if cursor[f.index('WG')].strip().upper() not in ['BF','CE','HE','LA','PJ','PR','PS','PW','SB','SW','SX','OC','AX','BG','BW','BY','MH','MR','MX','OX','PO','PB','OH']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): WG must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

            # YRORG (this occurs only in 2009 spec)
                errorList = ["Error on %s %s: YRORG must be greater than 1600 and less than the plan start year when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if not isinstance(cursor[YRORG],int) or cursor[YRORG] < 1600 or cursor[YRORG] > fmpStartYear - 1 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): YRORG must be greater than 1600 and less than the plan start year when POLYTYPE is FOR."%len(errorList))

                errorList = ["Warning on %s %s: YRORG should not be greater than YRUPD + 5 when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if isinstance(cursor[YRUPD],int)
                                if cursor[YRORG] > cursor[YRUPD] + 5 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s):  YRORG should not be greater than YRUPD + 5 when POLYTYPE is FOR."%len(errorList))


            # HT

                errorList = ["Error on %s %s: HT must be populated and must be between 0 and 40 (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[HT] < 0 or cursor[HT] > 40] # surprisingly this will also catch nulls and empty spaces
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HT must be populated and must be between 0 and 40 (when POLYTYPE = FOR)."%len(errorList))

                errorList = ["Error on %s %s: HT must be greater than zero if the DEVSTAGE does not start with DEP, NEW or LOW (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[HT] <= 0
                                if cursor[DEVSTAGE] not in vnull
                                if cursor[DEVSTAGE][:3] not in ['DEP','NEW','LOW']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HT must be greater than zero if the DEVSTAGE does not start with DEP, NEW or LOW (when POLYTYPE = FOR)."%len(errorList))

                errorList = ["Warning on %s %s: The value of HT/(Plan Start Year - YRORG) should not be greater than 0.5."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if isinstance(cursor[YRORG],int) and isinstance(fmpStartYear,int) and isinstance(cursor[HT],(float, int))
                                if cursor[YRORG] != fmpStartYear
                                if cursor[HT] / (fmpStartYear - cursor[YRORG]) > 0.5]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): The value of HT/(Plan Start Year - YRORG) should not be greater than 0.5."%len(errorList))

                errorList = ["Warning on %s %s: HT should be greater than or equal to 0.8 if DEVSTAGE starts with FTG."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[HT] < 0.8
                                if cursor[DEVSTAGE] not in vnull
                                if cursor[DEVSTAGE][:3] == 'FTG']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): HT should be greater than or equal to 0.8 if DEVSTAGE starts with FTG."%len(errorList))

            # STKG
                errorList = ["Error on %s %s: STKG must be populated and must be between 0 and 4.0 (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[STKG] < 0 or cursor[STKG] > 4] # surprisingly this will also catch nulls and empty spaces
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): STKG must be populated and must be between 0 and 4.0 (when POLYTYPE = FOR)."%len(errorList))

                errorList = ["Error on %s %s: STKG must be greater than zero if the DEVSTAGE starts with FTG (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[STKG] <= 0
                                if cursor[DEVSTAGE] not in vnull
                                if cursor[DEVSTAGE][:3] == 'FTG']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): STKG must be greater than zero if the DEVSTAGE starts with FTG (when POLYTYPE = FOR)."%len(errorList))

                errorList = ["Warning on %s %s: STKG should be greater than or equal to 0.4 if the DEVSTAGE starts with FTG (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[STKG] < 0.4
                                if cursor[DEVSTAGE] not in vnull
                                if cursor[DEVSTAGE][:3] == 'FTG']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): STKG should be greater than 0.4 if the DEVSTAGE starts with FTG (when POLYTYPE = FOR)."%len(errorList))

                errorList = ["Warning on %s %s: STKG should be zero when DEVSTAGE starts with DEP."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[DEVSTAGE] not in vnull
                                if cursor[DEVSTAGE][:3] == 'DEP'
                                if cursor[STKG] != 0]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): STKG should be zero when DEVSTAGE starts with DEP."%len(errorList))



            # SC

                errorList = ["Error on %s %s: SC must be between 0 and 4 when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[SC] < 0 or cursor[SC] > 4] # surprisingly this will also catch nulls and empty spaces
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SC must be between 0 and 4 when POLYTYPE = FOR."%len(errorList))

                errorList = ["Warning on %s %s: SC should be 4 when FORMOD is PF."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[FORMOD] == 'PF'
                                if cursor[SC] != 4 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): SC should be 4 when FORMOD is PF."%len(errorList))


            # ECOSRC

                errorList = ["Error on %s %s: ECOSRC must be populated with the correct coding scheme when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[ECOSRC] not in ['ALGO','DIGITALA','DIGITALP','FOC','FRICNVRT','MARKING','OCULARA','OCULARG','OPC','PHOTO','PHOTOLS','PHOTOPLS','PHOTOSS','PLOTFIXD','PLOTVAR','REGENASS','SEMEXTEN','SEMINTEN']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ECOSRC must be populated with the correct coding scheme when POLYTYPE = FOR."%len(errorList))

            # ECOPCT1 and ECOPCT2

                errorList = ["Error on %s %s: ECOPCT1 must be populated and between 0 to 100 when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[ECOPCT1] < 1 or cursor[ECOPCT1] > 100]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ECOPCT1 must be populated and between 1 to 100 when POLYTYPE = FOR."%len(errorList))

                if "ECOPCT2" in f:
                    errorList = ["Error on %s %s: ECOPCT1 + ECOPCT2 should equal 100 when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[POLYTYPE] == 'FOR'
                                    if cursor[ECOPCT1] + int(cursor[f.index('ECOPCT2')] or 0) != 100]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): ECOPCT1 must be populated and between 0 to 100 when POLYTYPE = FOR."%len(errorList))

                if "ECOPCT2" not in f:
                    errorList = ["Error on %s %s: ECOPCT1 should be 100 when EXCOPCT2 field does not exist (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[POLYTYPE] == 'FOR'
                                    if cursor[ECOPCT1] != 100]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): ECOPCT1 must be 100 when POLYTYPE = FOR and when EXCOPCT2 field does not exist."%len(errorList))

            # ACCESS1
                errorList = ["Error on %s %s: ACCESS1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[ACCESS1] not in ['GEO','LUD','NON','OWN','PRC','STO']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

            # ACCESS2
                if 'ACCESS2' in f:
                    errorList = ["Error on %s %s: ACCESS2 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[ACCESS2] not in vnull
                                    if cursor[ACCESS2] not in ['GEO','LUD','NON','OWN','PRC','STO']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS2 must follow the correct coding scheme if populated."%len(errorList))

                    errorList = ["Error on %s %s: ACCESS1 must not be NON if ACCESS2 is not equal to NON."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[ACCESS2] in ['GEO','LUD','OWN','PRC','STO']
                                    if cursor[ACCESS1] == 'NON'] # Originally, if ACCESS2 != 'NON'. fixed in Jan 10, 2018
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS1 must not be NON if ACCESS2 is not equal to NON."%len(errorList))

                    errorList = ["Error on %s %s: ACCESS1 must not be the same as ACCESS2 unless both are NON."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[POLYTYPE] == 'FOR'
                                    if cursor[ACCESS1] in ['GEO','LUD','OWN','PRC','STO'] ## if ACCESS1 is populated with correct coding scheme except 'NON'.
                                    if cursor[ACCESS1] == cursor[ACCESS2]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS1 must not be the same as ACCESS2 unless both are NON."%len(errorList))


            # MGMTCON1
                errorList = ["Error on %s %s: MGMTCON1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[MGMTCON1] not in ['COLD','DAMG','ISLD','NATB','NONE','PENA','POOR','ROCK','SAND','SHRB','SOIL','STEP','UPFR','U_PF','WATR','WETT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

                try:
                    errorList = ["Error on %s %s: MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[POLYTYPE] == 'FOR'
                                    if cursor[ACCESS1] == 'GEO' or cursor[f.index('ACCESS2')] == 'GEO'
                                    if cursor[MGMTCON1] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%len(errorList))
                except:
                    # in the case where ACCESS2 field does not exist, the above try statement will fail
                    errorList = ["Error on %s %s: MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[POLYTYPE] == 'FOR'
                                    if cursor[ACCESS1] == 'GEO'
                                    if cursor[MGMTCON1] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%len(errorList))

                errorList = ["Warning on %s %s: MGMTCON1 should not equal 'NONE' when FORMOD = 'PF'."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[FORMOD] == 'PF'
                                if cursor[MGMTCON1] == 'NONE']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): MGMTCON1 should not equal 'NONE' when FORMOD = 'PF'."%len(errorList))

                errorList = ["Warning on %s %s: MGMTCON1 should not equal 'NONE' when SC = 4."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[SC] == 4
                                if cursor[MGMTCON1] == 'NONE']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): MGMTCON1 should not equal 'NONE' when SC = 4."%len(errorList))

            # MGMTCON2, MGMTCON3
                if "MGMTCON2" in f:
                    errorList = ["Error on %s %s: MGMTCON1 must not be 'NONE' if MGMTCON2 is not 'NONE'."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[POLYTYPE] == 'FOR'
                                    if cursor[f.index('MGMTCON2')] != 'NONE'
                                    if cursor[MGMTCON1] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not be 'NONE' if MGMTCON2 is not 'NONE'."%len(errorList))

                    errorList = ["Error on %s %s: MGMTCON2 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[POLYTYPE] == 'FOR'
                                    if cursor[f.index('MGMTCON2')] not in [None,'',' ','COLD','DAMG','ISLD','NATB','NONE','PENA','POOR','ROCK','SAND','SHRB','SOIL','STEP','UPFR','U_PF','WATR','WETT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON2 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%len(errorList))

                if "MGMTCON3" in f:
                    errorList = ["Error on %s %s: MGMTCON3 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[POLYTYPE] == 'FOR'
                                    if cursor[f.index('MGMTCON3')] not in [None,'',' ','COLD','DAMG','ISLD','NATB','NONE','PENA','POOR','ROCK','SAND','SHRB','SOIL','STEP','UPFR','U_PF','WATR','WETT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON3 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%len(errorList))

                if "MGMTCON2" and "MGMTCON3" in f:
                    errorList = ["Error on %s %s: MGMTCON1 and MGMTCON2 must not be 'NONE' if MGMTCON3 is not 'NONE'."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[POLYTYPE] == 'FOR'
                                    if cursor[f.index('MGMTCON3')] != 'NONE'
                                    if cursor[MGMTCON1] == 'NONE' or cursor[f.index('MGMTCON2')] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 and MGMTCON2 must not be 'NONE' if MGMTCON3 is not 'NONE'."%len(errorList))


            except (ValueError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1



# #########################           BMI          #############################

        if lyrAcro == "BMI":
            try:

            # Managed
                errorList = ["Error on %s %s: MANAGED must be either M or U when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[MANAGED] not in ['M','U']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MANAGED must be either M or U when POLYTYPE = FOR."%len(errorList))

            # PLANFU
                errorList = ["Error on %s %s: PLANFU must be populated when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[PLANFU] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PLANFU must be populated when POLYTYPE = FOR."%len(errorList))

            # AGESTR
                errorList = ["Error on %s %s: AGESTR must be either E or U when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[AGESTR] not in ['E','U']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AGESTR must be either E or U when POLYTYPE = FOR."%len(errorList))

                errorList = ["Warning on %s %s: AGESTR should be 'E' when SILVSYS is CC or SH, and 'U' when SILVSYS is SE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if (cursor[SILVSYS] in ['CC','SH'] and cursor[AGESTR] != 'E') or (cursor[SILVSYS] == 'SE' and cursor[AGESTR] != 'U')]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): AGESTR should be 'E' when SILVSYS is CC or SH, and 'U' when SILVSYS is SE."%len(errorList))

            # AGE
                errorList = ["Error on %s %s: AGE must be populated with a correct format when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[AGE] < 0 or cursor[AGE] > 999 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AGE must be populated a correct format when POLYTYPE = FOR."%len(errorList))

                errorList = ["Warning on %s %s: AGE should equal the plan period start year minus the YRORG (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[AGE] != fmpStartYear - cursor[YRORG]]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): AGE must be populated a correct format when POLYTYPE = FOR."%len(errorList))

            # AVAIL
                errorList = ["Error on %s %s: AVAIL must be either 'A' or 'U' when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[AVAIL] not in ['A','U'] ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AVAIL must be either 'A' or 'U' when POLYTYPE = FOR."%len(errorList))

                errorList = ["Warning on %s %s: AVAIL should be 'U' if FORMOD = PF or SC = 4 or MANAGED = U or ACCESS1 is not NON(when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[AVAIL] != 'U'
                                if cursor[FORMOD] == 'PF' or cursor[SC] == 4 or cursor[MANAGED] == 'U' or cursor[ACCESS1] != 'NON']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): AVAIL should be 'U' if FORMOD = PF or SC = 4 or MANAGED = U or ACCESS1 is not NON (when POLYTYPE = FOR)."%len(errorList))

            # SILVSYS
                errorList = ["Error on %s %s: SILVSYS must be populated with correct coding scheme when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[SILVSYS] not in ['CC','SE','SH'] ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be populated with correct coding scheme when POLYTYPE = FOR."%len(errorList))

            # NEXTSTG
                errorList = ["Error on %s %s: NEXTSTG must be populated with correct coding scheme when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[NEXTSTG] not in ['THINPRE','THINCOM','CONVENTN','BLKSTRIP','SEEDTREE','SCNDPASS','HARP','CLAAG','PREPCUT','SEEDCUT','FIRSTCUT','LASTCUT','IMPROVE','SELECT','SNGLTREE','GROUPSE'] ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be populated with correct coding scheme when POLYTYPE = FOR."%len(errorList))

                errorList = ["Error on %s %s: NEXTSTG cannot be IMPROVE or SELECT if AGESTR = 'E' (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR'
                                if cursor[NEXTSTG] in ['IMPROVE','SELECT']
                                if cursor[AGESTR] == 'E' ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): NEXTSTG cannot be IMPROVE or SELECT if AGESTR = 'E' (when POLYTYPE = FOR)."%len(errorList))

            # SI
                errorList = ["Error on %s %s: SI must be populated when POLYTYPE = FOR and AVAIL = A and SILVSYS = CC or SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR' and cursor[AVAIL] == 'A' and SILVSYS in ['CC','SH']
                                if cursor[SI] in vnull ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SI must be populated when POLYTYPE = FOR and AVAIL = A and SILVSYS = CC or SH."%len(errorList))

            # SISRC
                errorList = ["Error on %s %s: SISRC must be populated with correct coding scheme when POLYTYPE = FOR and AVAIL = A and SILVSYS = CC or SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[POLYTYPE] == 'FOR' and cursor[AVAIL] == 'A' and SILVSYS in ['CC','SH']
                                if cursor[SISRC] not in ['ACTUAL','ASSIGNED'] ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SISRC must be populated with correct coding scheme when POLYTYPE = FOR and AVAIL = A and SILVSYS = CC or SH."%len(errorList))


            except (ValueError, NameError) as e:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                arcpy.AddError("***Unable to run full validation on %s due to the following error:\n"%lyr + str(sys.exc_info()[1]))
                criticalError += 1




#    Still in the for loop: "for lyr in summarytbl.keys():"

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



if __name__ == "__main__":

    gdb = r'C:\DanielK_Workspace\FMP_LOCAL\Pic_Forest\FMP\2019\_data\FMP_Schema.gdb'
    #gdb = r'C:\DanielK_Workspace\FMP_LOCAL\Pic_Forest\FMP\2019\_data\test.gdb'

    year = 2019
    fmpStartYear = 2019

    summarytbl ={
    'MU966_19FDP00': ['FDP',
                   'Forecast Depletions',
                   'NAD 1983 UTM Zone 16N',
                   ['FSOURCE', 'FYRDEP', 'FDEVSTAGE'],
                   ['OBJECTID',
                    'SHAPE',
                    'MU966_19FDP00_',
                    'MU966_19FDP00_ID',
                    'SHAPE_LENGTH',
                    'SHAPE_AREA']],
    'MU966_19PCM01': ['PCM',
                   'Planning Composite',
                   'NAD 1983 UTM Zone 16N',
                   ['POLYID',
                    'POLYTYPE',
                    'OWNER',
                    'YRUPD',
                    'SOURCE',
                    'FORMOD',
                    'DEVSTAGE',
                    'YRDEP',
                    'SPCOMP',
                    'YRORG',
                    'HT',
                    'STKG',
                    'SC',
                    'ECOSRC',
                    'ECOSITE1',
                    'ECOPCT1',
                    'ACCESS1',
                    'MGMTCON1'],
                   ['OBJECTID',
                    #'SHAPE',
                    'MU966_19PCM00_',
                    'MU966_19PCM00_ID',
                    'FMFOBJID',
                    'GEOGNUM',
                    'AUTHORTY',
                    'WG',
                    'ECOSITE2',
                    'ECOPCT2',
                    'ACCESS2',
                    'MGMTCON2',
                    'MGMTCON3',
                    'AGS_POLE',
                    'AGS_SML',
                    'AGS_MED',
                    'AGS_LGE',
                    'UGS_POLE',
                    'UGS_SML',
                    'UGS_MED',
                    'UGS_LGE',
                    'USPCOMP',
                    'UWG',
                    'UYRORG',
                    'UHT',
                    'USTKG',
                    'USC',
                    'VERDATE',
                    'SENSITIV',
                    'MANAGED',
                    'TYPE',
                    'MNRCODE',
                    'SMZ',
                    'OMZ',
                    'PLANFU',
                    'AGESTR',
                    'AGE',
                    'AVAIL',
                    'SILVSYS',
                    'NEXTSTG',
                    'SI',
                    'SISRC',
                    'SGR',
                    'INCIDSPC',
                    'VERT',
                    'HORIZ',
                    'PRI_ECO',
                    'SEC_ECO',
                    'OCCLO',
                    'UCCLO',
                    'DEPTYPE',
                    'CUTCODE',
                    'PLANT_YR',
                    'FTG_YR',
                    'SARAHFLAG',
                    'HA',
                    'PW',
                    'PR',
                    'PJ',
                    'SB',
                    'SW',
                    'BF',
                    'CE',
                    'LA',
                    'PO',
                    'PB',
                    'BW',
                    'MH',
                    'AB',
                    'BE',
                    'PLANFU_NE',
                    'PLANFU_NW',
                    'WCODE',
                    'FMU_CODE',
                    'SHAPE_LENGTH',
                    'SHAPE_AREA']]}

    run(gdb, summarytbl, year, fmpStartYear)