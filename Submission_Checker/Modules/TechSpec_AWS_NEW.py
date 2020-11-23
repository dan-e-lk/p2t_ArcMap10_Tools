#-------------------------------------------------------------------------------
# Name:         TechSpec_AWS_NEW.py
# Purpose:      This module checkes every validation statements under AWS Tech Spec 2017
#
# Author:       RIAU, Ministry of Natural Resources and Forestry
#
# Notes:        To find the validation code, run Search (Ctrl+F) for validation header such as "4.2.19")
#               Some 2017 updates are prefixed with v2017
# Created:      2017 12 21
# Last Modified:2017 12 29
# 
#           Any further updates can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog
#-------------------------------------------------------------------------------
import arcpy
import os, sys
import Reference as R
import pprint

verbose = True
vnull = [None,'',' '] # vnull is used to check if an item is NULL or blank.


# \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\InDevelopment\Submission_Checker\Modules\PDF\FIM_AWS_TechSpec_2017.pdf

# This Dictionary will be used to check mandatory fields, layer acronyms and missing layers.
lyrInfo = {
# Dictionary of lists of lists
# Layer acronym            name                           mandatory fields                                              Data Type   Tech Spec  Tech Spec URL
    "AGP":  ["Existing Forestry Aggregate Pits",        ['PITID', 'PITOPEN', 'PITCLOSE', 'CAT9APP'],                    'point',    '4.2.19',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=71')   ],# v2017 used to have PIT_ID, PIT_OPEN
    "SAC":  ["Scheduled Area Of Concern",               ['AOCID', 'AOCTYPE'],                                           'polygon',  '4.2.8',        R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=21')   ],# v2017
    "SAG":  ["Scheduled Aggregate Extraction",          ['AWS_YR', 'AGAREAID'],                                         'polygon',  '4.2.14',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=52')   ],# v2017
    "SEA":  ["Scheduled Establishment Assessment",      ['AWS_YR', 'YRDEP', 'TARGETFU', 'TARGETYD'],                    'polygon',  '4.2.20',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=75')   ],# v2017 this is a new layer in 2017 spec
    "SHR":  ["Scheduled Harvest",                       ['AWS_YR', 'BLOCKID', 'SILVSYS', 'HARVCAT','FUELWOOD'],         'polygon',  '4.2.7',        R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=15')   ],# v2017 Addition of BLOCKID
    "SOR":  ["Scheduled Operational Road Boundaries",   ['AWS_YR', 'ORBID'],                                            'polygon',  '4.2.11',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=34')   ],# v2017
    "SPT":  ["Scheduled Protection Treatment",          ['AWS_YR', 'TRTMTHD1'],                                         'polygon',  '4.2.18',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=67')   ],# v2017
    "SRA":  ["Scheduled Existing Road Activities",      ['AWS_YR', 'ROADID', 'ROADCLAS','TRANS','ACCESS',
                                                         'DECOM','CONTROL1'],                                           'arc',      '4.2.12',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=37')   ],# v2017 TRANS, ACCESS, CONTROL1 and DECOM are now mandatory
    "SRC":  ["Scheduled Road Corridors",                ['AWS_YR', 'ROADID', 'ROADCLAS','TRANS','ACYEAR',
                                                         'ACCESS','DECOM','INTENT','CONTROL1'],                         'polygon',  '4.2.10',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=24')   ],# v2020 Maintain and Monitor attributes are not mandatory
    "SRG":  ["Scheduled Regeneration Treatments",       ['AWS_YR', 'TRTMTHD1'],                                         'polygon',  '4.2.16',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=59')   ],# v2017
    "SRP":  ["Scheduled Residual Patches",              ['RESID'],                                                      'polygon',  '4.2.9',        R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=22')   ],# v2017 AWS_YR is not required
    "SSP":  ["Scheduled Site Preparation Treatments",   ['AWS_YR', 'TRTMTHD1'],                                         'polygon',  '4.2.15',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=55')   ],# v2017
    "STT":  ["Scheduled Tending Treatments",            ['AWS_YR', 'TRTMTHD1'],                                         'polygon',  '4.2.17',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=63')   ],# v2017
    "SWC":  ["Scheduled Water Crossing Activities",     ['AWS_YR', 'WATXID', 'WATXTYPE','TRANS','ROADID'],              'point',    '4.2.13',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=45')   ],# V2017 TRANS is mandatory
    "WSY":  ["Scheduled Wood Storage Yards",            ['AWS_YR', 'WSYID', 'TYPE'],                                    'polygon',  '4.2.13',       R.findPDF('FIM_AWS_TechSpec_2020.pdf#page=79')   ]# this layer was added in 2020   
    }


def run(gdb, summarytbl, year, fmpStartYear, dataformat):  ## eg. summarytbl = {'MU110_17SAC10': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCTYPE', 'AOCID'], ['OBJECTID', 'MU110_17SAC10_', 'MU110_17SAC10_ID']], 'MU110_17SAC11':...}
    lyrList = summarytbl.keys()
    fieldValUpdate = dict(zip(lyrList,['' for i in lyrList]))  ## if we find a record-value-based mandatory field, field validation status should be updated.
    fieldValComUpdate = dict(zip(lyrList,[[] for i in lyrList])) ## if we find a record-value-based mandatory field, field validation comments should be updated.
    recordVal = dict(zip(lyrList,['' for i in lyrList]))  ## recordVal should be either Valid or Invalid for each layer.
    recordValCom = dict(zip(lyrList,[[] for i in lyrList]))  ## recordValCom should be in the form, "1 record(s) where AWS_YR = 2016".
    errorDetail = dict(zip(lyrList,[[] for i in lyrList])) ## this will be used to populate "Error Detail" section of the report. (dictionary of list of list)

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


        ##################### Checking all the AWS_YR fields ###################
        #ref-AWS_YR
        if lyrAcro in ['SAG','SEA','SHR','SOR','SPT','SRA','SRC','SRG','SSP','STT','SWC','WSY']:
            try:
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1. *AWS_YR = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('AWS_YR')]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%len(errorList))

                # This has been removed in 2020. id: *2020.11.005
                # specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                # cursor.reset()
                # if len(specialList) == 0:
                #     minorError += 1
                #     recordValCom[lyr].append("Warning on AWS_YR attributes: At least one feature should be populated with the current AWS year (%s)."%year)

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing AWS_YR field"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ######### Going through each layer type in alphabetical order ##########


        ###########################  Checking AGP   ############################

        if lyrAcro == "AGP":
            try: # need try and except block here for instances such as not having mandatory fields.
            # PITID
                errorList = ["Error on %s %s: PITID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('PITID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PITID must be populated."%len(errorList))

            # PITOPEN
                errorList = ["Error on %s %s: PITOPEN must be populated with the correct coding scheme. *PITOPEN = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('PITOPEN')]) for row in cursor
                                if R.fimdate(cursor[f.index('PITOPEN')]) is None]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PITOPEN must be populated with the correct coding scheme."%len(errorList))

            # PITCLOSE
                errorList = ["Error on %s %s: PITCLOSE must be Y or N if populated. *PITCLOSE = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('PITCLOSE')]) for row in cursor
                                if cursor[f.index('PITCLOSE')] not in vnull + ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PITCLOSE must be Y or N if populated."%len(errorList))

                errorList = ["Error on %s %s: PITCLOSE must be N if CAT9APP is not NULL. *PITCLOSE = [%s]  *CAT9APP = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('PITCLOSE')],cursor[f.index('CAT9APP')]) for row in cursor
                                if  cursor[f.index('CAT9APP')] not in vnull
                                and cursor[f.index('PITCLOSE')] != 'N']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PITCLOSE must be N if CAT9APP is not NULL."%len(errorList))

            # CAT9APP
                errorList = ["Error on %s %s: CAT9APP must be either NULL or follow the correct coding scheme. *CAT9APP = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('CAT9APP')]) for row in cursor
                                if cursor[f.index('CAT9APP')] not in vnull
                                and R.fimdate(cursor[f.index('CAT9APP')]) is None]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CAT9APP must be either NULL or follow the correct coding scheme."%len(errorList))

                # The following statement has been removed in 2020.  *2020.10.015
                # errorList = ["Error on %s %s: CAT9APP date cannot be greater than 10 years from PITOPEN date.  *CAT9APP = [%s] *PITOPEN = [%s]"
                #                 %(id_field, cursor[id_field_idx],cursor[f.index('CAT9APP')],cursor[f.index('PITOPEN')]) for row in cursor
                #                 if R.fimdate(cursor[f.index('CAT9APP')]) is not None
                #                 and R.fimdate(cursor[f.index('PITOPEN')]) is not None
                #                 and R.fimdate(cursor[f.index('CAT9APP')]) > (R.fimdate(str(int(cursor[f.index('PITOPEN')][:4]) + 10) +  cursor[f.index('PITOPEN')][4:]))]
                # cursor.reset()
                # if len(errorList) > 0:
                #     errorDetail[lyr].append(errorList)
                #     criticalError += 1
                #     recordValCom[lyr].append("Error on %s record(s): The CAT9APP date cannot be greater than 10 years from PITOPEN date."%len(errorList))

                errorList = ["Error on %s %s: CAT9APP must be NULL if PITCLOSE is Y.  *PITCLOSE = [%s]  *CAT9APP = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('PITCLOSE')],cursor[f.index('CAT9APP')]) for row in cursor
                                if cursor[f.index('PITCLOSE')] == 'Y'
                                and cursor[f.index('CAT9APP')] not in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CAT9APP must be NULL if PITCLOSE is Y."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking SAC   ############################

        if lyrAcro == "SAC":
            try:
            # AOCID
                errorList = ["Error on %s %s: AOCID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AOCID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AOCID must be populated."%len(errorList))

            # AOCTYPE
                errorList = ["Error on %s %s: AOCTYPE must be populated with the correct coding scheme. *AOCTYPE = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('AOCTYPE')]) for row in cursor
                                if cursor[f.index('AOCTYPE')] not in ['M','R']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AOCTYPE must be populated with the correct coding scheme."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking SAG   ############################

        if lyrAcro == "SAG":
            pass
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # AGAREAID
                # No validation needed: blank or null is a valid code


        ###########################  Checking SEA   ############################

        if lyrAcro == "SEA":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # YRDEP
                errorList = ["Error on %s %s: YRDEP must be populated with the correct format and zero or null is not a valid value.  *YRDEP = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('YRDEP')]) for row in cursor
                                if int(cursor[f.index('YRDEP')] or 0) < 1000 or cursor[f.index('YRDEP')] > year] # year of last disturbance shouldn't be a future year.
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): YRDEP must be populated with the correct format and zero or null is not a valid value."%len(errorList))

            # TARGETFU
                errorList = ["Error on %s %s: TARGETFU must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('TARGETFU')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TARGETFU must be populated."%len(errorList))

            # TARGETYD
                errorList = ["Error on %s %s: TARGETYD must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('TARGETYD')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TARGETYD must be populated."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking SHR   ############################

        if lyrAcro == "SHR":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once 
                # To find this code block, search this script for #ref-AWS_YR

            # BLOCKID
                errorList = ["Error on %s %s: The population of BLOCKID is mandatory where plan start year is greater than or equal to 2019."
                                %(id_field, cursor[id_field_idx]) for row in cursor
                                if fmpStartYear >= 2019 and cursor[f.index('BLOCKID')] in vnull] #*24c03
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of BLOCKID is mandatory where plan start year is greater than or equal to 2019."%len(errorList))            

            # SILVSYS
                errorList = ["Error on %s %s: SILVSYS must follow the correct coding scheme if populated.  *SILVSYS = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('SILVSYS')]) for row in cursor
                                if cursor[f.index('SILVSYS')] not in vnull + ['CC','SE','SH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must follow the correct coding scheme if populated."%len(errorList))

                ## If the FUELWOOD attribute is Y then the SILVSYS and HARVCAT attributes can be null
                errorList = ["Error on %s %s: SILVSYS must be populated if FUELWOOD is not Y.  *SILVSYS = [%s] *FUELWOOD = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('SILVSYS')],cursor[f.index('FUELWOOD')]) for row in cursor
                                if cursor[f.index('FUELWOOD')] != 'Y' and cursor[f.index('SILVSYS')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be populated if FUELWOOD is not Y."%len(errorList))

                ## If the harvest category is second pass, then the silvicultural system must be clearcut.
                errorList = ["Error on %s %s: SILVSYS must be CC when HARVCAT = SCNDPASS.  *SILVSYS = [%s] *HARVCAT = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('SILVSYS')],cursor[f.index('HARVCAT')]) for row in cursor
                                if cursor[f.index('HARVCAT')] == 'SCNDPASS' and cursor[f.index('SILVSYS')] != 'CC']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): SILVSYS must be CC when HARVCAT = SCNDPASS."%len(errorList))                    

            # HARVCAT
                errorList = ["Error on %s %s: HARVCAT must follow the correct coding scheme if populated.  *HARVCAT = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('HARVCAT')]) for row in cursor
                                if cursor[f.index('HARVCAT')] not in vnull + ['REGULAR','BRIDGING','CONTNGNT','REDIRECT','ACCELER','FRSTPASS','SCNDPASS','SALVAGE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVCAT must follow the correct coding scheme if populated."%len(errorList))


                errorList = ["Error on %s %s: The population of HARVCAT is mandatory except when FUELWOOD = Y.  *HARVCAT = [%s] *FUELWOOD = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('HARVCAT')],cursor[f.index('FUELWOOD')]) for row in cursor
                                if cursor[f.index('HARVCAT')] in vnull and cursor[f.index('FUELWOOD')] != 'Y']
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of HARVCAT is mandatory except when FUELWOOD = Y."%len(errorList))

                # The following validation has been removed in 2020.  *2020.10.012
                # errorList = ["Error on %s %s: HARVCAT = BRIDGING is only available when the AWS start year is equal to the first year of the plan period."
                #                 %(id_field, cursor[id_field_idx]) for row in cursor
                #                 if cursor[f.index('HARVCAT')] == 'BRIDGING'
                #                 if year != fmpStartYear and cursor[f.index('AWS_YR')] == year] # *24c06
                # cursor.reset()
                # if len(errorList) > 0:
                #     errorDetail[lyr].append(errorList)
                #     criticalError += 1
                #     recordValCom[lyr].append("Error on %s record(s): HARVCAT = BRIDGING is only available when the AWS start year is equal to the first year of the plan period."%len(errorList))

            # FUELWOOD
                errorList = ["Error on %s %s: The population of FUELWOOD is mandatory and must follow the correct coding scheme where AWS_YR = submission year.  *FUELWOOD = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('FUELWOOD')]) for row in cursor
                                if cursor[f.index('AWS_YR')] == year
                                if cursor[f.index('FUELWOOD')] not in ['Y','N']] # *24c08
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of FUELWOOD is mandatory and must follow the correct coding scheme."%len(errorList))


            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking SOR   ############################

        if lyrAcro == "SOR":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # ORBID
                errorList = ["Error on %s %s: ORBID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ORBID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ORBID must be populated."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking SPT   ############################

        if lyrAcro == "SPT":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # TRTMTHD1, 2 and 3
                # For TRTMTHD1, 2 or 3, the population of one of these attributes is mandatory where AWS_YR equals the fiscal year to which the AWS applies
                # The attribute population must follow the correct coding scheme
                codingScheme = " ['PCHEMA','PCHEMG','PMANUAL'] " # simply change this line for other treatment layer validations!!
                t2check1 = ''
                t3check1 = ''
                t2check2 = ''
                t3check2 = ''
                if 'TRTMTHD2' in f:
                    t2check1 = " and cursor[f.index('TRTMTHD2')] not in " + codingScheme
                    t2check2 = " or cursor[f.index('TRTMTHD2')] not in " + codingScheme + " + vnull "
                if 'TRTMTHD3' in f:
                    t3check1 = " and cursor[f.index('TRTMTHD3')] not in " + codingScheme
                    t3check2 = " or cursor[f.index('TRTMTHD3')] not in " + codingScheme + " + vnull "                    

                command = """errorList = ["Error on %s %s: The population of TRTMTHD1, 2 or 3 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."
                                %(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] == year
                                if cursor[f.index('TRTMTHD1')] not in """ + codingScheme + t2check1 + t3check1 + "or (cursor[f.index('TRTMTHD1')] not in " + codingScheme + " + vnull " + t2check2 + t3check2 + ")]"     
                                # The first half of the last line checkes if at least one of the 3 fields have been populated with the coding scheme
                                # The second half of the last line checks if all 3 fields have correct coding scheme if populated
                exec(command)

                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of TRTMTHD1, 2 or 3 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%len(errorList))


            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking SRA   ############################

        if lyrAcro == "SRA":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # ROADID
                errorList = ["Error on %s %s: ROADID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADID must be populated."%len(errorList))

            # ROADCLAS
                errorList = ["Error on %s %s: ROADCLAS must be populated with the correct coding scheme. *ROADCLAS = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('ROADCLAS')]) for row in cursor
                                if cursor[f.index('ROADCLAS')] not in ['P','B','O']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADCLAS must be populated with the correct coding scheme."%len(errorList))

            # TRANS
                errorList = ["Error on %s %s: TRANS must be populated with the correct coding scheme.  *TRANS = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('TRANS')]) for row in cursor
                                if cursor[f.index('TRANS')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRANS must be populated with the correct coding scheme."%len(errorList))

            # ACCESS        # big change in v2017 spec
                errorList = ["Error on %s %s: ACCESS must follow the correct coding scheme if populated.  *ACCESS = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('ACCESS')]) for row in cursor
                                if cursor[f.index('ACCESS')] not in vnull + ['APPLY','REMOVE','ADD','EXISTING','BOTH','ADDREMOVE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must follow the correct coding scheme if populated."%len(errorList))

            # DECOM         # big change in v2017 spec
                if 'DECOM' in f:
                    errorList = ["Error on %s %s: DECOM must follow the correct coding scheme if populated.  *DECOM = [%s]"
                                    %(id_field, cursor[id_field_idx],cursor[f.index('DECOM')]) for row in cursor
                                    if cursor[f.index('DECOM')] not in vnull + ['BERM','SCAR','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): DECOM must follow the correct coding scheme if populated."%len(errorList))

            # MAINTAIN
                if 'MAINTAIN' in f:
                    errorList = ["Error on %s %s: MAINTAIN must be populated with the correct coding scheme (Y or N)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('MAINTAIN')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MAINTAIN must be populated with the correct coding scheme (Y or N)."%len(errorList))

            # MONITOR
                if 'MONITOR' in f:
                    errorList = ["Error on %s %s: MONITOR must be populated with the correct coding scheme (Y or N)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('MONITOR')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MONITOR must be populated with the correct coding scheme (Y or N)."%len(errorList))


            # Checking "At a minimum, one of Decommissioning, Maintenance, Monitoring, Access Control, or Transfer must occur for each record (DECOM = Y or MAINTAIN = Y or MONITOR = Y or ACCESS = Y or TRANS = Y) where AWS_YR equals the fiscal year to which the AWS applies."
                optField = ['MAINTAIN','MONITOR']
                matchingField = list(set(optField) & set(f))
                command = """errorList = ["Error on %s %s: At a minimum, one of Decommissioning, Maintenance, Monitoring or Access Control must occur."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] == year
                                    if cursor[f.index('ACCESS')] in vnull and cursor[f.index('DECOM')] in vnull and cursor[f.index('TRANS')] != 'Y' """ #*24c04 (added TRANS. And only check if AWS_YR = current submission year)

                if len(matchingField) > 0:
                    for i in range(len(matchingField)):
                        command += """and cursor[f.index('""" + matchingField[i] + """')] != 'Y' """
                command += ']'

                exec(command) ## executing the command built above...
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): At a minimum, one of Decommissioning, Maintenance, Monitoring or Access Control must occur."%len(errorList))

            # CONTROL1
                errorList = ["Error on %s %s: CONTROL1 must be populated with the correct coding scheme where ACCESS is APPLY, ADD, BOTH or REMOVE.  *CONTROL1 = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('CONTROL1')]) for row in cursor
                                if cursor[f.index('ACCESS')] in ['APPLY','ADD','BOTH','REMOVE']
                                if cursor[f.index('CONTROL1')] not in ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 must be populated with the correct coding scheme where ACCESS is APPLY, ADD, BOTH or REMOVE."%len(errorList))

                errorList = ["Error on %s %s: CONTROL1 must follow the correct coding scheme if pouplated.  *CONTROL1 = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('CONTROL1')]) for row in cursor
                                if cursor[f.index('CONTROL1')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 must follow the correct coding scheme if pouplated.."%len(errorList))

            # CONTROL2
                if 'CONTROL2' in f:
                    errorList = ["Error on %s %s: CONTROL2 must follow the correct coding scheme if pouplated.  *CONTROL2 = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('CONTROL2')]) for row in cursor
                                    if cursor[f.index('CONTROL2')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL2 must follow the correct coding scheme if pouplated."%len(errorList))

            # CONTROL1 and 2 both should be null if ACCESS = REMOVE
                command = """errorList = ["Warning on %s %s: Both CONTROL1 and 2 should be null if ACCESS = REMOVE."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS')] == 'REMOVE'
                                    if cursor[f.index('CONTROL1')] not in vnull """

                if 'CONTROL2' in f:
                    command += """or cursor[f.index('CONTROL2')] not in vnull """
                command += ']'

                exec(command) ## executing the command built above...
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): Both CONTROL1 and 2 should be null if ACCESS = REMOVE."%len(errorList))                    


            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


       ###########################  Checking SRC   ############################

        if lyrAcro == "SRC":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # ROADID
                errorList = ["Error on %s %s: ROADID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADID must be populated."%len(errorList))

            # ROADCLAS
                errorList = ["Error on %s %s: ROADCLAS must be populated with the correct coding scheme. *ROADCLAS = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('ROADCLAS')]) for row in cursor
                                if cursor[f.index('ROADCLAS')] not in ['P','B']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADCLAS must be populated with the correct coding scheme."%len(errorList))

            # TRANS
                errorList = ["Error on %s %s: TRANS must be greater than or equal to plan start year, if populated.  *TRANS = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('TRANS')]) for row in cursor
                                if int(cursor[f.index('TRANS')] or 9999) < fmpStartYear]  # 'or 9999' - this will avoid flagging Null values
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRANS must be greater than or equal to plan start year, if populated."%len(errorList))

            # ACYEAR
                errorList = ["Error on %s %s: ACYEAR must be greater than or equal to plan start year and less than or equal to plan end year, if populated.  *ACYEAR = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('ACYEAR')]) for row in cursor
                                if int(cursor[f.index('ACYEAR')] or fmpStartYear) not in range(fmpStartYear, fmpStartYear + 11)] # 'or fmpStartYear' - this will avoid flagging Null values
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACYEAR must be greater than or equal to plan start year and less than or equal to plan end year, if populated."%len(errorList))

                errorList = ["Error on %s %s: ACCESS must be populated if ACYEAR is populated.  *ACYEAR = [%s] *ACCESS = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('ACYEAR')],cursor[f.index('ACCESS')]) for row in cursor
                                if cursor[f.index('ACCESS')] in vnull
                                if int(cursor[f.index('ACYEAR')] or 0) in range(fmpStartYear, fmpStartYear + 11)]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must be populated if ACYEAR is populated."%len(errorList))

            # ACCESS        # big change in v2017 spec
                errorList = ["Error on %s %s: ACCESS must follow the correct coding scheme if populated.  *ACCESS = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('ACCESS')]) for row in cursor
                                if cursor[f.index('ACCESS')] not in vnull + ['APPLY','REMOVE','BOTH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ACCESS must follow the correct coding scheme if populated."%len(errorList))

            # ACCESS & CONTROL1
                errorList = ["Error on %s %s: CONTROL1 must be populated with the correct coding scheme where ACCESS is APPLY or BOTH.  *ACCESS = [%s] *CONTROL1 = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('ACCESS')],cursor[f.index('CONTROL1')]) for row in cursor
                                if cursor[f.index('ACCESS')] in ['APPLY','BOTH']
                                if cursor[f.index('CONTROL1')] not in ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s):  CONTROL1 must be populated with the correct coding scheme where ACCESS is APPLY or BOTH."%len(errorList))

            # DECOM         # big change in v2017 spec
                errorList = ["Error on %s %s: DECOM must follow the correct coding scheme if populated.  *DECOM = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('DECOM')]) for row in cursor
                                if cursor[f.index('DECOM')] not in vnull + ['BERM','SCAR','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): DECOM must follow the correct coding scheme if populated."%len(errorList))

            # these validations have been removed in 2020. *2020.10.014 *2020.10.013
            # # MAINTAIN
            #     errorList = ["Error on %s %s: MAINTAIN must be populated with the correct coding scheme (Y or N)."%(id_field, cursor[id_field_idx]) for row in cursor
            #                     if cursor[f.index('MAINTAIN')] not in ['Y','N']]
            #     cursor.reset()
            #     if len(errorList) > 0:
            #         errorDetail[lyr].append(errorList)
            #         criticalError += 1
            #         recordValCom[lyr].append("Error on %s record(s): MAINTAIN must be populated with the correct coding scheme (Y or N)."%len(errorList))

            # # MONITOR
            #     errorList = ["Error on %s %s: MONITOR must be populated with the correct coding scheme (Y or N)."%(id_field, cursor[id_field_idx]) for row in cursor
            #                     if cursor[f.index('MONITOR')] not in ['Y','N']]
            #     cursor.reset()
            #     if len(errorList) > 0:
            #         errorDetail[lyr].append(errorList)
            #         criticalError += 1
            #         recordValCom[lyr].append("Error on %s record(s): MONITOR must be populated with the correct coding scheme (Y or N)."%len(errorList))                                        

            # # ACCESS, DECOM, MAINTAIN & MONITOR   #*24c11 added If AWS_YR == year. This was to prevent it from flagging road corridors not planned for this year but still a good-to-have info.
            #     errorList = ["Error on %s %s: One of DECOM, MAINTAIN, MONITOR or ACCESS must occur for each record. *DECOM = [%s] *MAINTAIN = [%s] *MONITOR = [%s] *ACCESS = [%s]"
            #                     %(id_field, cursor[id_field_idx],cursor[f.index('DECOM')],cursor[f.index('MAINTAIN')],cursor[f.index('MONITOR')],cursor[f.index('ACCESS')]) for row in cursor
            #                     if cursor[f.index('AWS_YR')] == year
            #                     if cursor[f.index('MAINTAIN')] != 'Y' and cursor[f.index('MONITOR')] != 'Y'
            #                     if cursor[f.index('ACCESS')] not in ['APPLY','REMOVE','BOTH']
            #                     if cursor[f.index('DECOM')] not in ['BERM','SCAR','SLSH','WATX']]
            #     cursor.reset()
            #     if len(errorList) > 0:
            #         errorDetail[lyr].append(errorList)
            #         criticalError += 1
            #         recordValCom[lyr].append("Error on %s record(s):  One of DECOM, MAINTAIN, MONITOR or ACCESS must occur for each record.."%len(errorList))

            # INTENT & TRANS
                errorList = ["Error on %s %s: INTENT must be populated if TRANS value is populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if int(cursor[f.index('TRANS')] or 0) >= fmpStartYear
                                if cursor[f.index('INTENT')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): INTENT must be populated if TRANS value is populated."%len(errorList))

            # CONTROL1
                errorList = ["Error on %s %s: CONTROL1 must follow the correct coding scheme if populated.  *CONTROL1 = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('CONTROL1')]) for row in cursor
                                if cursor[f.index('CONTROL1')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CONTROL1 must follow the correct coding scheme if populated."%len(errorList))

            # CONTROL2
                if 'CONTROL2' in f:
                    errorList = ["Error on %s %s: CONTROL2 must follow the correct coding scheme if populated.  *CONTROL2 = [%s]"
                                    %(id_field, cursor[id_field_idx],cursor[f.index('CONTROL2')]) for row in cursor
                                    if cursor[f.index('CONTROL2')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL2 must follow the correct coding scheme if populated."%len(errorList))

            # CONTROL1 or 2 must be populated if ACCESS = BOTH or APPLY
                command = """errorList = ["Warning on %s %s: CONTROL1 or 2 must be populated if ACCESS = BOTH or APPLY."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS')] in ['BOTH','APPLY']
                                    if cursor[f.index('CONTROL1')] in vnull """

                if 'CONTROL2' in f:
                    command += """and cursor[f.index('CONTROL2')] in vnull """
                command += ']'

                exec(command) ## executing the command built above...
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Warning on %s record(s): CONTROL1 or 2 must be populated if ACCESS = BOTH or APPLY."%len(errorList)) 

            # CONTROL1 and 2 both should be null if ACCESS = REMOVE
                command = """errorList = ["Warning on %s %s: Both CONTROL1 and 2 should be null if ACCESS = REMOVE."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS')] == 'REMOVE'
                                    if cursor[f.index('CONTROL1')] not in vnull """

                if 'CONTROL2' in f:
                    command += """or cursor[f.index('CONTROL2')] not in vnull """
                command += ']'

                exec(command) ## executing the command built above...
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    minorError += 1
                    recordValCom[lyr].append("Warning on %s record(s): Both CONTROL1 and 2 should be null if ACCESS = REMOVE."%len(errorList))    


            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking SRG   ############################

        if lyrAcro == "SRG":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # TRTMTHD1, 2 and 3
                # For TRTMTHD1, 2 or 3, the population of one of these attributes is mandatory where AWS_YR equals the fiscal year to which the AWS applies
                # The attribute population must follow the correct coding scheme
                codingScheme = " ['PLANT','SCARIFY','SEED','SEEDSIP'] " # simply change this line for other treatment layer validations!!
                t2check1 = ''
                t3check1 = ''
                t2check2 = ''
                t3check2 = ''
                if 'TRTMTHD2' in f:
                    t2check1 = " and cursor[f.index('TRTMTHD2')] not in " + codingScheme
                    t2check2 = " or cursor[f.index('TRTMTHD2')] not in " + codingScheme + " + vnull "
                if 'TRTMTHD3' in f:
                    t3check1 = " and cursor[f.index('TRTMTHD3')] not in " + codingScheme
                    t3check2 = " or cursor[f.index('TRTMTHD3')] not in " + codingScheme + " + vnull "                    

                command = """errorList = ["Error on %s %s: The population of TRTMTHD1, 2 or 3 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."
                                %(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] == year
                                if cursor[f.index('TRTMTHD1')] not in """ + codingScheme + t2check1 + t3check1 + "or (cursor[f.index('TRTMTHD1')] not in " + codingScheme + " + vnull " + t2check2 + t3check2 + ")]"     
                                # The first half of the last line checkes if at least one of the 3 fields have been populated with the coding scheme
                                # The second half of the last line checks if all 3 fields have correct coding scheme if populated
                exec(command)

                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of TRTMTHD1, 2 or 3 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%len(errorList))


            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking SRP   ############################

        if lyrAcro == "SRP":
            try:
            # RESID
                errorList = ["Error on %s %s: RESID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('RESID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): RESID must be populated."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking SSP   ############################

        if lyrAcro == "SSP":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # TRTMTHD1, 2 and 3
                # For TRTMTHD1, 2 or 3, the population of one of these attributes is mandatory where AWS_YR equals the fiscal year to which the AWS applies
                # The attribute population must follow the correct coding scheme
                codingScheme = " ['SIPMECH','SIPCHEMA','SIPCHEMG','SIPPB'] " # simply change this line for other treatment layer validations!!
                t2check1 = ''
                t3check1 = ''
                t2check2 = ''
                t3check2 = ''
                if 'TRTMTHD2' in f:
                    t2check1 = " and cursor[f.index('TRTMTHD2')] not in " + codingScheme
                    t2check2 = " or cursor[f.index('TRTMTHD2')] not in " + codingScheme + " + vnull "
                if 'TRTMTHD3' in f:
                    t3check1 = " and cursor[f.index('TRTMTHD3')] not in " + codingScheme
                    t3check2 = " or cursor[f.index('TRTMTHD3')] not in " + codingScheme + " + vnull "                    

                command = """errorList = ["Error on %s %s: The population of TRTMTHD1, 2 or 3 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."
                                %(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] == year
                                if cursor[f.index('TRTMTHD1')] not in """ + codingScheme + t2check1 + t3check1 + "or (cursor[f.index('TRTMTHD1')] not in " + codingScheme + " + vnull " + t2check2 + t3check2 + ")]"     
                                # The first half of the last line checkes if at least one of the 3 fields have been populated with the coding scheme
                                # The second half of the last line checks if all 3 fields have correct coding scheme if populated
                exec(command)

                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of TRTMTHD1, 2 or 3 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%len(errorList))


            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking STT   ############################

        if lyrAcro == "STT":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # TRTMTHD1, 2 and 3
                # For TRTMTHD1, 2 or 3, the population of one of these attributes is mandatory where AWS_YR equals the fiscal year to which the AWS applies
                # The attribute population must follow the correct coding scheme
                codingScheme = " ['CLCHEMA','CLCHEMG','CLMANUAL','CLMECH','CLPB','IMPROVE','THINPRE','CULTIVAT','PRUNE'] " # simply change this line for other treatment layer validations!!
                t2check1 = ''
                t3check1 = ''
                t2check2 = ''
                t3check2 = ''
                if 'TRTMTHD2' in f:
                    t2check1 = " and cursor[f.index('TRTMTHD2')] not in " + codingScheme
                    t2check2 = " or cursor[f.index('TRTMTHD2')] not in " + codingScheme + " + vnull "
                if 'TRTMTHD3' in f:
                    t3check1 = " and cursor[f.index('TRTMTHD3')] not in " + codingScheme
                    t3check2 = " or cursor[f.index('TRTMTHD3')] not in " + codingScheme + " + vnull "                    

                command = """errorList = ["Error on %s %s: The population of TRTMTHD1, 2 or 3 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."
                                %(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] == year
                                if cursor[f.index('TRTMTHD1')] not in """ + codingScheme + t2check1 + t3check1 + "or (cursor[f.index('TRTMTHD1')] not in " + codingScheme + " + vnull " + t2check2 + t3check2 + ")]"     
                                # The first half of the last line checkes if at least one of the 3 fields have been populated with the coding scheme
                                # The second half of the last line checks if all 3 fields have correct coding scheme if populated
                exec(command)

                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of TRTMTHD1, 2 or 3 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%len(errorList))


            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking SWC   ############################

        if lyrAcro == "SWC":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # WATXID
                errorList = ["Error on %s %s: WATXID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('WATXID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): WATXID must be populated."%len(errorList))

            # WATXTYPE
                errorList = ["Error on %s %s: WATXTYPE must be populated with the correct coding scheme.  *WATXTYPE = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('WATXTYPE')]) for row in cursor
                                if cursor[f.index('WATXTYPE')] not in ['BRID','TEMP','CULV','MULTI','FORD','ICE','BOX','ARCH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): WATXTYPE must be populated with the correct coding scheme.."%len(errorList))

            # TRANS
                errorList = ["Error on %s %s: TRANS must be populated with the correct coding scheme.  *TRANS = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('TRANS')]) for row in cursor
                                if cursor[f.index('TRANS')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TRANS must be populated with the correct coding scheme."%len(errorList))

            # CONSTRCT
                if 'CONSTRCT' in f:
                    errorList = ["Error on %s %s: CONSTRCT must follow the correct coding scheme where AWS_YR equals the start year of the AWS or the following year.  *CONSTRCT = [%s]"
                                    %(id_field, cursor[id_field_idx],cursor[f.index('CONSTRCT')]) for row in cursor
                                    if int(cursor[f.index('AWS_YR')] or 0) in [year,year+1] 
                                    if cursor[f.index('CONSTRCT')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONSTRCT must follow the correct coding scheme where AWS_YR equals the start year of the AWS or the following year."%len(errorList))

            # MONITOR
                if 'MONITOR' in f:
                    errorList = ["Error on %s %s: MONITOR must follow the correct coding scheme where AWS_YR equals the start year of the AWS or the following year.  *MONITOR = [%s]"
                                    %(id_field, cursor[id_field_idx],cursor[f.index('MONITOR')]) for row in cursor
                                    if int(cursor[f.index('AWS_YR')] or 0) in [year,year+1] 
                                    if cursor[f.index('MONITOR')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): MONITOR must follow the correct coding scheme where AWS_YR equals the start year of the AWS or the following year."%len(errorList))

            # REMOVE
                if 'REMOVE' in f:
                    errorList = ["Error on %s %s: REMOVE must follow the correct coding scheme where AWS_YR equals the start year of the AWS or the following year.  *REMOVE = [%s]"
                                    %(id_field, cursor[id_field_idx],cursor[f.index('REMOVE')]) for row in cursor
                                    if int(cursor[f.index('AWS_YR')] or 0) in [year,year+1] 
                                    if cursor[f.index('REMOVE')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): REMOVE must follow the correct coding scheme where AWS_YR equals the start year of the AWS or the following year."%len(errorList))

            # REPLACE
                if 'REPLACE' in f:
                    errorList = ["Error on %s %s: REPLACE must follow the correct coding scheme where AWS_YR equals the start year of the AWS or the following year.  *REPLACE = [%s]"
                                    %(id_field, cursor[id_field_idx],cursor[f.index('REPLACE')]) for row in cursor
                                    if int(cursor[f.index('AWS_YR')] or 0) in [year,year+1] 
                                    if cursor[f.index('REPLACE')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): REPLACE must follow the correct coding scheme where AWS_YR equals the start year of the AWS or the following year."%len(errorList))

            # Checking "At a minimum, one of Construction, Monitoring, Remove or Replace must occur for each record (CONSTRCT = Y MONITOR = Y REMOVE = Y or REPLACE = Y) where AWS_YR equals the fiscal year to which the AWS applies or the following year."
                optField = ['CONSTRCT','MONITOR','REMOVE','REPLACE']
                matchingField = list(set(optField) & set(f))
                if len(matchingField) == 0:   ## if none of CONSTRCT, MONITOR, REMOVE or REPLACE field exists, this is an error at field validation level.
                   fieldValComUpdate[lyr].append("At a minimum, one of CONSTRCT, MONITOR, REMOVE or REPLACE must occur.")
                   fieldValUpdate[lyr] = 'Invalid'
                else:
                    command = """errorList = ["Error on %s %s: One of CONSTRCT, MONITOR, REMOVE or REPLACE must occur for each record where AWS_YR equals the start year of the AWS or the following year."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if int(cursor[f.index('AWS_YR')] or 0) in [year,year+1] 
                                        if cursor[f.index('""" + matchingField[0] + """')] != 'Y' """

                    if len(matchingField) > 1:
                        for i in range(1,len(matchingField)):
                            command = command + """and cursor[f.index('""" + matchingField[i] + """')] != 'Y' """
                    command = command + ']'

                    exec(command) ## executing the command built above...
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): One of CONSTRCT, MONITOR, REMOVE or REPLACE must occur for each record where AWS_YR equals the start year of the AWS or the following year."%len(errorList))

            # ROADID
                errorList = ["Error on %s %s: ROADID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): ROADID must be populated."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True


        ###########################  Checking WSY   ############################

        if lyrAcro == "WSY":
            try:
            # AWS_YR
                # AWS_YR attribute from multiple layers are getting checked all at once
                # To find this code block, search this script for #ref-AWS_YR

            # WSYID
                errorList = ["Error on %s %s: WSYID must be populated."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('WSYID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): WSYID must be populated."%len(errorList))

            # TYPE
                errorList = ["Error on %s %s: TYPE must be populated with the correct coding scheme.  *TYPE = [%s]"
                                %(id_field, cursor[id_field_idx],cursor[f.index('TYPE')]) for row in cursor
                                if cursor[f.index('TYPE')] not in ['THY','TMY','LMY']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): TYPE must be populated with the correct coding scheme.."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True



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
            arcpy.AddMessage('    ') # just to add new line.

    return [errorDetail, recordVal, recordValCom, fieldValUpdate, fieldValComUpdate]


# Tester:
##if __name__ == '__main__':
##    summarytbl = {
##                'MU110_17SAC10': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCTYPE', 'AOCID'], ['OBJECTID', 'SHAPE', 'MU110_17SAC10_', 'MU110_17SAC10_ID', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAC11': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCID', 'AOCTYPE'], ['OBJECTID', 'SHAPE', 'MU110_17SAC11_', 'MU110_17SAC11_ID', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAG00': ['SAG', 'Scheduled Aggregate Extraction', 'NAD_1983_UTM_Zone_17N', ['AWS_YR', 'AGAREAID'], ['OBJECTID', 'SHAPE', 'MU110_17SAG00_', 'MU110_17SAG00_ID', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SSP00': ['SSP', 'Scheduled Site Preparation Treatments', 'NAD_1983_UTM_Zone_17N', ['AWS_YR', 'TRTMTHD1'], ['OBJECTID', 'SHAPE', 'MU110_17SSP00_', 'MU110_17SSP00_ID', 'BLOCKID', 'TRTMTHD2', 'SHAPE_LENGTH','SHAPE_AREA']],
##                'MU110_17SRA00': ['SRA', 'Scheduled Existing Road Activities', 'NAD_1983_UTM_Zone_17N', ['ROADID', 'ROADCLAS', 'AWS_YR'], ['OBJECTID', 'SHAPE', 'MU110_17SRA00_', 'MU110_17SRA00_ID', 'ACCESS', 'DECOM', 'MAINTAIN', 'MONITOR', 'CONTROL1', 'CONTROL2','RESPONS', 'RD_NETWORK', 'ACC_REM', 'SHAPE_LENGTH']],
##                'MU110_17SOR00': ['SOR', 'Scheduled Operational Road Boundaries', 'NAD_1983_UTM_Zone_17N', ['ORBID', 'AWS_YR'], ['OBJECTID', 'SHAPE', 'MU110_17SOR00_', 'MU110_17SOR00_ID', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17AGP00': ['AGP', 'Existing Forestry Aggregate Pits', 'NAD_1983_UTM_Zone_17N', ['PITID', 'PITOPEN', 'PITCLOSE', 'CAT9APP'], ['OBJECTID', 'SHAPE', 'MU110_17AGP00_', 'MU110_17AGP00_ID', 'PIT_NAME']],
##                'MU110_17SRC00': ['SRC', 'Scheduled Road Corridors', 'NAD_1983_UTM_Zone_17N', ['ROADID', 'ROADCLAS', 'AWS_YR'], ['OBJECTID', 'SHAPE', 'MU110_17SRC00_', 'MU110_17SRC00_ID', 'AOCXID', 'NOXING', 'ACCESS', 'DECOM', 'CONTROL1', 'ACC_REM', 'LAYER', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAC07': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCTYPE', 'AOCID'], ['OBJECTID', 'SHAPE', 'MU110_17SAC07_', 'MU110_17SAC07_ID', 'AOC_WIDTH', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAC06': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCID', 'AOCTYPE'], ['OBJECTID', 'SHAPE', 'MU110_17SAC06_', 'MU110_17SAC06_ID', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAC05': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCID', 'AOCTYPE'], ['OBJECTID', 'SHAPE', 'MU110_17SAC05_', 'MU110_17SAC05_ID', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAC04': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCTYPE', 'AOCID'], ['OBJECTID', 'SHAPE', 'MU110_17SAC04_', 'MU110_17SAC04_ID', 'AOC_WIDTH', 'SYMBOL', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAC03': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCTYPE', 'AOCID'], ['OBJECTID', 'SHAPE', 'MU110_17SAC03_', 'MU110_17SAC03_ID', 'TYPE', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAC02': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCID', 'AOCTYPE'], ['OBJECTID', 'SHAPE', 'MU110_17SAC02_', 'MU110_17SAC02_ID', 'STATUS', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAC01': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCID', 'AOCTYPE'], ['OBJECTID', 'SHAPE', 'MU110_17SAC01_', 'MU110_17SAC01_ID', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAC09': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCTYPE', 'AOCID'], ['OBJECTID', 'SHAPE', 'MU110_17SAC09_', 'MU110_17SAC09_ID', 'BUFF_DIST', 'STATUS', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SAC08': ['SAC', 'Scheduled Area Of Concern', 'NAD_1983_UTM_Zone_17N', ['AOCID', 'AOCTYPE'], ['OBJECTID', 'SHAPE', 'MU110_17SAC08_', 'MU110_17SAC08_ID', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SPT00': ['SPT', 'Scheduled Protection Treatment', 'NAD_1983_UTM_Zone_17N', ['AWS_YR', 'TRTMTHD1'], ['OBJECTID', 'SHAPE', 'MU754_17SPT00_', 'MU754_17SPT00_ID', 'SHAPE_LENGTH', 'SHAPE_AREA', 'TRTMTHD3']],
##                'MU110_17SWC00': ['SWC', 'Scheduled Water Crossing Activities', 'NAD_1983_UTM_Zone_17N', ['WATXTYPE', 'ROADID', 'WATXID', 'AWS_YR'], ['OBJECTID', 'SHAPE', 'MU110_17SWC00_', 'MU110_17SWC00_ID', 'WATXTYP2', 'WATXTYP3', 'THERMAL', 'CONSTRCT', 'MONITOR', 'REPLACE', 'REMOVE']],
##                'MU110_17SHR00': ['SHR', 'Scheduled Harvest', 'NAD_1983_UTM_Zone_17N', ['HARVCAT', 'AWS_YR', 'FUELWOOD', 'SILVSYS'], ['OBJECTID', 'SHAPE', 'MU110_17SHR00_', 'MU110_17SHR00_ID', 'BLOCKID', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SRG00': ['SRG', 'Scheduled Regeneration Treatments', 'NAD_1983_UTM_Zone_17N', ['AWS_YR', 'TRTMTHD1'], ['OBJECTID', 'SHAPE', 'MU110_17SRG00_', 'MU110_17SRG00_ID', 'BLOCKID', 'TRTMTHD2', 'SHAPE_LENGTH', 'SHAPE_AREA']],
##                'MU110_17SNW00': ['SNW', 'Scheduled Non-Water AOC Crossing', 'NAD_1983_UTM_Zone_17N', ['AWS_YR', 'AOCXID', 'ROADID'], ['OBJECTID', 'SHAPE', 'MU110_17SNW00_', 'MU110_17SNW00_ID', 'SHAPE_LENGTH']],
##                'MU110_17STT00': ['STT', 'Scheduled Tending Treatments', 'NAD_1983_UTM_Zone_17N', ['TRTMTHD1', 'AWS_YR'], ['OBJECTID', 'SHAPE', 'MU110_17STT00_', 'MU110_17STT00_ID', 'BLOCKID', 'TRTMTHD2', 'SHAPE_LENGTH', 'SHAPE_AREA']]
##                }
##
##    gdb = r"C:\DanielK_Workspace\FMP_LOCAL\Abitibi_River\AWS\2017\_data\FMP_Schema.gdb"
##    gdb = r'\\lrcpsoprfp00001\GIS-DATA\WORK-DATA\FMPDS\Romeo_Malette\AWS\2017\_data\FMP_Schema.gdb'
##    fmpStartYear = 2012
##    year = 2017
##    result = run(gdb, summarytbl, year, fmpStartYear)
##    pprint.pprint(result[0]) #errorDetail
##    pprint.pprint(result[1]) #recordVal
##    pprint.pprint(result[2]) #recordValCom
##    pprint.pprint(result[3]) #fieldValUpdate
##    pprint.pprint(result[4]) #fieldValComUpdate
