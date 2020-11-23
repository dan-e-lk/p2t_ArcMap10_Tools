#-------------------------------------------------------------------------------
# Name:         TechSpec_FMP.py
# Purpose:      This module checkes every validation statements in FMP Tech Spec 2017
#
# Author:       RIAU, Ministry of Natural Resources and Forestry
#
#
# Created:      JUL 31 2017
# Updates:      MAR 28 2018 - DAN - The script now checks BMI, PCI and OPI
#               May 30 2018 - DAN - Now the script looks for FID if it cant find OBJECTID to accomodate shp and coverage
#               Any further updates can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog
#-------------------------------------------------------------------------------

import arcpy
import os, sys
import Reference as R
import pprint

verbose = True

lyrInfo = {
# Lyr acronym            name                           mandatory fields                                            Data type   Tech Spec       Tech Spec URL

    "AOC":  ["Area of Concern",                         ["AOCID","AOCTYPE"],                                        'polygon',  '4.2.8',        R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=108')],

    "BMI":  ["Base Model Inventory",                    ['POLYID', 'POLYTYPE', 'OWNER', 'YRSOURCE',
                                                       'SOURCE', 'FORMOD', 'DEVSTAGE', 'YRDEP', 'DEPTYPE',
                                                       'OYRORG', 'OSPCOMP', 'OLEADSPC', 'OAGE', 'OHT', 'OCCLO',
                                                       'OSTKG', 'OSC', 'UYRORG', 'USPCOMP', 'ULEADSPC', 'UAGE',
                                                       'UHT', 'UCCLO', 'USTKG', 'USC', 'INCIDSPC', 'VERT', 'HORIZ',
                                                       'PRI_ECO', 'SEC_ECO', 'ACCESS1', 'ACCESS2', 'MGMTCON1',
                                                       'MGMTCON2', 'MGMTCON3', 'YRORG', 'SPCOMP', 'LEADSPC',
                                                       'AGE', 'HT', 'CCLO', 'STKG', 'SC', 'MANAGED',
                                                       'PLANFU', 'AU', 'AVAIL', 'SILVSYS', 'NEXTSTG', 'YIELD'],     'polygon',  '4.1.4',        R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=11')], # Note that 'SMZ' is no longer mandatory

    "ERU":  ["Existing Road Use Management Strategies", ['ROADID','ROADCLAS','TRANS','ACYEAR','ACCESS','DECOM',
                                                        'INTENT','MAINTAIN','MONITOR','RESPONS','CONTROL1', 
                                                        'CONTROL2'],                                                'arc',      '4.2.12',       R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=125')], # CONTROL2 is added as a mandatory field in 2020.

    "FDP":  ["Forecast Depletions",                     ['FSOURCE','FYRDEP','FDEVSTAGE'],                           'polygon',  '4.1.8',        R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=91')],

    "IMP":  ["Tree Improvement",                        ['IMPROVE'],                                                'polygon',  '4.2.15',       R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=141')],

    "OPI":  ["Operational Planning Inventory",          ['POLYID', 'POLYTYPE', 'OWNER', 'YRSOURCE',
                                                       'SOURCE', 'FORMOD', 'DEVSTAGE', 'YRDEP', 'DEPTYPE',
                                                       'INCIDSPC', 'VERT', 'HORIZ',
                                                       'PRI_ECO', 'SEC_ECO', 'ACCESS1', 'ACCESS2', 'MGMTCON1',
                                                       'MGMTCON2', 'MGMTCON3', 'YRORG', 'SPCOMP', 'LEADSPC',
                                                       'AGE', 'HT', 'CCLO', 'STKG', 'SC', 'MANAGED', 
                                                       'PLANFU', 'AU', 'AVAIL', 'SILVSYS', 'NEXTSTG', 'YIELD',
                                                        'OMZ', 'SGR'],                                              'polygon',  '4.1.4',        R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=11')], # Note that 'SMZ' is no longer mandatory

    "ORB":  ["Operational Road Boundaries",             ['ORBID'],                                                  'polygon',  '4.2.11',       R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=122')],

    "PAG":  ["Planned Aggregate Extraction Areas",      ['AGAREAID'],                                               'polygon',  '4.2.14',       R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=139')],

    "PCI":  ["Planning Composite",                      ['POLYID', 'POLYTYPE', 'OWNER', 'YRSOURCE',
                                                        'SOURCE', 'FORMOD', 'DEVSTAGE', 'YRDEP', 'DEPTYPE',
                                                        'OYRORG', 'OSPCOMP', 'OLEADSPC', 'OAGE', 'OHT', 'OCCLO',
                                                        'OSTKG', 'OSC', 'UYRORG', 'USPCOMP', 'ULEADSPC', 'UAGE',
                                                        'UHT', 'UCCLO', 'USTKG', 'USC', 'INCIDSPC', 'VERT', 
                                                        'HORIZ', 'PRI_ECO', 'SEC_ECO', 'ACCESS1', 'MGMTCON1'],      'polygon',  '4.1.4',        R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=11')],

    "PHR":  ["Planned Harvest",                         ['BLOCKID','SILVSYS','HARVCAT'],                            'polygon',  '4.2.7',        R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=103')],

    "PRC":  ["Planned Road Corridors",                  ['ROADID','ROADCLAS','TRANS','ACYEAR','ACCESS','DECOM',
                                                        'INTENT', 'CONTROL1','CONTROL2'],                           'polygon',  '4.2.10',       R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=114')], # 'MAINTAIN' and 'MONITOR' removed *2020.11.006

    "PRP":  ["Planned Residual Patches",                ['RESID'],                                                  'polygon',  '4.2.9',        R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=112')],

    "WSY":  ["Wood Storage Yard",                       ['WSYID','TYPE'],                                           'polygon',  '4.2.16',       R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=143')], # this layer's been added in 2020

    "WXI":  ["Existing Road Water Crossing Inventory",  ['WATXID','WATXTYPE','RESPONS','ROADID'],                   'point',    '4.2.13',       R.findPDF('FIM_FMP_TechSpec_2020.pdf#page=135')],
        }


# vnull is used to check if an item is NULL or blank.
vnull = [None,'',' ']

def run(gdb, summarytbl, year, fmpStartYear, dataformat):  ## eg. summarytbl = {'MU110_17SAC10': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCTYPE', 'AOCID'], ['OBJECTID', 'MU110_17SAC10_', 'MU110_17SAC10_ID']], 'MU110_17SAC11':...}

    if verbose: print("%s\n%s\n%s\n%s"%(gdb, summarytbl, year, fmpStartYear))

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


        ##############################################################################
        #                                                                            #
        ########################  Checking PCI, OPI and BMI   ########################
        #                                                                            #
        ##############################################################################


        if lyrAcro in ["PCI","BMI","OPI"]:

            # POLYID
            try:
                current_field = 'POLYID' 
                                
                errorList = ["Error on %s %s: The population of POLYID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of POLYID is mandatory."%len(errorList))

                IDList = [str(cursor[f.index(current_field)]) for row in cursor if cursor[f.index(current_field)] not in vnull ]
                cursor.reset()

                summary_comments, errorList = R.findDuplicateID(IDList, current_field) #*24c02
                if len(summary_comments) > 0:
                    criticalError += 1
                    recordValCom[lyr].append(summary_comments)
                    errorDetail[lyr].append(errorList)

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # POLYTYPE
            try:
                current_field = 'POLYTYPE'
                errorList = ["Error on %s %s: The population of POLYTYPE is mandatory and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] not in ['WAT','DAL','GRS','ISL','UCL','BSH','RCK','TMS','OMS','FOR']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of POLYTYPE is mandatory and must follow the correct coding scheme."%len(errorList))

                ## The following statement can be checked on other fields: "If POLYTYPE attribute does not equal FOR, then FORMOD,DEVSTAGE, OYRORG, OSPCOMP..."

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # OWNER
            try:
                current_field = 'OWNER'            
                errorList = ["Error on %s %s: The population of OWNER is mandatory and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if str(cursor[f.index('OWNER')]) not in ['0','1','2','3','4','5','6','7','8','9']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of OWNER is mandatory and must follow the correct coding scheme."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # YRSOURCE
            try:
                current_field = 'YRSOURCE'                 
                errorList = ["Error on %s %s: The YRSOURCE must be populated with the correct format (YYYY)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('YRSOURCE')] in vnull or cursor[f.index('YRSOURCE')] < 1000 or cursor[f.index('YRSOURCE')] > 9999 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The YRSOURCE must be populated with the correct format (YYYY)."%len(errorList))

                errorList = ["Error on %s %s: The YRSOURCE must be at least a year less than the plan period start year."%(id_field, cursor[id_field_idx]) for row in cursor
                                if int(cursor[f.index('YRSOURCE')] or 0) > fmpStartYear - 1]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The YRSOURCE must be at least a year less than the plan period start year."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # SOURCE
            try:
                current_field = 'SOURCE'                
                errorList = ["Error on %s %s: The population of SOURCE must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('SOURCE')] not in ['BASECOVR','DIGITALA','DIGITALP','ESTIMATE','FOC','FORECAST','FRICNVRT','INFRARED','MARKING','OCULARA','OCULARG','OPC','PHOTO','PHOTOLS','PHOTOSS','PLOTFIXD','PLOTVAR','RADAR','REGENASS','SEMEXTEN','SEMINTEN','SPECTRAL','SUPINFO']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of SOURCE is mandatory and must follow the correct coding scheme."%len(errorList))

                if lyrAcro in ["PCI", "OPI"]:
                    errorList = ["Error on %s %s: SOURCE must not have the value FORECAST in PCI or OPI."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('SOURCE')] == 'FORECAST']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SOURCE must not have the value 'FORECAST' in PCI or OPI."%len(errorList))

                errorList = ["Error on %s %s: SOURCE must not equal ESTIMATE if the DEVSTAGE is NAT or starts with EST."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('DEVSTAGE')] not in vnull
                                if cursor[f.index('DEVSTAGE')][:3] == 'EST' or cursor[f.index('DEVSTAGE')] == 'NAT'
                                if cursor[f.index('SOURCE')] == 'ESTIMATE']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SOURCE must not equal ESTIMATE if the DEVSTAGE is NAT or starts with EST."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # FORMOD
            try:
                current_field = 'FORMOD'              
                errorList = ["Error on %s %s: FORMOD must be null when POLYTYPE is not equal to FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('FORMOD')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FORMOD must be null when POLYTYPE is not equal to FOR."%len(errorList))

                errorList = ["Error on %s %s: FORMOD must not be blank or null, and must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('FORMOD')] not in ['RP','MR','PF']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FORMOD must not be blank or null, and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

                if "SC" in f:
                    errorList = ["Warning on %s %s: FORMOD attribute should be PF when SC equals 4."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if str(cursor[f.index('SC')]) == '4'
                                    if cursor[f.index('FORMOD')] != 'PF']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1                     
                        recordValCom[lyr].append("Warning on %s record(s): FORMOD attribute should be PF when SC equals 4."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # DEVSTAGE
            try:
                current_field = 'DEVSTAGE'                
                errorList = ["Error on %s %s: DEVSTAGE must be null when POLYTYPE is not equal to FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('DEVSTAGE')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DEVSTAGE must be null when POLYTYPE is not equal to FOR."%len(errorList))

                errorList = ["Error on %s %s: The population of DEVSTAGE is mandatory and must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('DEVSTAGE')] not in ['DEPHARV', 'DEPNAT','LOWMGMT','LOWNAT','NEWPLANT','NEWSEED','NEWNAT','ESTPLANT','ESTSEED','ESTNAT','NAT','THINPRE','THINCOM','BLKSTRIP','SEEDTREE','FRSTPASS','PREPCUT','SEEDCUT','FIRSTCUT','LASTCUT','THINCOM','IMPROVE','SELECT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of DEVSTAGE is mandatory and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))


                optField = ['OSTKG','USTKG','STKG']
                matchingField = list(set(optField) & set(f))
                command = """errorList = ["Error on %s %s: DEVSTAGE attribute must be DEP* or NEW* if POLYTYPE = FOR and the stocking attributes equal 0.00 (OSTKG + USTKG + STKG = 0)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('DEVSTAGE')] not in ['DEPHARV','DEPNAT','NEWPLANT','NEWSEED','NEWNAT']
                                    if float(cursor[f.index('""" + matchingField[0] + """')] or 0)"""    # float(x or 0) will give 0.0 if x is None. *UD1: Added NEWPLANT, NEWSEED and NEWNAT on Dec 2017
                if len(matchingField) > 1:
                    for i in range(1,len(matchingField)):
                        command += """ + float(cursor[f.index('""" + matchingField[i] + """')] or 0)"""
                command += """ == 0]"""
                exec(command) ## executing the command built above...
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DEVSTAGE attribute must be DEP* or NEW* if POLYTYPE = FOR and the stocking attributes equal 0.00 (OSTKG + USTKG + STKG = 0)."%len(errorList))

                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Warning on %s %s: DEVSTAGE should be NEWPLANT, NEWSEED, NEWNAT, LOWMGMT, LOWNAT, DEPHARV or DEPNAT, if UCCLO + OCCLO < 25 (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if int(cursor[f.index('UCCLO')] or 0) + int(cursor[f.index('OCCLO')] or 0) < 25
                                    if cursor[f.index('DEVSTAGE')] not in ['LOWMGMT','LOWNAT','DEPHARV','DEPNAT','NEWPLANT','NEWSEED','NEWNAT']] # *23415
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1                      # minor error!!!!
                        recordValCom[lyr].append("Warning on %s record(s): DEVSTAGE should be LOWMGMT, LOWNAT, DEPHARV or DEPNAT if POLYTYPE = FOR and if UCCLO + OCCLO < 25."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # YRDEP
            try:
                current_field = 'YRDEP'               
                errorList = ["Error on %s %s: YRDEP must equal zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('YRDEP')] not in [0,None]] 
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): YRDEP must equal zero or null when POLYTYPE is not FOR."%len(errorList))

                errorList = ["Error on %s %s: YRDEP must be at least a year less than the plan start year."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('YRDEP')] > fmpStartYear - 1 ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): YRDEP must be at least a year less than the plan start year."%len(errorList))

                errorList = ["Warning on %s %s: YRDEP should be greater than or equal to 1900 where POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('YRDEP')] not in [None,0] and cursor[f.index('YRDEP')] < 1900] # *23404
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): YRDEP should be greater than or equal to 1900 where POLYTYPE = FOR."%len(errorList))

                errorList = ["Warning on %s %s: YRDEP should be greater than or equal to 1900 where DEPTYPE is not null."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('DEPTYPE')] not in vnull
                                if cursor[f.index('YRDEP')] < 1900]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): YRDEP should be greater than or equal to 1900 where DEPTYPE is not null (4.1.4 YRDEP)."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # DEPTYPE
            try:
                current_field = 'DEPTYPE'               
                errorList = ["Error on %s %s: DEPTYPE must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('DEPTYPE')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DEPTYPE must be null when POLYTYPE is not FOR."%len(errorList))

                errorList = ["Error on %s %s: DEPTYPE must follow the correct coding scheme where YRDEP is not 0."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('YRDEP')] not in [0] + vnull
                                if cursor[f.index('DEPTYPE')] not in ['BLOWDOWN','DISEASE','DROUGHT','FIRE','FLOOD','HARVEST','ICE','INSECTS','SNOW','UNKNOWN']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DEPTYPE must follow the correct coding scheme where YRDEP is not 0."%len(errorList))

                errorList = ["Warning on %s %s: DEPTYPE should not be UNKNOWN if DEVSTAGE starts with DEP, NEW or EST."%(id_field, cursor[id_field_idx]) for row in cursor
                                if str(cursor[f.index('DEVSTAGE')] or '')[:3] in ['DEP','NEW','EST']  # str(b or '') will give '' if b is None.
                                if cursor[f.index('DEPTYPE')] == 'UNKNOWN' ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): DEPTYPE should not be UNKNOWN if DEVSTAGE starts with DEP, NEW or EST."%len(errorList))

                ## The following has been included in YRDEP validation: If the disturbance type is not null (DEPTYPE ? null) then disturbance year should be greater than or equal nineteen hundred (YRDEP >= 1900)

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # OYRORG (PCI and BMI only)
            try:
                current_field = 'OYRORG'                 
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: OYRORG must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OYRORG')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OYRORG must be zero or null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: OYRORG must be greater than 1600 and less than the plan start year when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if not isinstance(cursor[f.index('OYRORG')],int) or cursor[f.index('OYRORG')] < 1600 or cursor[f.index('OYRORG')] > fmpStartYear - 1 ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OYRORG must be greater than 1600 and less than the plan start year when POLYTYPE is FOR."%len(errorList))

                    errorList = ["Warning on %s %s: OYRORG should not be greater than YRSOURCE when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OYRORG')] > cursor[f.index('YRSOURCE')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): OYRORG should not be greater than YRSOURCE when POLYTYPE is FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # OSPCOMP (PCI and BMI only)
            try:
                current_field = 'OSPCOMP'                
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: OSPCOMP must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OSPCOMP')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSPCOMP must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: OSPCOMP must be populated when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OSPCOMP')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSPCOMP must be populated when POLYTYPE is FOR."%len(errorList))

                    # code to check spcomp
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
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1  


            # OLEADSPC (PCI and BMI only)
            try:
                current_field = 'OLEADSPC'               
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: OLEADSPC must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OLEADSPC')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OLEADSPC must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: OLEADSPC must be populated when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OLEADSPC')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OLEADSPC must be populated when POLYTYPE = FOR."%len(errorList))

                    errorList = ["Error on %s %s: OLEADSPC must be a species listed in the OSPCOMP when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OLEADSPC')] not in vnull and cursor[f.index('OSPCOMP')] not in vnull
                                    if cursor[f.index('OLEADSPC')].upper() not in cursor[f.index('OSPCOMP')].upper()]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OLEADSPC must be a species listed in the OSPCOMP when POLYTYPE = FOR."%len(errorList))

                    # this check works even if the SPCOMP is not in descending order or if there are two or more species tied for greatest percent composition.
                    errorList = ["Error on %s %s: OLEADSPC must be the species with the greatest percent composition."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('OLEADSPC')] not in vnull
                                    if R.findLeadSpc(cursor[f.index('OSPCOMP')]) != None # if lead species can be found in the OSPCOMP - if lead spc cant be found, OSPCOMP value either is null or does not meet the tech spec.
                                    if cursor[f.index('OLEADSPC')].upper() in cursor[f.index('OSPCOMP')].upper()
                                    if cursor[f.index('OLEADSPC')].strip().upper() not in R.findLeadSpc(cursor[f.index('OSPCOMP')])]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OLEADSPC must be the species with the greatest percent composition."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1  

            # OAGE (PCI and BMI only)
            try:
                current_field = 'OAGE'              
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: OAGE must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OAGE')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OAGE must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: OAGE must be populated and follow the correct format when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if not isinstance(cursor[f.index('OAGE')],int) or cursor[f.index('OAGE')] < 0] ## testing if OAGE is always a positive integer or zero.
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OAGE must be populated and follow the correct format when POLYTYPE is FOR."%len(errorList))

                    errorList = ["Error on %s %s: OAGE - A zero or NULL value is not a valid code, unless DEVSTAGE is DEPHARV or DEPNAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('DEVSTAGE')] not in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('OAGE')] in [None, 0]] # *23412
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OAGE - A zero or NULL value is not a valid code, unless DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1  

            # OHT (PCI and BMI only)
            try:
                current_field = 'OHT'              
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: OHT must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OHT')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OHT must be zero when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: OHT must be populated and must be between 0 and 40 (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OHT')] == None or cursor[f.index('OHT')] < 0 or cursor[f.index('OHT')] > 40] # *23410
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OHT must be populated and must be between 0 and 40 (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Error on %s %s: OHT must be greater than zero if the DEVSTAGE does not start with DEP, NEW or LOW (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OHT')] <= 0 or cursor[f.index('OHT')] == None
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] not in ['DEP','NEW','LOW']] # *23413
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OHT must be greater than zero if the DEVSTAGE does not start with DEP, NEW or LOW (when POLYTYPE = FOR)."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1  


            # OCCLO (PCI and BMI only)
            try:
                current_field = 'OCCLO'            
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: OCCLO must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OCCLO')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OCCLO must be zero or null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: OCCLO must be populated and must be between 0 and 100 (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OCCLO')] == None or cursor[f.index('OCCLO')] < 0 or cursor[f.index('OCCLO')] > 100] # *23407
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OCCLO must be populated and must be between 0 and 100 (when POLYTYPE = FOR)."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1  

            # OSTKG (PCI and BMI only)
            try:
                current_field = 'OSTKG'            
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: OSTKG must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OSTKG')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSTKG must be zero or null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: OSTKG must be populated and must be between 0 and 4.0 (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OSTKG')] == None or cursor[f.index('OSTKG')] < 0 or cursor[f.index('OSTKG')] > 4] # *23410
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSTKG must be populated and must be between 0 and 4.0 (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Error on %s %s: OSTKG must be greater than zero if the DEVSTAGE does not start with DEP or NEW (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] not in ['DEP','NEW']
                                    if cursor[f.index('OSTKG')] == None or cursor[f.index('OSTKG')] <= 0] # *23413
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSTKG must be greater than zero if the DEVSTAGE does not start with DEP or NEW (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Warning on %s %s: OSTKG should be greater than 0.4 for certain DEVSTAGE values (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('DEVSTAGE')] in ['NAT','ESTNAT','ESTPLANT','ESTSEED','IMPROVE','SELECT','SNGLTREE','THINCOM','FIRSTCUT','SEEDCUT','PREPCUT','FIRSTPASS','BLKSTRIP','THINPRE']
                                    if cursor[f.index('OSTKG')] == None or cursor[f.index('OSTKG')] < 0.4] # *23413
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): OSTKG should be greater than 0.4 when DEVSTAGE is one of the following: NAT, ESTNAT, ESTPLANT, ESTSEED, IMPROVE, SELECT, SNGLTREE, THINCOM, FIRSTCUT, SEEDCUT, PREPCUT, FIRSTPASS, BLKSTRIP, THINPRE."%len(errorList))

                    errorList = ["Warning on %s %s: OSTKG and USTKG should be zero when DEVSTAGE starts with DEP."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] == 'DEP'
                                    if cursor[f.index('OSTKG')] not in [0, None] or cursor[f.index('USTKG')] not in [0, None]] # *23413
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): OSTKG and USTKG should be zero when DEVSTAGE starts with DEP."%len(errorList))

                    errorList = ["Warning on %s %s: OSTKG should be less than 2.5."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('OSTKG')] > 2.5]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): OSTKG should be less than 2.5."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1  

            # OSC (PCI and BMI only)
            try:
                current_field = 'OSC'            
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: OSC must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('OSC')] not in [0,None]] # *23405
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSC must be zero or null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: OSC must be between 0 and 4 when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('OSC')] not in [0,1,2,3,4]] # *23405
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OSC must be between 0 and 4 when POLYTYPE = FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1  

            # UYRORG (PCI and BMI only)
            try:
                current_field = 'UYRORG'
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: UYRORG must be zero or null when POLYTYPE is not FOR or if DEVSTAGE is DEPHARV or DEPNAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('UYRORG')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UYRORG must be zero or null when POLYTYPE is not FOR or if DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Warning on %s %s: UYRORG should be greater than OYRORG when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UYRORG')] <= cursor[f.index('OYRORG')] ] # *23414 *24b05
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1 #*24c05
                        recordValCom[lyr].append("Warning on %s record(s): UYRORG should be greater than OYRORG when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%len(errorList))

                    errorList = ["Error on %s %s: UYRORG must be greater than 1800 when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UYRORG')] == None or cursor[f.index('UYRORG')] < 1800 ] # *23414
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UYRORG must be greater than 1800 when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%len(errorList))

                    errorList = ["Error on %s %s: UYRORG must be less than the plan start year when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UYRORG')] >= fmpStartYear ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UYRORG must be less than the plan start year when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%len(errorList))

                    errorList = ["Warning on %s %s: UYRORG should not be greater than YRSOURCE when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UYRORG')] > cursor[f.index('YRSOURCE')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): UYRORG should not be greater than YRSOURCE when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1  

            # USPCOMP (PCI and BMI only)
            try:
                current_field = 'USPCOMP'            
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: USPCOMP must be null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('USPCOMP')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USPCOMP must be null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on %s %s: USPCOMP must be entered when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('USPCOMP')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USPCOMP must be entered when POLYTYPE is FOR and VERT is TO, TU, MO or MU."%len(errorList))

                    # code to check spcomp
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
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # ULEADSPC (PCI and BMI only)
            try:
                current_field = 'ULEADSPC'            
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: ULEADSPC must be null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('ULEADSPC')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ULEADSPC must be null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on %s %s: ULEADSPC must be populated when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('ULEADSPC')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ULEADSPC must be populated when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%len(errorList))

                    errorList = ["Error on %s %s: ULEADSPC must be a species listed in the USPCOMP."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('ULEADSPC')] not in vnull and cursor[f.index('USPCOMP')] != None
                                    if cursor[f.index('ULEADSPC')].upper() not in cursor[f.index('USPCOMP')].upper()]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ULEADSPC must be a species listed in the USPCOMP."%len(errorList))

                    # this check works even if the SPCOMP is not in descending order or if there are two or more species tied for greatest percent composition.
                    errorList = ["Error on %s %s: ULEADSPC must be the species with the greatest percent composition."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ULEADSPC')] not in vnull
                                    if R.findLeadSpc(cursor[f.index('USPCOMP')]) != None # if lead species can be found in the OSPCOMP - if lead spc cant be found, OSPCOMP value either is null or does not meet the tech spec.
                                    if cursor[f.index('ULEADSPC')].upper() in cursor[f.index('USPCOMP')].upper()
                                    if cursor[f.index('ULEADSPC')].strip().upper() not in R.findLeadSpc(cursor[f.index('USPCOMP')])]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ULEADSPC must be the species with the greatest percent composition."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # UAGE (PCI and BMI only)
            try:
                current_field = 'UAGE'            
                if lyrAcro in ["PCI", "BMI"]:

                    # the following has been removed in 2020.  id: *2020.11.003
                    # errorList = ["Error on %s %s: UAGE must be zero (or null) when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%(id_field, cursor[id_field_idx]) for row in cursor
                    #                 if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                    #                 if cursor[f.index('UAGE')] not in [0,None]]
                    # cursor.reset()
                    # if len(errorList) > 0:
                    #     errorDetail[lyr].append(errorList)
                    #     criticalError += 1
                    #     recordValCom[lyr].append("Error on %s record(s): UAGE must be zero (or null) when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    # Where the stand canopy has been determined to be two-tiered (VERT = TO, TU, MO, or MU), then an understorey age value must be entered (UAGE > 0)
                    errorList = ["Error on %s %s: UAGE must be greater than zero when VERT is TO, TU, MO or MU."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if int(cursor[f.index('UAGE')] or -1) <= 0] ## this will flag even if UAGE is ' ' or NULL.
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UAGE must be greater than zero when VERT is TO, TU, MO or MU."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # UHT (PCI and BMI only)
            try:
                current_field = 'UHT'              
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: UHT must be zero (or null) when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('UHT')] not in [0,None] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UHT must be zero (or null) when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on %s %s: UHT must be greater than 0 when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UHT')] <= 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UHT must be greater than 0 when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%len(errorList))

                    errorList = ["Error on %s %s: UHT must be between 0 and 40 when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('UHT')] == None or cursor[f.index('UHT')] < 0 or cursor[f.index('UHT')] > 40] # *23410
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UHT must be between 0 and 40 when POLYTYPE = FOR."%len(errorList))

                    errorList = ["Error on %s %s: OHT minus UHT must be >= 3 OR OAGE minus UAGE must be >= 20, when VERT is TO, TU, MO or MU."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UHT')] != 0 and cursor[f.index('UAGE')] != 0
                                    if isinstance(cursor[f.index('UHT')],(int,float)) and isinstance(cursor[f.index('OHT')],(int,float)) and isinstance(cursor[f.index('OAGE')],(int,float)) and isinstance(cursor[f.index('UAGE')],(int,float))
                                    if (cursor[f.index('UHT')] > cursor[f.index('OHT')] - 3) and (cursor[f.index('UAGE')] > cursor[f.index('OAGE')] - 20)]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): OHT minus UHT must be >= 3 OR OAGE minus UAGE must be >= 20, when VERT is TO, TU, MO or MU."%len(errorList))      # *UD2 update on Dec 2017
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # UCCLO (PCI and BMI only)
            try:
                current_field = 'UCCLO'              
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: UCCLO must be zero or null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('UCCLO')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UCCLO must be zero or null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on %s %s: UCCLO cannot be zero when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR' and cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('UCCLO')] == 0]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UCCLO cannot be zero when POLYTYPE = FOR and when VERT is TO, TU, MO or MU."%len(errorList))

                    errorList = ["Error on %s %s: UCCLO must be between 0 and 100 when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('UCCLO')] == None or cursor[f.index('UCCLO')] < 0 or cursor[f.index('UCCLO')] > 100] # 23410
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): UCCLO must be between 0 and 100 when POLYTYPE = FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # USTKG (PCI and BMI only)
            try:
                current_field = 'USTKG'             
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: USTKG must be zero or null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR' or cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('USTKG')] not in [0,None]] # SQL version: (POLYTYPE <> 'FOR' OR DEVSTAGE in('DEPHARV','DEPNAT')) AND (USTKG <> 0 OR USTKG is Null)
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USTKG must be zero or null when POLYTYPE is not FOR or when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on %s %s: USTKG must be between 0 and 4.0 (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('USTKG')] == None or cursor[f.index('USTKG')] < 0 or cursor[f.index('USTKG')] > 4] # *23410
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USTKG must be between 0 and 4.0 (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Warning on %s %s: USTKG should not be 0 when VERT is TO, TU, MO or MU (does not apply when DEVSTAGE is DEPHARV or DEPNAT)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('DEVSTAGE')] not in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('VERT')] in ['TO','TU','MO','MU']
                                    if cursor[f.index('USTKG')] <= 0] # *24b06
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): USTKG should not be 0 when VERT is TO, TU, MO or MU (does not apply when DEVSTAGE is DEPHARV or DEPNAT)."%len(errorList))

                    ## The following validation is being checked in the OSTKG section: "If DEVSTAGE attribute starts with DEP, then OSTKG + USTKG = 0"

                    errorList = ["Warning on %s %s: USTKG should be less than 2.5."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('USTKG')] > 2.5]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): USTKG should be less than 2.5."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # USC (PCI and BMI only)
            try:
                current_field = 'USC'            
                if lyrAcro in ["PCI", "BMI"]:
                    errorList = ["Error on %s %s: USC must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('USC')] not in [0,None]] # *23405
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USC must be zero or null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: USC must be zero when DEVSTAGE is DEPHARV or DEPNAT."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('DEVSTAGE')] in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('USC')] != 0] # *23405
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USC must be zero when DEVSTAGE is DEPHARV or DEPNAT."%len(errorList))

                    errorList = ["Error on %s %s: USC must be between 0 and 4 when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('USC')] not in [0,1,2,3,4]] # *23405
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): USC must be between 0 and 4 when POLYTYPE = FOR."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # INCIDSPC (applies to PCI BMI and OPI)
            try:
                current_field = 'INCIDSPC'            
                errorList = ["Error on %s %s: INCIDSPC must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('INCIDSPC')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INCIDSPC must be null when POLYTYPE is not FOR."%len(errorList))

                errorList = ["Error on %s %s: INCIDSPC must be populated when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('INCIDSPC')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INCIDSPC must be populated when POLYTYPE = FOR."%len(errorList))

                errorList = ["Error on %s %s: INCIDSPC must follow the correct species code (or NON) if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('INCIDSPC')] not in vnull
                                if cursor[f.index('INCIDSPC')].upper() != 'NON'
                                if cursor[f.index('INCIDSPC')].upper() not in R.SpcListInterp + R.SpcListOther ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INCIDSPC must follow the correct species code (or NON) if populated."%len(errorList))

                if lyrAcro == 'PCI':
                    errorList = ["Warning on %s %s: INCIDSPC should not represent over 10 percent in OSPCOMP (when VERT is not SV)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('INCIDSPC')] not in [None,'',' ','NON','Non'] and cursor[f.index('OSPCOMP')] != None  # if INCIDSPC is None, '' or ' ', then the next statement wouldn't work.
                                    if cursor[f.index('VERT')].upper() != 'SV'                                    
                                    if cursor[f.index('INCIDSPC')].upper() in cursor[f.index('OSPCOMP')].upper()
                                    if int(cursor[f.index('OSPCOMP')][cursor[f.index('OSPCOMP')].upper().find(cursor[f.index('INCIDSPC')].upper())+3:cursor[f.index('OSPCOMP')].upper().find(cursor[f.index('INCIDSPC')].upper())+6]) > 10] # int(sp[sp.find(incidspc)+3:sp.find(incidspc)+6])
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): INCIDSPC should not represent over 10 percent in OSPCOMP (when VERT is not SV)."%len(errorList))

                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Warning on %s %s: INCIDSPC should not represent over 10 percent in SPCOMP (when VERT is not SV)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('INCIDSPC')] not in [None,'',' ','NON','Non'] and cursor[f.index('SPCOMP')] != None
                                    if cursor[f.index('VERT')].upper() != 'SV'                                    
                                    if cursor[f.index('INCIDSPC')].upper() in cursor[f.index('SPCOMP')].upper()
                                    if int(cursor[f.index('SPCOMP')][cursor[f.index('SPCOMP')].upper().find(cursor[f.index('INCIDSPC')].upper())+3:cursor[f.index('SPCOMP')].upper().find(cursor[f.index('INCIDSPC')].upper())+6]) > 10]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): INCIDSPC should not represent over 10 percent in SPCOMP (when VERT is not SV)."%len(errorList))                                      
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # VERT
            try:
                current_field = 'VERT'            
                errorList = ["Error on %s %s: VERT must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('VERT')] not in ['SI','SV','TO','TU','MO','MU','CX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): VERT must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # HORIZ
            try:
                current_field = 'HORIZ'            
                errorList = ["Error on %s %s: HORIZ must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('HORIZ')] not in ['SS','SP','FP','MP','OC','OU']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HORIZ must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # PRI_ECO and SEC_ECO
            try:
                current_field = 'PRI_ECO and SEC_ECO'
                errorList = ["Error on %s %s: PRI_ECO must be populated when POLYTYPE is FOR or when SEC_ECO is not null."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR' or cursor[f.index('SEC_ECO')] not in vnull
                                if cursor[f.index('PRI_ECO')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PRI_ECO must be populated when POLYTYPE is FOR or when SEC_ECO is not null."%len(errorList))

                ## code to check PRI_ECO and SEC_ECO
                for fname in ["PRI_ECO", "SEC_ECO"]:
                    errorList = []
                    for row in cursor:
                        if cursor[f.index(fname)] not in vnull:
                            check = R.ecoVal(cursor[f.index(fname)],fname)
                            if check is None: ## when no error found
                                pass
                            else:
                                errorList.append("%s on %s %s: %s"%(check[0],id_field, cursor[id_field_idx],check[1]))

                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): %s value error. For more info, search for '%s' in the Error Detail section."%(len(errorList),fname,fname))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # ACCESS1
            try:
                current_field = 'ACCESS1'            
                errorList = ["Error on %s %s: ACCESS1 must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] != 'FOR'
                                if cursor[f.index('ACCESS1')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS1 must be null when POLYTYPE is not FOR."%len(errorList))


                errorList = ["Error on %s %s: ACCESS1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('ACCESS1')] not in ['GEO','LUD','NON','OWN','PRC','STO']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # ACCESS2
            try:
                current_field = 'ACCESS2'               
                if 'ACCESS2' in f:
                    errorList = ["Error on %s %s: ACCESS2 must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('ACCESS2')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS2 must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: ACCESS2 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS2')] not in vnull
                                    if cursor[f.index('ACCESS2')] not in ['GEO','LUD','NON','OWN','PRC','STO']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS2 must follow the correct coding scheme if populated."%len(errorList))

                    errorList = ["Error on %s %s: ACCESS1 must not be NON if ACCESS2 is not equal to NON (or blank)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS2')] not in vnull + ['NON']
                                    if cursor[f.index('ACCESS1')] == 'NON'] # *23401
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS1 must not be NON if ACCESS2 is not equal to NON (or blank)."%len(errorList))

                    errorList = ["Error on %s %s: ACCESS1 must not be the same as ACCESS2 unless both are NON."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('ACCESS1')] in ['GEO','LUD','OWN','PRC','STO'] ## if ACCESS1 is populated with correct coding scheme except 'NON'.
                                    if cursor[f.index('ACCESS1')] == cursor[f.index('ACCESS2')]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): ACCESS1 must not be the same as ACCESS2 unless both are NON."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # MGMTCON1
            try:
                current_field = 'MGMTCON1'            
                try:
                    errorList = ["Error on %s %s: MGMTCON1, MGMTCON2 and MGMTCON3 must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('MGMTCON1')] not in vnull or cursor[f.index('MGMTCON2')] not in vnull or cursor[f.index('MGMTCON3')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1, MGMTCON2 and MGMTCON3 must be null when POLYTYPE is not FOR."%len(errorList))
                except:
                    # in the case where MGMTCON2 or MGMTCON3 field does not exist, the above try statement will fail
                    try:
                        errorList = ["Error on %s %s: MGMTCON1 and MGMTCON2 must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[f.index('POLYTYPE')] != 'FOR'
                                        if cursor[f.index('MGMTCON1')] not in vnull or cursor[f.index('MGMTCON2')] not in vnull]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): MGMTCON1 and MGMTCON2 must be null when POLYTYPE is not FOR."%len(errorList))
                    except:
                        # in the case where MGMTCON2 field does not exist, the above try statement will fail
                        errorList = ["Error on %s %s: MGMTCON1 must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[f.index('POLYTYPE')] != 'FOR'
                                        if cursor[f.index('MGMTCON1')] not in vnull]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must be null when POLYTYPE is not FOR."%len(errorList))

                errorList = ["Error on %s %s: MGMTCON1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('POLYTYPE')] == 'FOR'
                                if cursor[f.index('MGMTCON1')] not in ['COLD','DAMG','ISLD','NATB','NONE','PENA','POOR','ROCK','SAND','SHRB','SOIL','STEP','UPFR','U_PF','WATR','WETT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must be populated and must follow the correct coding scheme when POLYTYPE is FOR."%len(errorList))

                try:
                    errorList = ["Error on %s %s: MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('ACCESS1')] == 'GEO' or cursor[f.index('ACCESS2')] == 'GEO'
                                    if cursor[f.index('MGMTCON1')] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%len(errorList))
                except:
                    # in the case where ACCESS2 field does not exist, the above try statement will fail
                    errorList = ["Error on %s %s: MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('ACCESS1')] == 'GEO'
                                    if cursor[f.index('MGMTCON1')] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not be 'NONE' if ACCESS1 or ACCESS2 is equal to 'GEO'."%len(errorList))

                errorList = ["Error on %s %s: MGMTCON1 must not equal 'NONE' when FORMOD = 'PF'."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('FORMOD')] == 'PF'
                                if cursor[f.index('MGMTCON1')] == 'NONE']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not equal 'NONE' when FORMOD = 'PF'."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # MGMTCON2, MGMTCON3
            try:
                current_field = 'MGMTCON2 and MGMTCON3'            
                if "MGMTCON2" in f:
                    errorList = ["Error on %s %s: MGMTCON1 must not be 'NONE' if MGMTCON2 has been populated with a value other than 'NONE'."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MGMTCON2')] not in vnull + ['NONE']
                                    if cursor[f.index('MGMTCON1')] == 'NONE'] # *23402
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not be 'NONE' if MGMTCON2 has been populated with a value other than 'NONE'."%len(errorList))

                    errorList = ["Error on %s %s: MGMTCON2 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MGMTCON2')] not in [None,'',' ','COLD','DAMG','ISLD','NATB','NONE','PENA','POOR','ROCK','SAND','SHRB','SOIL','STEP','UPFR','U_PF','WATR','WETT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON2 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%len(errorList))

                if "MGMTCON3" in f:
                    errorList = ["Error on %s %s: MGMTCON3 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MGMTCON3')] not in [None,'',' ','COLD','DAMG','ISLD','NATB','NONE','PENA','POOR','ROCK','SAND','SHRB','SOIL','STEP','UPFR','U_PF','WATR','WETT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON3 must follow the correct coding scheme (if populated) when POLYTYPE is FOR."%len(errorList))

                if "MGMTCON2" and "MGMTCON3" in f:
                    errorList = ["Error on %s %s: MGMTCON1 and MGMTCON2 must not be 'NONE' (or null) if MGMTCON3 is not 'NONE'."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MGMTCON3')] not in vnull + ['NONE']
                                    if cursor[f.index('MGMTCON1')] == 'NONE' or cursor[f.index('MGMTCON2')] in vnull + ['NONE']] # *23402
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 and MGMTCON2 must not be 'NONE' (or null) if MGMTCON3 is not 'NONE'."%len(errorList))

                try:
                    # using try and except here because most of the times, MGMTCON2 and 3 exists
                    errorList = ["Error on %s %s: MGMTCON1 must not have the same value as MGMTCON2 or MGMTCON3 unless they are all NONE."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MGMTCON1')] != 'NONE'
                                    if cursor[f.index('MGMTCON1')] == cursor[f.index('MGMTCON2')] or cursor[f.index('MGMTCON1')] == cursor[f.index('MGMTCON3')]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not have the same value as MGMTCON2 or MGMTCON3 unless they are all NONE."%len(errorList))
                except:
                    try:
                        errorList = ["Error on %s %s: MGMTCON1 must not have the same value as MGMTCON2 unless they are both NONE."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[f.index('POLYTYPE')] == 'FOR'
                                        if cursor[f.index('MGMTCON1')] != 'NONE'
                                        if cursor[f.index('MGMTCON1')] == cursor[f.index('MGMTCON2')]]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): MGMTCON1 must not have the same value as MGMTCON2 unless they are both NONE."%len(errorList))
                    except:
                        pass

                if 'SC' in f:
                    errorList = ["Warning on %s %s: MGMTCON1 should not equal 'NONE' when SC = 'PF'."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('SC')] == 'PF'
                                    if cursor[f.index('MGMTCON1')] == 'NONE']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): MGMTCON1 should not equal 'NONE' when SC = 'PF'."%len(errorList))

                if 'MGMTCON2' not in f and 'MGMTCON3' in f:
                   fieldValComUpdate[lyr].append("Missing MGMTCON2: If MGMTCON3 field exists, then MGMTCON2 field should also exist.")
                   fieldValUpdate[lyr] = 'Invalid'

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            ################################     BMI and OPI ONLY     ##################################

            # YRORG (BMI and OPI only)
            try:
                current_field = 'YRORG'             
                if lyrAcro in ["BMI","OPI"]:
                    errorList = ["Error on %s %s: YRORG must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('YRORG')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): YRORG must be zero or null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: YRORG must be greater than 1600 and less than the plan start year when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('YRORG')] == None or cursor[f.index('YRORG')] < 1600 or cursor[f.index('YRORG')] > fmpStartYear - 1 ] # *23413
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): YRORG must be greater than 1600 and less than the plan start year when POLYTYPE is FOR."%len(errorList))

                    errorList = ["Warning on %s %s: YRORG should not be greater than YRSOURCE when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('YRORG')] > cursor[f.index('YRSOURCE')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): YRORG should not be greater than YRSOURCE when POLYTYPE is FOR."%len(errorList))

                if lyrAcro in ["BMI"]:
                    errorList = ["Warning on %s %s: YRORG should be greater than or equal to OYRORG."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('YRORG')] < cursor[f.index('OYRORG')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): YRORG should be greater than or equal to OYRORG."%len(errorList))

                    errorList = ["Warning on %s %s: YRORG should be less than or equal to UYRORG if UYRORG is not 0."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('UYRORG')] not in [0, None]
                                    if cursor[f.index('YRORG')] > cursor[f.index('UYRORG')] ] # *23413
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): YRORG should be less than or equal to UYRORG if UYRORG is not 0."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # SPCOMP (BMI and OPI only)
            try:
                current_field = 'SPCOMP'            
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: SPCOMP must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('SPCOMP')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SPCOMP must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: SPCOMP must be populated when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('SPCOMP')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SPCOMP must be populated when POLYTYPE is FOR."%len(errorList))

                    # code to check spcomp
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
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # LEADSPC (BMI and OPI only)
            try:
                current_field = 'LEADSPC'              
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: LEADSPC must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('LEADSPC')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): LEADSPC must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: LEADSPC must be populated when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('LEADSPC')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): LEADSPC must be populated when POLYTYPE = FOR."%len(errorList))

                    errorList = ["Error on %s %s: LEADSPC must be species listed in the SPCOMP when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('LEADSPC')] not in vnull and cursor[f.index('SPCOMP')] not in vnull
                                    if cursor[f.index('LEADSPC')].upper() not in cursor[f.index('SPCOMP')].upper()]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): LEADSPC must be species listed in the SPCOMP when POLYTYPE = FOR."%len(errorList))

                    # this check works even if the SPCOMP is not in descending order or if there are two or more species tied for greatest percent composition.
                    errorList = ["Error on %s %s: LEADSPC must be the species with the greatest percent composition."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('LEADSPC')] not in vnull
                                    if R.findLeadSpc(cursor[f.index('SPCOMP')]) != None # if lead species can be found in the OSPCOMP - if lead spc cant be found, OSPCOMP value either is null or does not meet the tech spec.
                                    if cursor[f.index('LEADSPC')].upper() in cursor[f.index('SPCOMP')].upper()
                                    if cursor[f.index('LEADSPC')].strip().upper() not in R.findLeadSpc(cursor[f.index('SPCOMP')])]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): LEADSPC must be the species with the greatest percent composition."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # AGE (BMI and OPI only)
            try:
                current_field = 'LEADSPC'              
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: AGE must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('AGE')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AGE must be zero or null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: AGE must be populated and follow the correct format when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if not isinstance(cursor[f.index('AGE')],int) or cursor[f.index('AGE')] < 0] ## testing if AGE is always a positive integer or zero.
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AGE must be populated and follow the correct format when POLYTYPE is FOR."%len(errorList))

                    errorList = ["Error on %s %s: AGE - A zero or NULL value is not a valid code, unless DEVSTAGE is DEPHARV or DEPNAT (when POLYTYPE is FOR)."%(id_field, cursor[id_field_idx]) for row in cursor # *23412
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('DEVSTAGE')] not in ['DEPHARV','DEPNAT']
                                    if cursor[f.index('AGE')] in [None, 0]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AGE - A zero or NULL value is not a valid code, unless DEVSTAGE is DEPHARV or DEPNAT (when POLYTYPE is FOR)."%len(errorList)) # *23412

                    errorList = ["Error on %s %s: AGE must be equal to the plan start year minus the YRORG."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('AGE')] > 0 and cursor[f.index('YRORG')] > 0
                                    if fmpStartYear - cursor[f.index('YRORG')] != cursor[f.index('AGE')] ]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AGE must be equal to the plan start year minus the YRORG."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # HT (BMI and OPI only)
            try:
                current_field = 'HT'            
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: HT must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('HT')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): HT must be zero or null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: HT must be populated and must be between 0 and 40 (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('HT')] == None or cursor[f.index('HT')] < 0 or cursor[f.index('HT')] > 40] # *23410
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): HT must be populated and must be between 0 and 40 (when POLYTYPE = FOR)."%len(errorList))

                    errorList = ["Error on %s %s: HT must be greater than zero if the DEVSTAGE does not start with DEP, NEW or LOW (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('HT')] == None or cursor[f.index('HT')] <= 0
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] not in ['DEP','NEW','LOW']] # *23413
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): HT must be greater than zero if the DEVSTAGE does not start with DEP, NEW or LOW (when POLYTYPE = FOR)."%len(errorList))

                    # only applied to BMI
                    if lyrAcro == 'BMI':
                        errorList = ["Warning on %s %s: HT should be greater than or equal to UHT and less than or equal to OHT."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[f.index('POLYTYPE')] == 'FOR'
                                        if cursor[f.index('HT')] >= 0 and cursor[f.index('OHT')] >= 0 and cursor[f.index('UHT')] >= 0
                                        if cursor[f.index('HT')] < cursor[f.index('UHT')] or cursor[f.index('HT')] > cursor[f.index('OHT')] ]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            minorError += 1
                            recordValCom[lyr].append("Warning on %s record(s): HT should be greater than or equal to UHT and less than or equal to OHT."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # CCLO (BMI and OPI only)
            try:
                current_field = 'CCLO'            
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: CCLO must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('CCLO')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CCLO must be zero or null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: CCLO must be populated and must be between 0 and 100 (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('CCLO')] == None or cursor[f.index('CCLO')] < 0 or cursor[f.index('CCLO')] > 100] # *23410
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CCLO must be populated and must be between 0 and 100 (when POLYTYPE = FOR)."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # STKG (BMI and OPI only)
            try:
                current_field = 'STKG'             
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: STKG must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('STKG')] not in [0,None]]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): STKG must be zero or null when POLYTYPE is not FOR."%len(errorList))


                    errorList = ["Error on %s %s: STKG must be populated and must be between 0 and 4.0 (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('STKG')] == None or cursor[f.index('STKG')] < 0 or cursor[f.index('STKG')] > 4] # *23410
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): STKG must be populated and must be between 0 and 4.0 (when POLYTYPE = FOR)."%len(errorList))


                    errorList = ["Error on %s %s: STKG must be greater than zero if the DEVSTAGE starts with NAT or EST (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('STKG')] == None or cursor[f.index('STKG')] <= 0
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] in ['NAT','EST']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): STKG must be greater than zero if the DEVSTAGE starts with NAT or EST (when POLYTYPE = FOR)."%len(errorList))


                    errorList = ["Warning on %s %s: STKG should be greater than 0.4 if DEVSTAGE is NAT or starts with EST (when POLYTYPE = FOR)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('STKG')] < 0.4
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] in ['NAT','EST']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): STKG should be greater than 0.4 if DEVSTAGE is NAT or starts with EST (when POLYTYPE = FOR)."%len(errorList))


                    errorList = ["Warning on %s %s: STKG should be zero or null when DEVSTAGE starts with DEP."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('DEVSTAGE')] not in vnull
                                    if cursor[f.index('DEVSTAGE')][:3] == 'DEP'
                                    if cursor[f.index('STKG')] not in [0, None]] # *23413
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): STKG should be zero or null when DEVSTAGE starts with DEP."%len(errorList))


                    errorList = ["Warning on %s %s: STKG should be less than 2.5."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('STKG')] > 2.5]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): STKG should be less than 2.5."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # SC (BMI and OPI only)
            try:
                current_field = 'SC'            
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: SC must be zero or null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('SC')] not in [0,None]] # *23405
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SC must be zero or null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: SC must be between 0 and 4 when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('SC')] not in [0,1,2,3,4]] # *23405
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SC must be between 0 and 4 when POLYTYPE = FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # MANAGED (BMI and OPI only)
            try:
                current_field = 'MANAGED'            
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: MANAGED must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('MANAGED')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MANAGED must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: MANAGED must be M or U when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MANAGED')] not in ['M','U']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MANAGED must be M or U when POLYTYPE = FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # SMZ (BMI and OPI only)  SMZ is no longer a mandatory field in 2020
            # try:
            #     current_field = 'SMZ'            
            #     if lyrAcro in ["BMI", "OPI"]:
            #         errorList = ["Error on %s %s: SMZ must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
            #                         if cursor[f.index('SMZ')] in vnull]
            #         cursor.reset()
            #         if len(errorList) > 0:
            #             errorDetail[lyr].append(errorList)
            #             criticalError += 1
            #             recordValCom[lyr].append("Error on %s record(s): SMZ must be populated."%len(errorList))
            # except ValueError:
            #     recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
            #     arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
            #     criticalError += 1

            # PLANFU (BMI and OPI only)
            try:
                current_field = 'PLANFU'         
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: PLANFU must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('PLANFU')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PLANFU must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: PLANFU must be populated when POLYTYPE = FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('PLANFU')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): PLANFU must be populated when POLYTYPE = FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # AU (BMI and OPI only)
            try:
                current_field = 'AU'             
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: AU must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('AU')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AU must be null when POLYTYPE is not FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # AVAIL (BMI and OPI only)
            try:
                current_field = 'AVAIL'             
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: AVAIL must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('AVAIL')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AVAIL must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: AVAIL must be A or U when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('AVAIL')] not in ['A','U']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AVAIL must be A or U when POLYTYPE is FOR."%len(errorList))

                    errorList = ["Error on %s %s: AVAIL must be U when MANAGED = U."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('MANAGED')] == 'U'
                                    if cursor[f.index('AVAIL')] != 'U']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): AVAIL must be U when MANAGED = U."%len(errorList))

                    errorList = ["Warning on %s %s: AVAIL should be U when FORMOD = PF and OWNER = 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if str(cursor[f.index('OWNER')]) == '1'
                                    if cursor[f.index('FORMOD')] == 'PF'
                                    if cursor[f.index('AVAIL')] != 'U']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): AVAIL should be U when FORMOD = PF and OWNER = 1."%len(errorList))

                    errorList = ["Warning on %s %s: AVAIL should be U when SC = 4 and OWNER = 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if str(cursor[f.index('OWNER')]) == '1'
                                    if str(cursor[f.index('SC')]) == '4'
                                    if cursor[f.index('AVAIL')] != 'U']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): AVAIL should be U when SC = 4 and OWNER = 1."%len(errorList))

                    errorList = ["Warning on %s %s: AVAIL should be U when ACCESS1 is GEO, LUD, OWN, PRC or STO."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if str(cursor[f.index('OWNER')]) == '1'
                                    if cursor[f.index('ACCESS1')] in ['GEO','LUD','OWN','PRC','STO']
                                    if cursor[f.index('AVAIL')] != 'U']
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): AVAIL should be U when ACCESS1 is GEO, LUD, OWN, PRC or STO."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # SILVSYS (BMI and OPI only)
            try:
                current_field = 'SILVSYS'            
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: SILVSYS must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('SILVSYS')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SILVSYS must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: SILVSYS must be CC, SE or SH when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('SILVSYS')] not in ['CC','SE','SH']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SILVSYS must be CC, SE or SH when POLYTYPE is FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # NEXTSTG (BMI and OPI only)
            try:
                current_field = 'NEXTSTG'            
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: NEXTSTG must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('NEXTSTG')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): NEXTSTG must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: NEXTSTG must follow the coding scheme when POLYTYPE is FOR and AVAIL = A."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('AVAIL')] == 'A'
                                    if cursor[f.index('NEXTSTG')] not in ['THINPRE','THINCOM','CONVENT','BLKSTRIP','SEEDTREE','SCNDPASS','PREPCUT','SEEDCUT','FIRSTCUT','LASTCUT','IMPROVE','SELECT']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): NEXTSTG must follow the coding scheme when POLYTYPE is FOR and AVAIL = A."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # YIELD (BMI and OPI only)
            try:
                current_field = 'YIELD'            
                if lyrAcro in ["BMI", "OPI"]:
                    errorList = ["Error on %s %s: YIELD must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('YIELD')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): YIELD must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: YIELD must be populated when POLYTYPE is FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('YIELD')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): YIELD must be populated when POLYTYPE is FOR."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            ################################     OPI ONLY     ##################################

            # OMZ (OPI only)
                # There's nothing to validate.

            # SGR (OPI only)
            try:
                current_field = 'YIELD'            
                if lyrAcro == "OPI":
                    errorList = ["Error on %s %s: SGR must be null when POLYTYPE is not FOR."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] != 'FOR'
                                    if cursor[f.index('SGR')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SGR must be null when POLYTYPE is not FOR."%len(errorList))

                    errorList = ["Error on %s %s: SGR must not be null when POLYTYPE is FOR, AVAIL = A, and AGE >= 30."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('POLYTYPE')] == 'FOR'
                                    if cursor[f.index('AVAIL')] == 'A' 
                                    if int(cursor[f.index('AGE')] or 0) >= 30 # because a blank string is greater than any number in python world.
                                    if cursor[f.index('SGR')] in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): SGR must not be null when POLYTYPE is FOR, AVAIL = A, and AGE >= 30."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

        
                # that's all for the inventory data (BMI, PCI and OPI)!!!!!
        #############################################################################
        #############################################################################
        #############################################################################
        #############################################################################


        ########################         Checking FDP        ########################

        if lyrAcro == "FDP":

            # FSOURCE
            try:
                current_field = 'FSOURCE'              
                errorList = ["Error on %s %s: FSOURCE must be populated and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('FSOURCE')] not in ['FORECAST','BASECOVR','DIGITALA','DIGITALP','ESTIMATE','FOC','FRICNVRT','INFRARED','MARKING','OCULARA','OCULARG','OPC','PHOTO','PHOTOLS','PHOTOSS','PLOTFIXD','PLOTVAR','RADAR','REGENASS','SEMEXTEN','SEMINTEN','SPECTRAL','SUPINFO']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FSOURCE must be populated and must follow the correct coding scheme."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # FYRDEP
            try:
                current_field = 'FYRDEP'            
                errorList = ["Error on %s %s: FYRDEP must be populated and zero is not a valid code."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('FYRDEP')] in [0, None, '',' ']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FYRDEP must be populated and zero is not a valid code."%len(errorList))

                errorList = ["Warning on %s %s: FYRDEP should not be less than plan start year minus 4."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('FYRDEP')] not in [0, None, '',' ']
                                if cursor[f.index('FYRDEP')] < fmpStartYear - 4]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): FYRDEP should not be less than plan start year minus 4."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # FDEVSTAGE
            try:
                current_field = 'FDEVSTAGE'            
                errorList = ["Error on %s %s: FDEVSTAGE must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('FDEVSTAGE')] not in ['DEPHARV', 'DEPNAT','LOWMGMT','LOWNAT','NEWPLANT','NEWSEED','NEWNAT','ESTPLANT','ESTSEED','ESTNAT','NAT','THINPRE','THINCOM','BLKSTRIP','SEEDTREE','FRSTPASS','PREPCUT','SEEDCUT','FIRSTCUT','LASTCUT','THINCOM','IMPROVE','SELECT']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): FDEVSTAGE must be populated with the correct coding scheme."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


        ########################         Checking AOC        ########################

        if lyrAcro == "AOC":

            # AOCID
            try:
                current_field = 'AOCID'            
                errorList = ["Error on %s %s: AOCID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AOCID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AOCID must be populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # AOCTYPE
            try:
                current_field = 'AOCTYPE'             
                errorList = ["Error on %s %s: AOCTYPE must be populated with M or R."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AOCTYPE')] not in ['M','R']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AOCTYPE must be populated with M or R."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


        ########################         Checking ERU        ########################

        if lyrAcro == "ERU":

            # ROADID
            try:
                current_field = 'ROADID'            
                errorList = ["Error on %s %s: ROADID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADID must be populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # ROADCLAS
            try:
                current_field = 'ROADCLAS'            
                errorList = ["Error on %s %s: ROADCLAS must be populated with P, B or O."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ROADCLAS')] not in ['P','B','O']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADCLAS must be populated with P, B or O."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # TRANS
            try:
                current_field = 'TRANS'            
                errorList = ["Error on %s %s: TRANS, if populated, must be greater than or equal to the plan start year."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('TRANS')] not in [0, None, '', ' ']
                                if cursor[f.index('TRANS')] < fmpStartYear]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRANS, if populated, must be greater than or equal to the plan start year."%len(errorList))

                # The following is a validation for INTENT: "If TRANS value does not equal zero (TRANS is not 0) then INTENT must be populated"

                errorList = ["Warning on %s %s: TRANS, if populated, should not be greater than plan start year plus 20."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('TRANS')] not in vnull
                                if cursor[f.index('TRANS')] > fmpStartYear + 20]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): TRANS, if populated, should not be greater than plan start year plus 20."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # ACYEAR
            try:
                current_field = 'ACYEAR'            
                errorList = ["Error on %s %s: ACYEAR, if populated, must be greater than or equal to the plan start year when ACCESS is not EXISTING or REMOVE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ACYEAR')] not in [0, None, '', ' ']
                                if cursor[f.index('ACCESS')] not in ['EXISTING','REMOVE']
                                if cursor[f.index('ACYEAR')] < fmpStartYear]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACYEAR, if populated, must be greater than or equal to the plan start year when ACCESS is not EXISTING or REMOVE."%len(errorList))

                # Below is checking ACCESS...
                errorList = ["Error on %s %s: ACCESS must not be null if ACYEAR is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ACYEAR')] not in [0, None, '', ' ']
                                if cursor[f.index('ACCESS')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must not be null if ACYEAR is populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # ACCESS
            try:
                current_field = 'ACCESS'            
                errorList = ["Error on %s %s: ACCESS must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ACCESS')] not in vnull + ['APPLY','REMOVE','ADD','EXISTING','BOTH','ADDREMOVE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must follow the correct coding scheme if populated."%len(errorList))

                # this is checking CONTROL1
                errorList = ["Error on %s %s: CONTROL1 must not be null if ACCESS = APPLY, ADD, BOTH OR ADDREMOVE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ACCESS')] in ['APPLY','ADD','BOTH','ADDREMOVE']
                                if cursor[f.index('CONTROL1')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 must not be null if ACCESS = APPLY, ADD, BOTH OR ADDREMOVE."%len(errorList))

                # this is checking CONTROL1
                errorList = ["Warning on %s %s: CONTROL1 should be null if ACCESS = REMOVE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ACCESS')] == 'REMOVE'
                                if cursor[f.index('CONTROL1')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): CONTROL1 should be null if ACCESS = REMOVE."%len(errorList))

                # this is checking CONTROL2
                if "CONTROL2" in f:
                    errorList = ["Warning on %s %s: CONTROL2 should be null if ACCESS = REMOVE."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS')] == 'REMOVE'
                                    if cursor[f.index('CONTROL2')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): CONTROL2 should be null if ACCESS = REMOVE."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # DECOM, MAINTAIN, MONITOR, ACCESS
            try:
                current_field = 'DECOM, MAINTAIN, MONITOR and ACCESS'            
                errorList = ["Error on %s %s: At least one of DECOM, MAINTAIN, MONITOR or ACCESS must occur."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('DECOM')] in vnull
                                if cursor[f.index('MAINTAIN')] != 'Y'
                                if cursor[f.index('MONITOR')] != 'Y'
                                if cursor[f.index('ACCESS')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): At least one of DECOM, MAINTAIN, MONITOR or ACCESS must occur."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # DECOM
            try:
                current_field = 'DECOM'            
                errorList = ["Error on %s %s: DECOM must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('DECOM')] not in vnull + ['BERM','SCAR','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DECOM must follow the correct coding scheme if populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # INTENT
            try:
                current_field = 'INTENT'            
                errorList = ["Error on %s %s: INTENT must be populated if TRANS is not 0."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('TRANS')] not in [0,None]
                                if cursor[f.index('INTENT')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INTENT must be populated if TRANS is not 0."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # MAINTAIN
            try:
                current_field = 'MAINTAIN'            
                errorList = ["Error on %s %s: MAINTAIN must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('MAINTAIN')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MAINTAIN must be populated with Y or N."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # MONITOR
            try:
                current_field = 'MONITOR'   
                errorList = ["Error on %s %s: MONITOR must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('MONITOR')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): MONITOR must be populated with Y or N."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # RESPONS
            try:
                current_field = 'RESPONS'            
                errorList = ["Error on %s %s: RESPONS must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('RESPONS')] not in ['SFL','MNR','OTH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): RESPONS must be populated with the correct coding scheme."%len(errorList))

                respons_sfl_list = ["" for row in cursor if cursor[f.index('RESPONS')] == "SFL"]
                cursor.reset()
                if len(respons_sfl_list) == 0:
                    minorError += 1
                    recordValCom[lyr].append("Warning: At least one record should have RESPONS = SFL (except for Crown managed units).")                
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # CONTROL1 and 2
            try:
                current_field = 'CONTROL1 and CONTROL2'            
                errorList = ["Error on %s %s: CONTROL1 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('CONTROL1')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 must follow the correct coding scheme if populated."%len(errorList))

                errorList = ["Error on %s %s: CONTROL2 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('CONTROL2')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL2 must follow the correct coding scheme if populated."%len(errorList))

                # the following has been added in 2020.  id:*2020.11.001
                # The population of CONTROL1 or CONTROL2 is mandatory where ACCESS != REMOVE or ACCESS is not null
                errorList = ["Error on %s %s: Population of CONTROL1 or CONTROL2 is mandatory where ACCESS is not REMOVE or ACCESS is not null."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('CONTROL1')] in vnull and cursor[f.index('CONTROL2')] in vnull
                                if cursor[f.index('ACCESS')] not in vnull + ["REMOVE"] ]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): Population of CONTROL1 or CONTROL2 is mandatory where ACCESS is not REMOVE or ACCESS is not null."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


        ########################         Checking ORB        ########################

        if lyrAcro == "ORB":

            # ORBID
            try:
                current_field = 'ORBID'            
                errorList = ["Error on %s %s: ORBID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ORBID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ORBID must be populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


        ########################         Checking IMP        ########################

        if lyrAcro == "IMP":
            # IMPROVE
            try:
                current_field = 'IMPROVE'            
                errorList = ["Error on %s %s: IMPROVE must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('IMPROVE')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): IMPROVE must be populated with Y or N."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


        ########################         Checking PAG        ########################

        if lyrAcro == "PAG":
            # AGAREAID
            try:
                current_field = 'AGAREAID'             
                errorList = ["Error on %s %s: AGAREAID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AGAREAID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AGAREAID must be populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1



        ########################         Checking PHR        ########################

        if lyrAcro == "PHR":
            # BLOCKID
            try:
                current_field = 'BLOCKID'            
                errorList = ["Error on %s %s: BLOCKID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('BLOCKID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): BLOCKID must be populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # SILVSYS
            try:
                current_field = 'SILVSYS'            
                errorList = ["Error on %s %s: SILVSYS must be populated with CC, SE or SH."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('SILVSYS')] not in ['CC','SE','SH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be populated with CC, SE or SH."%len(errorList))

                errorList = ["Error on %s %s: SILVSYS must be CC if HARVCAT = SCNDPASS."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('HARVCAT')] == 'SCNDPASS'
                                if cursor[f.index('SILVSYS')] != 'CC']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be CC if HARVCAT = SCNDPASS."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # HARVCAT
            try:
                current_field = 'HARVCAT'            
                errorList = ["Error on %s %s: HARVCAT must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('HARVCAT')] not in ['BRIDGING','CONTNGNT','REGULAR','SALVAGE','REDIRECT','ACCELER','SCNDPASS']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVCAT must be populated with the correct coding scheme."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


        ########################         Checking PRC        ########################

        if lyrAcro == "PRC":
            # ROADID
            try:
                current_field = 'ROADID'            
                errorList = ["Error on %s %s: ROADID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADID must be populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # ROADCLAS
            try:
                current_field = 'ROADCLAS'            
                errorList = ["Error on %s %s: ROADCLAS must be populated with P or B."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ROADCLAS')] not in ['P','B']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADCLAS must be populated with P or B."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # TRANS
            try:
                current_field = 'TRANS'            
                errorList = ["Error on %s %s: TRANS, if populated, must be greater than or equal to the plan start year."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('TRANS')] not in [0, None, '', ' ']
                                if cursor[f.index('TRANS')] < fmpStartYear]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRANS, if populated, must be greater than or equal to the plan start year."%len(errorList))

                # The following is a validation for INTENT: "If TRANS value does not equal zero (TRANS is not 0) then INTENT must be populated"

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # ACYEAR
            try:
                current_field = 'ACYEAR'            
                errorList = ["Error on %s %s: ACYEAR, if populated, must be between plan start year and plan end year."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ACYEAR')] not in [0, None, '', ' ']
                                if cursor[f.index('ACYEAR')] < fmpStartYear or cursor[f.index('ACYEAR')] > fmpStartYear + 10]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACYEAR, if populated, must be between plan start year and plan end year."%len(errorList))

                # Below is checking ACCESS...
                errorList = ["Error on %s %s: ACCESS must be APPLY, REMOVE or BOTH if ACYEAR is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ACYEAR')] not in [0, None, '', ' ']
                                if cursor[f.index('ACCESS')] not in ['APPLY','REMOVE','BOTH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must be APPLY, REMOVE or BOTH if ACYEAR is populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


            # ACCESS
            try:
                current_field = 'ACCESS'            
                errorList = ["Error on %s %s: ACCESS must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ACCESS')] not in vnull + ['APPLY','REMOVE','BOTH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must follow the correct coding scheme if populated."%len(errorList))

                # this is checking CONTROL1
                errorList = ["Warning on %s %s: CONTROL1 should be null if ACCESS = REMOVE."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ACCESS')] == 'REMOVE'
                                if cursor[f.index('CONTROL1')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): CONTROL1 should be null if ACCESS = REMOVE."%len(errorList))

                # this is checking CONTROL2
                if "CONTROL2" in f:
                    errorList = ["Warning on %s %s: CONTROL2 should be null if ACCESS = REMOVE."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS')] == 'REMOVE'
                                    if cursor[f.index('CONTROL2')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        minorError += 1
                        recordValCom[lyr].append("Warning on %s record(s): CONTROL2 should be null if ACCESS = REMOVE."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # The following validation has been removed in 2020.  *2020.11.006
            # # DECOM, MAINTAIN, MONITOR, ACCESS
            # try:
            #     current_field = 'DECOM, MAINTAIN, MONITOR and ACCESS'            
            #     errorList = ["Error on %s %s: At least one of DECOM, MAINTAIN, MONITOR or ACCESS must occur."%(id_field, cursor[id_field_idx]) for row in cursor
            #                     if cursor[f.index('DECOM')] in vnull
            #                     if cursor[f.index('MAINTAIN')] != 'Y'
            #                     if cursor[f.index('MONITOR')] != 'Y'
            #                     if cursor[f.index('ACCESS')] in vnull]
            #     cursor.reset()
            #     if len(errorList) > 0:
            #         errorDetail[lyr].append(errorList)
            #         criticalError += 1
            #         recordValCom[lyr].append("Error on %s record(s): At least one of DECOM, MAINTAIN, MONITOR or ACCESS must occur."%len(errorList))

            #     # Not checking the following validation statement because CONSTRCT field does not exist:
            #     #   At a minimum, one of Construction, Decommissioning, Maintenance, Monitoring or Access Control must occur for each record (CONSTRCT = Y or DECOM IS NOT NULL or MAINTAIN = Y or MONITOR = Y or [ACCESS = APPLY or ACCESS = REMOVE OR ACCESS = BOTH])

            # except ValueError:
            #     recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
            #     arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
            #     criticalError += 1


            # DECOM
            try:
                current_field = 'DECOM'             
                errorList = ["Error on %s %s: DECOM must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('DECOM')] not in vnull + ['BERM','SCAR','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DECOM must follow the correct coding scheme if populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # INTENT
            try:
                current_field = 'INTENT'            
                errorList = ["Error on %s %s: INTENT must be populated if TRANS is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('TRANS')] not in [0, None]
                                if cursor[f.index('INTENT')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INTENT must be populated if TRANS is populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # MAINTAIN and MONITOR are no longer mandatory fields in 2020.  *2020.11.006
            # # MAINTAIN
            # try:
            #     current_field = 'MAINTAIN'            
            #     errorList = ["Error on %s %s: MAINTAIN must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
            #                     if cursor[f.index('MAINTAIN')] not in ['Y','N']]
            #     cursor.reset()
            #     if len(errorList) > 0:
            #         errorDetail[lyr].append(errorList)
            #         criticalError += 1
            #         recordValCom[lyr].append("Error on %s record(s): MAINTAIN must be populated with Y or N."%len(errorList))
            # except ValueError:
            #     recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
            #     arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
            #     criticalError += 1

            # # MONITOR
            # try:
            #     current_field = 'MONITOR'            
            #     errorList = ["Error on %s %s: MONITOR must be populated with Y or N."%(id_field, cursor[id_field_idx]) for row in cursor
            #                     if cursor[f.index('MONITOR')] not in ['Y','N']]
            #     cursor.reset()
            #     if len(errorList) > 0:
            #         errorDetail[lyr].append(errorList)
            #         criticalError += 1
            #         recordValCom[lyr].append("Error on %s record(s): MONITOR must be populated with Y or N."%len(errorList))
            # except ValueError:
            #     recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
            #     arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
            #     criticalError += 1            

            # CONTROL1 and 2
            try:
                current_field = 'CONTROL1 and CONTROL2'            
                errorList = ["Error on %s %s: CONTROL1 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('CONTROL1')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 must follow the correct coding scheme if populated."%len(errorList))

                if "CONTROL2" in f:
                    errorList = ["Error on %s %s: CONTROL2 must follow the correct coding scheme if populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('CONTROL2')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL2 must follow the correct coding scheme if populated."%len(errorList))

                if "CONTROL2" not in f:
                    errorList = ["Error on %s %s: CONTROL1 must be populated with the correct coding scheme where ACCESS = BOTH or APPLY."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS')] in ['BOTH','APPLY']
                                    if cursor[f.index('CONTROL1')] not in ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL1 must be populated with the correct coding scheme where ACCESS = BOTH or APPLY."%len(errorList))

                if "CONTROL2" in f:
                    errorList = ["Error on %s %s: CONTROL1 or CONTROL2 must be populated with the correct coding scheme where ACCESS = BOTH or APPLY."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS')] in ['BOTH','APPLY']
                                    if cursor[f.index('CONTROL1')] not in ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX'] and cursor[f.index('CONTROL2')] not in ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL1 or CONTROL2 must be populated with the correct coding scheme where ACCESS = BOTH or APPLY."%len(errorList))


            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1 


        ########################         Checking PRP        ########################

        if lyrAcro == "PRP":

            # RESID
            try:
                current_field = 'RESID'             
                errorList = ["Error on %s %s: RESID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('RESID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): RESID must be populated."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1


        ########################         Checking WSY        ########################

        if lyrAcro == "WSY":

            # WSYID
            try:
                current_field = 'WSYID'            
                errorList = ["Error on %s %s: WSYID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('WSYID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): WSYID must be populated."%len(errorList))

            # TYPE **2020.08.002
                current_field = 'TYPE'            
                errorList = ["Error on %s %s: TYPE must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('TYPE')] not in ['THY','TMY','LMY']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TYPE must be populated with the correct coding scheme."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1



        ########################         Checking WXI        ########################

        if lyrAcro == "WXI":

            # WATXID
            try:
                current_field = 'WATXID'            
                errorList = ["Error on %s %s: WATXID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('WATXID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): WATXID must be populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # WATXTYPE
            try:
                current_field = 'WATXTYPE'            
                errorList = ["Error on %s %s: WATXTYPE must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('WATXTYPE')] not in ['BRID','TEMP','CULV','MULTI','FORD','ICE','BOX','ARCH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): WATXTYPE must be populated with the correct coding scheme."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # RESPONS
            try:
                current_field = 'RESPONS'            
                # errorList = ["Error on %s %s: RESPONS must be populated with the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                #                 if cursor[f.index('RESPONS')] not in ['SFL','MNR','OTH']]
                # cursor.reset()
                # if len(errorList) > 0:
                #     errorDetail[lyr].append(errorList)
                #     criticalError += 1
                #     recordValCom[lyr].append("Error on %s record(s): RESPONS must be populated with the correct coding scheme."%len(errorList))

                errorList = ["Error on %s %s: RESPONS must be populated (blank or null is not a valid code)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('RESPONS')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): RESPONS must be populated (blank or null is not a valid code)."%len(errorList))

                respons_sfl_list = ["" for row in cursor if cursor[f.index('RESPONS')] == "SFL"]
                cursor.reset()
                if len(respons_sfl_list) == 0:
                    minorError += 1
                    recordValCom[lyr].append("Warning: At least one record should have RESPONS = SFL (except for Crown managed units).")       
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
                criticalError += 1

            # ROADID
            try:
                current_field = 'RESPONS'            
                errorList = ["Error on %s %s: ROADID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADID must be populated."%len(errorList))
            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s field due to value error - most likely due to missing mandatory field(s)"%current_field)
                arcpy.AddWarning("***Unable to run full validation on %s field due to the following error:\n"%current_field + str(sys.exc_info()[1]))
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
            arcpy.AddMessage('') # just to add a new line.

    return [errorDetail, recordVal, recordValCom, fieldValUpdate, fieldValComUpdate]

