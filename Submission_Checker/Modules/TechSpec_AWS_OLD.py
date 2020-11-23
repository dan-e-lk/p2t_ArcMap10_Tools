#-------------------------------------------------------------------------------
# Name:         TechSpec_AWS_OLD.py
# Purpose:      This module checkes every validation statements under appendix 1
#               of AWS Tech Spec 2009
#
# Author:       RIAU, Ministry of Natural Resources and Forestry
#
# Notes:        To find the validation code, run Search (Ctrl+F) for validation header such as "A1.1.2")
# Created:      01/03/2017
#
#           Any further updates can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog
#-------------------------------------------------------------------------------
import arcpy
import os, sys
import Reference as R
import pprint

verbose = True

lyrInfo = {
# Dictionary of lists of lists
# Layer acronym            name                           mandatory fields                                  Data Type   Tech Spec       Tech Spec URL
    "AGP":  ["Existing Forestry Aggregate Pits",        ['PIT_ID', 'PIT_OPEN', 'PITCLOSE', 'CAT9APP'],      'point',    'A1.14',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=112'   ],
    "SAC":  ["Scheduled Area Of Concern",               ['AOCID', 'AOCTYPE'],                               'polygon',  'A1.2',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=79'    ],
    "SAG":  ["Scheduled Aggregate Extraction",          ['AWS_YR', 'AGAREAID'],                             'polygon',  'A1.9',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=102'   ],
    "SHR":  ["Scheduled Harvest",                       ['AWS_YR', 'SILVSYS', 'HARVCAT', 'FUELWOOD'],       'polygon',  'A1.1',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=75'    ],
    "SNW":  ["Scheduled Non-Water AOC Crossing",        ['AWS_YR', 'AOCXID', 'ROADID'],                     'arc',      'A1.8',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=100'   ],
    "SOR":  ["Scheduled Operational Road Boundaries",   ['AWS_YR', 'ORBID'],                                'polygon',  'A1.5',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=87'    ],
    "SPT":  ["Scheduled Protection Treatment",          ['AWS_YR', 'TRTMTHD1'],                             'polygon',  'A1.13',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=110'   ],
    "SRA":  ["Scheduled Existing Road Activities",      ['AWS_YR', 'ROADID', 'ROADCLAS'],                   'arc',      'A1.6',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=89'    ],
    "SRC":  ["Scheduled Road Corridors",                ['AWS_YR', 'ROADID', 'ROADCLAS'],                   'polygon',  'A1.4',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=82'    ],
    "SRG":  ["Scheduled Regeneration Treatments",       ['AWS_YR', 'TRTMTHD1'],                             'polygon',  'A1.11',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=106'   ],
    "SRP":  ["Scheduled Residual Patches",              ['AWS_YR', 'RESID'],                                'polygon',  'A1.3',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=80'    ],
    "SSP":  ["Scheduled Site Preparation Treatments",   ['AWS_YR', 'TRTMTHD1'],                             'polygon',  'A1.10',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=104'   ],
    "STT":  ["Scheduled Tending Treatments",            ['AWS_YR', 'TRTMTHD1'],                             'polygon',  'A1.12',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=108'   ],
    "SWC":  ["Scheduled Water Crossing Activities",     ['AWS_YR', 'WATXID', 'WATXTYPE', 'ROADID'],         'point',    'A1.7',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=95'    ]
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


#       ######### Going through each layer type in alphabetical order ##########


        ###########################  Checking AGP   ############################

        if lyrAcro == "AGP":
            try: # need try and except block here for cases such as not having mandatory fields.
            # PIT_ID
                errorList = ["Error on %s %s: The population of PIT_ID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('PIT_ID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of PIT_ID is mandatory (A1.14.1)."%len(errorList))

            # PIT_OPEN
                errorList = ["Error on %s %s: The population of PIT_OPEN is mandatory and the attribute must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if R.fimdate(cursor[f.index('PIT_OPEN')]) is None]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of PIT_OPEN is mandatory and the attribute must follow the correct coding scheme (A1.14.2)."%len(errorList))

            # PITCLOSE
                errorList = ["Error on %s %s: PITCLOSE must be either NULL or follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('PITCLOSE')] not in vnull
                                and R.fimdate(cursor[f.index('PITCLOSE')]) is None]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): PITCLOSE must be either NULL or follow the correct coding scheme (A1.14.3)."%len(errorList))


                errorList = ["Error on %s %s: The PITCLOSE date cannot be greater than 10 years from PIT_OPEN date."%(id_field, cursor[id_field_idx]) for row in cursor
                                if R.fimdate(cursor[f.index('PITCLOSE')]) is not None
                                and R.fimdate(cursor[f.index('PIT_OPEN')]) is not None
                                and R.fimdate(cursor[f.index('PITCLOSE')]) > (R.fimdate(str(int(cursor[f.index('PIT_OPEN')][:4]) + 10) +  cursor[f.index('PIT_OPEN')][4:]))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The date cannot be greater than 10 years from PIT_OPEN date (A1.14.3)."%len(errorList))


                errorList = ["Error on %s %s: If PITCLOSE is not null, CAT9APP must be null. If PITCLOSE is null, CAT9APP cannot be null."%(id_field, cursor[id_field_idx]) for row in cursor
                                if (cursor[f.index('PITCLOSE')] in vnull and cursor[f.index('CAT9APP')] in vnull)
                                or (cursor[f.index('PITCLOSE')] not in vnull and cursor[f.index('CAT9APP')] not in vnull)]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): If PITCLOSE is not null, CAT9APP must be null. If PITCLOSE is null, CAT9APP cannot be null (A1.14.3)."%len(errorList))

            # CAT9APP
                errorList = ["Error on %s %s: CAT9APP must be either NULL or follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('CAT9APP')] not in vnull
                                and R.fimdate(cursor[f.index('CAT9APP')]) is None]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): CAT9APP must be either NULL or follow the correct coding scheme (A1.14.4)."%len(errorList))


                errorList = ["Error on %s %s: The CAT9APP date cannot be greater than 10 years from PIT_OPEN date."%(id_field, cursor[id_field_idx]) for row in cursor
                                if R.fimdate(cursor[f.index('CAT9APP')]) is not None
                                and R.fimdate(cursor[f.index('PIT_OPEN')]) is not None
                                and R.fimdate(cursor[f.index('CAT9APP')]) > (R.fimdate(str(int(cursor[f.index('PIT_OPEN')][:4]) + 10) +  cursor[f.index('PIT_OPEN')][4:]))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The CAT9APP date cannot be greater than 10 years from PIT_OPEN date (A1.14.4)."%len(errorList))

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
                errorList = ["Error on %s %s: The population of AOCID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AOCID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of AOCID is mandatory (A1.2.1)."%len(errorList))

            # AOCTYPE
                errorList = ["Error on %s %s: The population of AOCTYPE is mandatory and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AOCTYPE')] not in ['M','R']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of AOCTYPE is mandatory and must follow the correct coding scheme (A1.2.2)."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True

        ###########################  Checking SAG   ############################

        if lyrAcro == "SAG":
            try:
            # AWS_YR
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.9.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.9.1)")

            # AGAREAID
                errorList = ["Error on %s %s: The population of AGAREAID is mandatory where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('AGAREAID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of AGAREAID is mandatory where AWS_YR equals the fiscal year to which the AWS applies (A1.9.2)."%len(errorList))

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
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.1.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.1.1)")

            # SILVSYS
                errorList = ["Error on %s %s: The population of SILVSYS is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('SILVSYS')] not in ['CC','SE','SH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of SILVSYS is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.1.2)."%len(errorList))

                errorList = ["Error on %s %s: The attribute population of SILVSYS must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull or int(cursor[f.index('AWS_YR')]) != year
                                if cursor[f.index('SILVSYS')] not in vnull + ['CC','SE','SH']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The attribute population of SILVSYS must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year) (A1.1.2)."%len(errorList))

            # HARVCAT
                errorList = ["Error on %s %s: The population of HARVCAT is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('HARVCAT')] not in ['REGULAR','BRIDGING','REDIRECT','ACCELER','FRSTPASS','SCNDPASS','SALVAGE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of HARVCAT is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.1.3)."%len(errorList))

                errorList = ["Error on %s %s: The attribute population of HARVCAT must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull or int(cursor[f.index('AWS_YR')]) != year
                                if cursor[f.index('HARVCAT')] not in vnull + ['REGULAR','BRIDGING','REDIRECT','ACCELER','FRSTPASS','SCNDPASS','SALVAGE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The attribute population of HARVCAT must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year) (A1.1.3)."%len(errorList))

                errorList = ["Error on %s %s: HARVCAT = BRIDGING is only available when the AWS start year is equal to the first year of the 10 year plan period."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('HARVCAT')] == 'BRIDGING'
                                if year != fmpStartYear]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): HARVCAT = BRIDGING is only available when the AWS start year is equal to the first year of the 10 year plan period (A1.1.3)."%len(errorList))

            # FUELWOOD
                errorList = ["Error on %s %s: The population of FUELWOOD is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('FUELWOOD')] not in ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of FUELWOOD is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.1.4)."%len(errorList))

                errorList = ["Error on %s %s: The attribute population of FUELWOOD must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull or int(cursor[f.index('AWS_YR')]) != year
                                if cursor[f.index('FUELWOOD')] not in vnull + ['Y','N']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The attribute population of FUELWOOD must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year) (A1.1.4)."%len(errorList))

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True

        ###########################  Checking SNW   ############################

        if lyrAcro == "SNW":
            try:
            # AWS_YR
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.8.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.8.1)")

            # AOCXID
                errorList = ["Error on %s %s: The population of AOCXID is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('AOCXID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of AOCXID is mandatory where AWS_YR equals the fiscal year to which the AWS applies (A1.8.2)."%len(errorList))

            # ROADID
                errorList = ["Error on %s %s: The population of ROADID is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of ROADID is mandatory where AWS_YR equals the fiscal year to which the AWS applies (A1.8.3)."%len(errorList))

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
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.5.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.5.1)")

            # ORBID
                errorList = ["Error on %s %s: The population of ORBID is mandatory where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('ORBID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of ORBID is mandatory where AWS_YR equals the fiscal year to which the AWS applies. (A1.5.2)."%len(errorList))

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
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.13.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.13.1)")

            # TRTMTHD1
                errorList = ["Error on %s %s: The population of TRTMTHD1 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('TRTMTHD1')] not in ['PCHEMA','PCHEMG','PMANUAL']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of TRTMTHD1 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies. (A1.13.2)."%len(errorList))

                errorList = ["Error on %s %s: The attribute population of TRTMTHD1 must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull or int(cursor[f.index('AWS_YR')]) != year
                                if cursor[f.index('TRTMTHD1')] not in vnull + ['PCHEMA','PCHEMG','PMANUAL']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The attribute population of TRTMTHD1 must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year) (A1.13.2)."%len(errorList))

            # TRTMTHD2
                if 'TRTMTHD2' in f:
                    errorList = ["Error on %s %s: If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if (cursor[f.index('TRTMTHD1')] in vnull and cursor[f.index('TRTMTHD2')] not in vnull)
                                    or cursor[f.index('TRTMTHD2')] not in vnull + ['PCHEMA','PCHEMG','PMANUAL']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme (A1.13.2)."%len(errorList))

            # TRTMTHD3
                if 'TRTMTHD3' in f:
                    if 'TRTMTHD2' in f:
                        errorList = ["Error on %s %s: If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if ((cursor[f.index('TRTMTHD1')] in vnull or cursor[f.index('TRTMTHD2')] in vnull) and cursor[f.index('TRTMTHD3')] not in vnull)
                                        or cursor[f.index('TRTMTHD3')] not in vnull + ['PCHEMA','PCHEMG','PMANUAL']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme (A1.13.2)."%len(errorList))
                    else:
                        fieldValUpdate[lyr] = 'Invalid'
                        fieldValComUpdate[lyr].append('TRTMTHD2 is mandatory when TRTMTHD3 is present.')

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
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.6.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.6.1)")

            # ROADID
                errorList = ["Error on %s %s: The population of ROADID is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of ROADID is mandatory where AWS_YR equals the fiscal year to which the AWS applies. (A1.6.2)."%len(errorList))

            # ROADCLAS
                errorList = ["Error on %s %s: The population of ROADCLAS is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('ROADCLAS')] not in ['P','B','O']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of ROADCLAS is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.6.3)."%len(errorList))

                errorList = ["Error on %s %s: The attribute population of ROADCLAS must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull or int(cursor[f.index('AWS_YR')]) != year
                                if cursor[f.index('ROADCLAS')] not in vnull + ['P','B','O']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The attribute population of ROADCLAS must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year). (A1.6.3)."%len(errorList))

            # ACCESS
                if 'ACCESS' in f:
                    errorList = ["Error on %s %s: The population of ACCESS must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                    if cursor[f.index('ACCESS')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of ACCESS must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.6.4)."%len(errorList))

            # ACCESS: Presence of CONTROL1 field is mandatory if there's one or more record where ACCESS = Y (existance of a field depends on value of another field.)
                    accessCounter = ["" for row in cursor if cursor[f.index('ACCESS')] == 'Y']
                    cursor.reset()
                    if len(accessCounter) > 0:
                        if 'CONTROL1' not in f:
                           fieldValComUpdate[lyr].append("Missing CONTROL1: If ACCESS = Y, CONTROL1 must be populated (A1.6.4).")
                           fieldValUpdate[lyr] = 'Invalid'

            # DECOM
                if 'DECOM' in f:
                    errorList = ["Error on %s %s: The population of DECOM must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                    if cursor[f.index('DECOM')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of DECOM must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.6.5)."%len(errorList))

            # ACCESS and DECOM can't both be Y
                if 'ACCESS' in f and 'DECOM' in f:
                    errorList = ["Error on %s %s: If DECOM = Y, then ACCESS must be N (if present) and vice versa. "%(id_field, cursor[id_field_idx]) for row in cursor
                                    if (cursor[f.index('ACCESS')] =='Y' and cursor[f.index('DECOM')] =='Y')]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): If DECOM = Y, then ACCESS must be N (if present) and vice versa (A1.6.4, A1.6.5)."%len(errorList))

            # MAINTAIN
                if 'MAINTAIN' in f:
                    errorList = ["Error on %s %s: The population of MAINTAIN must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                    if cursor[f.index('MAINTAIN')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of MAINTAIN must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.6.6)."%len(errorList))

            # MONITOR
                if 'MONITOR' in f:
                    errorList = ["Error on %s %s: The population of MONITOR must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                    if cursor[f.index('MONITOR')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of MONITOR must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.6.7)."%len(errorList))


            # Checking "At a minimum, one of Decommissioning, Maintenance, Monitoring or Access Control must occur for each record (DECOM = Y or MAINTAIN = Y or MONITOR = Y or ACCESS = Y) where AWS_YR equals the fiscal year to which the AWS applies."
                optField = ['DECOM','MAINTAIN','MONITOR','ACCESS']
                matchingField = list(set(optField) & set(f))
                if len(matchingField) == 0:   ## if none of 'DECOM','MAINTAIN','MONITOR','ACCESS' fields exists.
                   fieldValComUpdate[lyr].append("At a minimum, one of DECOM, MAINTAIN, MONITOR, ACCESS must occur. (A1.6.4)")
                   fieldValUpdate[lyr] = 'Invalid'
                else:
                    command = """errorList = ["Error on %s %s: At a minimum, one of Decommissioning, Maintenance, Monitoring or Access Control must occur for each record where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
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
                        recordValCom[lyr].append("Error on %s record(s): At a minimum, one of Decommissioning, Maintenance, Monitoring or Access Control must occur for each record where AWS_YR equals the fiscal year to which the AWS applies (A1.6.4)."%len(errorList))

            # CONTROL1
                if 'ACCESS' in f and 'CONTROL1' in f:
                    errorList = ["Error on %s %s: The population of CONTROL1 is mandatory and must follow the correct coding scheme where ACCESS = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS')] =='Y'
                                    if cursor[f.index('CONTROL1')] not in ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of CONTROL1 is mandatory and must follow the correct coding scheme where ACCESS = Y (A1.6.8)."%len(errorList))

                if 'CONTROL1' in f:
                    errorList = ["Error on %s %s: The population of CONTROL1 must follow the correct coding scheme (even when ACCESS is not Y)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('CONTROL1')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of CONTROL1 must follow the correct coding scheme (even when ACCESS is not Y) (A1.6.8)."%len(errorList))
            # CONTROL2
                if 'CONTROL1' in f and 'CONTROL2' in f:
                    errorList = ["Error on %s %s: CONTROL2 must only have a control type when CONTROL1 has a control type."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('CONTROL1')] in vnull
                                    if cursor[f.index('CONTROL2')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL2 must only have a control type when CONTROL1 has a control type (A1.6.8)."%len(errorList))

                if 'CONTROL2' in f:
                    errorList = ["Error on %s %s: The population of CONTROL2 must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('CONTROL2')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of CONTROL2 must follow the correct coding scheme (A1.6.8)."%len(errorList))

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
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.4.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.4.1)")

            # ROADID
                errorList = ["Error on %s %s: The population of ROADID is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of ROADID is mandatory where AWS_YR equals the fiscal year to which the AWS applies. (A1.4.2)."%len(errorList))

            # ROADCLAS - note that in SRC, "O" is not an option.
                errorList = ["Error on %s %s: The population of ROADCLAS is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('ROADCLAS')] not in ['P','B']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of ROADCLAS is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.4.3)."%len(errorList))

                errorList = ["Error on %s %s: The attribute population of ROADCLAS must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull or int(cursor[f.index('AWS_YR')]) != year
                                if cursor[f.index('ROADCLAS')] not in vnull + ['P','B']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The attribute population of ROADCLAS must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year). (A1.4.3)."%len(errorList))

            # AOCXID & NOXING - there's nothing to validate.

            # ACCESS
                if 'ACCESS' in f:
                    errorList = ["Error on %s %s: The population of ACCESS must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                    if cursor[f.index('ACCESS')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of ACCESS must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.4.6)."%len(errorList))

            # ACCESS: Presence of CONTROL1 field is mandatory if there's one or more record where ACCESS = Y (existance of a field depends on value of another field.)
                    accessCounter = ["" for row in cursor if cursor[f.index('ACCESS')] == 'Y']
                    cursor.reset()
                    if len(accessCounter) > 0:
                        if 'CONTROL1' not in f:
                           fieldValComUpdate[lyr].append("Missing CONTROL1: If ACCESS = Y, CONTROL1 must be populated (A1.4.6).")
                           fieldValUpdate[lyr] = 'Invalid'

            # DECOM
                if 'DECOM' in f:
                    errorList = ["Error on %s %s: The population of DECOM must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                    if cursor[f.index('DECOM')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of DECOM must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.4.7)."%len(errorList))

            # ACCESS and DECOM can't both be Y
                if 'ACCESS' in f and 'DECOM' in f:
                    errorList = ["Error on %s %s: If DECOM = Y, then ACCESS must be N (if present) and vice versa. "%(id_field, cursor[id_field_idx]) for row in cursor
                                    if (cursor[f.index('ACCESS')] =='Y' and cursor[f.index('DECOM')] =='Y')]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): If DECOM = Y, then ACCESS must be N (if present) and vice versa (A1.4.6, A1.4.7)."%len(errorList))

            # CONTROL1
                if 'ACCESS' in f and 'CONTROL1' in f:
                    errorList = ["Error on %s %s: The population of CONTROL1 is mandatory and must follow the correct coding scheme where ACCESS = Y."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('ACCESS')] =='Y'
                                    if cursor[f.index('CONTROL1')] not in ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of CONTROL1 is mandatory and must follow the correct coding scheme where ACCESS = Y (A1.4.8)."%len(errorList))

                if 'CONTROL1' in f:
                    errorList = ["Error on %s %s: The population of CONTROL1 must follow the correct coding scheme (even when ACCESS is not Y)."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('CONTROL1')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of CONTROL1 must follow the correct coding scheme (even when ACCESS is not Y) (A1.4.8)."%len(errorList))
            # CONTROL2
                if 'CONTROL1' in f and 'CONTROL2' in f:
                    errorList = ["Error on %s %s: CONTROL2 must only have a control type when CONTROL1 has a control type."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('CONTROL1')] in vnull
                                    if cursor[f.index('CONTROL2')] not in vnull]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): CONTROL2 must only have a control type when CONTROL1 has a control type (A1.4.8)."%len(errorList))

                if 'CONTROL2' in f:
                    errorList = ["Error on %s %s: The population of CONTROL2 must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('CONTROL2')] not in vnull + ['BERM','GATE','SCAR','SIGN','PRIV','SLSH','WATX']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of CONTROL2 must follow the correct coding scheme (A1.4.8)."%len(errorList))

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
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.11.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.11.1)")

            # TRTMTHD1
                errorList = ["Error on %s %s: The population of TRTMTHD1 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('TRTMTHD1')] not in ['PLANT','SCARIFY','SEED','SEEDSIP']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of TRTMTHD1 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies. (A1.11.2)."%len(errorList))

                errorList = ["Error on %s %s: The attribute population of TRTMTHD1 must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull or int(cursor[f.index('AWS_YR')]) != year
                                if cursor[f.index('TRTMTHD1')] not in vnull + ['PLANT','SCARIFY','SEED','SEEDSIP']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The attribute population of TRTMTHD1 must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year) (A1.11.2)."%len(errorList))

            # TRTMTHD2
                if 'TRTMTHD2' in f:
                    errorList = ["Error on %s %s: If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if (cursor[f.index('TRTMTHD1')] in vnull and cursor[f.index('TRTMTHD2')] not in vnull)
                                    or cursor[f.index('TRTMTHD2')] not in vnull + ['PLANT','SCARIFY','SEED','SEEDSIP']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme (A1.11.2)."%len(errorList))

            # TRTMTHD3
                if 'TRTMTHD3' in f:
                    if 'TRTMTHD2' in f:
                        errorList = ["Error on %s %s: If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if ((cursor[f.index('TRTMTHD1')] in vnull or cursor[f.index('TRTMTHD2')] in vnull) and cursor[f.index('TRTMTHD3')] not in vnull)
                                        or cursor[f.index('TRTMTHD3')] not in vnull + ['PLANT','SCARIFY','SEED','SEEDSIP']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme (A1.11.2)."%len(errorList))
                    else:
                        fieldValUpdate[lyr] = 'Invalid'
                        fieldValComUpdate[lyr].append('TRTMTHD2 is mandatory when TRTMTHD3 is present.')

            except ValueError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to missing mandatory field(s)"%lyr)
                criticalError += 1
            except TypeError:
                recordValCom[lyr].append("***Unable to run full validation on %s due to unexpected error."%lyr)
                systemError = True

        ###########################  Checking SRP   ############################

        if lyrAcro == "SRP":
            try:
            # AWS_YR
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.3.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.3.1)")

            # RESID
                errorList = ["Error on %s %s: The population of RESID is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('RESID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of RESID is mandatory where AWS_YR equals the fiscal year to which the AWS applies. (A1.3.2)."%len(errorList))

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
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.10.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.10.1)")

            # TRTMTHD1
                errorList = ["Error on %s %s: The population of TRTMTHD1 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('TRTMTHD1')] not in ['SIPMECH','SIPCHEMA','SIPCHEMG','SIPPB']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of TRTMTHD1 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies. (A1.10.2)."%len(errorList))

                errorList = ["Error on %s %s: The attribute population of TRTMTHD1 must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull or int(cursor[f.index('AWS_YR')]) != year
                                if cursor[f.index('TRTMTHD1')] not in vnull + ['SIPMECH','SIPCHEMA','SIPCHEMG','SIPPB']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The attribute population of TRTMTHD1 must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year) (A1.10.2)."%len(errorList))

            # TRTMTHD2
                if 'TRTMTHD2' in f:
                    errorList = ["Error on %s %s: If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if (cursor[f.index('TRTMTHD1')] in vnull and cursor[f.index('TRTMTHD2')] not in vnull)
                                    or cursor[f.index('TRTMTHD2')] not in vnull + ['SIPMECH','SIPCHEMA','SIPCHEMG','SIPPB']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme (A1.10.2)."%len(errorList))

            # TRTMTHD3
                if 'TRTMTHD3' in f:
                    if 'TRTMTHD2' in f:
                        errorList = ["Error on %s %s: If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if ((cursor[f.index('TRTMTHD1')] in vnull or cursor[f.index('TRTMTHD2')] in vnull) and cursor[f.index('TRTMTHD3')] not in vnull)
                                        or cursor[f.index('TRTMTHD3')] not in vnull + ['SIPMECH','SIPCHEMA','SIPCHEMG','SIPPB']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme (A1.10.2)."%len(errorList))
                    else:
                        fieldValUpdate[lyr] = 'Invalid'
                        fieldValComUpdate[lyr].append('TRTMTHD2 is mandatory when TRTMTHD3 is present.')

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
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.12.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.12.1)")

            # TRTMTHD1
                errorList = ["Error on %s %s: The population of TRTMTHD1 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('TRTMTHD1')] not in ['CLCHEMA','CLCHEMG','CLMANUAL','CLMECH','CLPB','IMPROVE','THINPRE','CULTIVAT','PRUNE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of TRTMTHD1 is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies. (A1.12.2)."%len(errorList))

                errorList = ["Error on %s %s: The attribute population of TRTMTHD1 must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year)."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull or int(cursor[f.index('AWS_YR')]) != year
                                if cursor[f.index('TRTMTHD1')] not in vnull + ['CLCHEMA','CLCHEMG','CLMANUAL','CLMECH','CLPB','IMPROVE','THINPRE','CULTIVAT','PRUNE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The attribute population of TRTMTHD1 must follow the correct coding scheme (even if the AWS_YR doesn't equal the fiscal year) (A1.12.2)."%len(errorList))

            # TRTMTHD2
                if 'TRTMTHD2' in f:
                    errorList = ["Error on %s %s: If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if (cursor[f.index('TRTMTHD1')] in vnull and cursor[f.index('TRTMTHD2')] not in vnull)
                                    or cursor[f.index('TRTMTHD2')] not in vnull + ['CLCHEMA','CLCHEMG','CLMANUAL','CLMECH','CLPB','IMPROVE','THINPRE','CULTIVAT','PRUNE']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): If TRTMTHD2 is populated then TRTMTHD1 must also be populated and TRTMTHD2 must follow the correct coding scheme (A1.12.2)."%len(errorList))

            # TRTMTHD3
                if 'TRTMTHD3' in f:
                    if 'TRTMTHD2' in f:
                        errorList = ["Error on %s %s: If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if ((cursor[f.index('TRTMTHD1')] in vnull or cursor[f.index('TRTMTHD2')] in vnull) and cursor[f.index('TRTMTHD3')] not in vnull)
                                        or cursor[f.index('TRTMTHD3')] not in vnull + ['CLCHEMA','CLCHEMG','CLMANUAL','CLMECH','CLPB','IMPROVE','THINPRE','CULTIVAT','PRUNE']]
                        cursor.reset()
                        if len(errorList) > 0:
                            errorDetail[lyr].append(errorList)
                            criticalError += 1
                            recordValCom[lyr].append("Error on %s record(s): If TRTMTHD3 is populated then TRTMTHD1 and TRTMTHD2 must also be populated and TRTMTHD3 must follow the correct coding scheme (A1.12.2)."%len(errorList))
                    else:
                        fieldValUpdate[lyr] = 'Invalid'
                        fieldValComUpdate[lyr].append('TRTMTHD2 is mandatory when TRTMTHD3 is present.')

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
                errorList = ["Error on %s %s: AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] in vnull
                                or (int(cursor[f.index('AWS_YR')]) !=0 and (int(cursor[f.index('AWS_YR')]) < fmpStartYear or int(cursor[f.index('AWS_YR')]) > (fmpStartYear + 9)))]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): AWS_YR cannot be less than the FMP start year (except for 0 on areas not scheduled) or greater than the plan end year minus 1 (A1.7.1)."%len(errorList))

                specialList = ['' for row in cursor if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year ]
                cursor.reset()
                if len(specialList) == 0:
                    criticalError += 1
                    recordValCom[lyr].append("Error on AWS_YR attributes: At least one feature must be populated with the AWS start year identified in the FI Portal submission record. (A1.7.1)")

            # WATXID
                errorList = ["Error on %s %s: The population of WATXID is mandatory."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('WATXID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of WATXID is mandatory (A1.7.2)."%len(errorList))

            # WATXTYPE
                errorList = ["Error on %s %s: The population of WATXTYPE is mandatory and must follow the correct coding scheme."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('WATXTYPE')] not in ['BRID','CULV','FORD','ICE']]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of WATXTYPE is mandatory and must follow the correct coding scheme (A1.7.3)."%len(errorList))

            # CONSTRCT
                if 'CONSTRCT' in f:
                    errorList = ["Error on %s %s: The population of CONSTRCT must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                    if cursor[f.index('CONSTRCT')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of CONSTRCT must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.7.4)."%len(errorList))

            # MONITOR
                if 'MONITOR' in f:
                    errorList = ["Error on %s %s: The population of MONITOR must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                    if cursor[f.index('MONITOR')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of MONITOR must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.7.5)."%len(errorList))

            # REMOVE
                if 'REMOVE' in f:
                    errorList = ["Error on %s %s: The population of REMOVE must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                    if cursor[f.index('REMOVE')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of REMOVE must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.7.6)."%len(errorList))

            # REPLACE
                if 'REPLACE' in f:
                    errorList = ["Error on %s %s: The population of REPLACE must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                    if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                    if cursor[f.index('REPLACE')] not in ['Y','N']]
                    cursor.reset()
                    if len(errorList) > 0:
                        errorDetail[lyr].append(errorList)
                        criticalError += 1
                        recordValCom[lyr].append("Error on %s record(s): The population of REPLACE must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies (A1.7.7)."%len(errorList))

            # Checking "At a minimum, one of Construction, Monitoring, Remove or Replace must occur for each record (CONSTRCT = Y MONITOR = Y REMOVE = Y or REPLACE = Y) where AWS_YR equals the fiscal year to which the AWS applies or the following year."
                optField = ['CONSTRCT','MONITOR','REMOVE','REPLACE']
                matchingField = list(set(optField) & set(f))
                if len(matchingField) == 0:   ## if none of CONSTRCT, MONITOR, REMOVE or REPLACE fields exists.
                   fieldValComUpdate[lyr].append("At a minimum, one of CONSTRCT, MONITOR, REMOVE or REPLACE must occur. (A1.7.4)")
                   fieldValUpdate[lyr] = 'Invalid'
                else:
                    command = """errorList = ["Error on %s %s: At a minimum, one of Construction, Monitoring, Remove or Replace must occur for each record where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                        if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
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
                        recordValCom[lyr].append("Error on %s record(s): At a minimum, one of Construction, Monitoring, Remove or Replace must occur for each record where AWS_YR equals the fiscal year to which the AWS applies (A1.7.4)."%len(errorList))

            # ROADID
                errorList = ["Error on %s %s: The population of ROADID is mandatory and must follow the correct coding scheme where AWS_YR equals the fiscal year to which the AWS applies."%(id_field, cursor[id_field_idx]) for row in cursor
                                if cursor[f.index('AWS_YR')] not in vnull and int(cursor[f.index('AWS_YR')]) == year
                                if cursor[f.index('ROADID')] in vnull]
                cursor.reset()
                if len(errorList) > 0:
                    errorDetail[lyr].append(errorList)
                    criticalError += 1
                    recordValCom[lyr].append("Error on %s record(s): The population of ROADID is mandatory where AWS_YR equals the fiscal year to which the AWS applies. (A1.7.8)."%len(errorList))

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
            arcpy.AddMessage('') # just to add new line.

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
##                'MU110_17AGP00': ['AGP', 'Existing Forestry Aggregate Pits', 'NAD_1983_UTM_Zone_17N', ['PIT_ID', 'PIT_OPEN', 'PITCLOSE', 'CAT9APP'], ['OBJECTID', 'SHAPE', 'MU110_17AGP00_', 'MU110_17AGP00_ID', 'PIT_NAME']],
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
