#-------------------------------------------------------------------------------
# Name:        Reference
# Purpose:     This stores constant variables and functions that applies to all plans.
#
# Author:      Ministry of Natural Resources and Forestry
#
# Created:     24/02/2017
# Copyright:   MNRF
#           Any further updates can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog
#-------------------------------------------------------------------------------
import os, datetime, time

# plan start year and region information is not being used by the checker tool, but the fmu and the code are being used.
# https://www.ontario.ca/page/management-units-and-forest-management-plan-renewal-schedules#section-1
# Last edited on Nov 16, 2020. bug id: *2020.11.04
static_db = {
#           fmu                     code        plan start years    region
        'Abitibi_River':        [   '110',      [2012, 2022],       'NE'    ],
        'Algoma':               [   '615',      [2010, 2020],       'NE'    ],
        'Algonquin_Park':       [   '451',      [2010, 2021],       'S'     ],
        'Bancroft_Minden':      [   '220',      [2011, 2021],       'S'     ],
        'Big_Pic':              [   '067',      [2007, 2017],       'NE'    ], # will be a part of Pic_Forest in 2019
        'Black_River':          [   '370',      [2006],             ''      ], #outdated?
        'Boundary_Waters':      [   '406',      [2020, 2030],       'NW'    ], # updated 2020
        'Black_Spruce':         [   '035',      [2011, 2021],       'NW'    ],
        'Caribou':              [   '175',      [2008, 2020],       'NW'    ],
        'Crossroute':           [   '405',      [2007, 2017],       'NW'    ],
        'Dog_River_Matawin':    [   '177',      [2009, 2021],       'NW'    ],
        'Dryden':               [   '535',      [2011, 2021],       'NW'    ],
        'English_River':        [   '230',      [2009, 2019],       'NW'    ],
        'French_Severn':        [   '360',      [2009, 2019],       'S'     ],
        'Gordon_Cosens':        [   '438',      [2010, 2020],       'NE'    ],
        'Hearst':               [   '601',      [2007, 2019],       'NE'    ],
        'Kenogami':             [   '350',      [2011, 2021],       'NW'    ],
        'Kenora':               [   '644',      [2012, 2022],       'NW'    ],
        'Lac_Seul':             [   '702',      [2011, 2021],       'NW'    ],
        'Lake_Nipigon_815':     [   '815',      [2011, 2021],       'NW'    ], # Lake_Nipigon used to be #815 updated 2021
        'Lake_Nipigon':         [   '816',      [2011, 2021],       'NW'    ], # Lake_Nipigon used to be #815 updated 2021
        'Lakehead':             [   '796',      [2007, 2021],       'NW'    ],
        'Magpie':               [   '565',      [2009, 2019],       'NE'    ],
        'Martel':               [   '509',      [2011, 2021],       'NE'    ],
        'Missanaibi':        	[   '574',      [2021],             'NE'    ],  # Martel-Magpie became Missanaibi in 2021    
        'Mazinaw_Lanark':       [   '140',      [2011, 2021],       'S'     ],
        'Nagagami':             [   '390',      [2011, 2021],       'NE'    ],
        'Nipissing':            [   '754',      [2009, 2019],       'NE'    ],
        'Northshore':           [   '680',      [2010, 2020],       'NE'    ],
        'Ogoki':                [   '415',      [2008, 2020],       'NW'    ],
        'Ottawa_Valley':        [   '780',      [2011, 2021],       'S'     ],
        'Pic_Forest':           [   '966',      [2021],             'NE'    ], # Amalgamation of Big_Pic and Pic_River as of 2019 plan. Pic's new start year is now 2021
        'Pic_River':            [   '965',      [2006, 2013],       'NE'    ], # will be a part of Pic_Forest in 2019
        'Pineland':             [   '421',      [2011, 2021],       'NW'    ],
        'Red_Lake':             [   '840',      [2008, 2020],       'NW'    ],
        'Romeo_Malette':        [   '930',      [2009, 2019],       'NE'    ],
        'Sapawe':               [   '853',      [2010, 2020],       'NW'    ],
        'Spanish':              [   '210',      [2010, 2020],       'NE'    ],
        'Sudbury':              [   '889',      [2010, 2020],       'NE'    ],
        'Temagami':             [   '898',      [2009, 2019],       'NE'    ],
        'Timiskaming':          [   '280',      [2011, 2021],       'NE'    ],
        'Trout_Lake':           [   '120',      [2009, 2021],       'NW'    ],
        'Wabadowgong_Noopming': [   '443',      [2011, 2023],       'NW'    ], # The former Armstrong Forest has been separated from the Lake Nipigon Forest; the new Wabadowgong Noopming Forest has been designated #update 2021
        'Wabigoon':             [   '130',      [2008, 2019],       'NW'    ],
        'Whiskey_Jack':         [   '490',      [2012, 2022],       'NW'    ],
        'White_River':          [   '060',      [2008, 2018],       'NE'    ],
        'Whitefeather':         [   '994',      [2012, 2022],       'NW'    ]
        }

# spcomp list in 2017 tech spec
##spcList2017 = ['AX', 'AB', 'AW', 'PL', 'PT', 'BD', 'BE', 'BW', 'BY', 'BN', 'CE', 'CR', 'CH', 'CB', 'OC', 'EX', 'EW', 'BF', 'OH', 'HE', 'HI', 'IW', 'LA', 'MH', 'MR', 'MS', 'MR', 'MH', 'OB', 'OR', 'OW', 'PN', 'PJ', 'PR', 'PS', 'PW', 'PO', 'PB', 'SX', 'SB', 'SR', 'SW', 'LA']

SpcListInterp = ['AB', 'AW', 'AX', 'BD', 'BE', 'BF', 'BG', 'BN', 'BW', 'BY', 'CB', 'CD', 'CE', 'CH', 'CR', 'CW', 'EW', 'EX', 'HE', 'HI', 'IW', 'LA', 'LO', 'MH', 'MR', 'MS', 'MX', 'OC', 'OH', 'OR', 'OW', 'OX', 'PB', 'PD', 'PJ', 'PL', 'PO', 'PR', 'PS', 'PT', 'PW', 'PX', 'SB', 'SW', 'SX', 'WB', 'WI']

SpcListOther = ['AL', 'AQ', 'AP', 'AG', 'BC', 'BP', 'GB', 'BB', 'CAT', 'CC', 'CM', 'CP', 'CS', 'CT', 'ER', 'EU', 'HK', 'HT', 'HL', 'HB', 'HM', 'HP', 'HS', 'HC', 'KK', 'LE', 'LJ', 'BL', 'LL', 'LB', 'GT', 'MB', 'MF', 'MM', 'MT', 'MN', 'MP', 'AM', 'EMA', 'MO', 'OBL', 'OB', 'OCH', 'OP', 'OS', 'OSW', 'PA', 'PN', 'PP', 'PC', 'PH', 'PE', 'RED', 'SS', 'SC', 'SK', 'SN', 'SR', 'SY', 'TP', 'HAZ']

def spcVal(data, fieldname, version = 2017): #sample data: 'Cw  70La  20Sb  10'
    # This function will return None if no error's found or if the input is None or empty string.
    if data in [None,'',' ']:
        return None
    else:
        try:
            if len(data)%6 == 0:
                n = len(data)/6
                spcList = [data[6*i:6*i+3].strip().upper() for i in range(n)]
                percentList = [int(data[6*i+3:6*i+6].strip()) for i in range(n)]

                if sum(percentList) == 100:
                    if len(set(spcList)) == len(spcList):

                        correctList = list(set(spcList)&set(SpcListInterp))
                        # To save processing time, check the spc code with the most common spc list (SpcListInterp) first, if not found, check the other possible spc code
                        if len(correctList) != len(spcList):
                            correctList = list(set(spcList)&set(SpcListInterp + SpcListOther))

                        if len(correctList) == len(spcList):
                            if sorted(percentList,reverse=True) == percentList:
                                return None
                            else:
                                return ["Warning1","%s values are not in descending order."%fieldname]
                        else:
                            wrongList = list(set(spcList) - set(correctList))
                            return ["Error4","%s has invalid species code(s)"%fieldname]
                    else:
                        return ["Error3","%s has duplicate species codes"%fieldname]
                else:
                    return ["Error2","%s does not add up to 100"%fieldname]
            else:
                return ["Error1", "%s does not follow the SSSPPPSSSPPP pattern"%fieldname] #*24b11
        except:
            return ["Error1", "%s does not follow the SSSPPPSSSPPP pattern"%fieldname] #*24b11


def findLeadSpc(spcomp):
    """
    This function will try to find lead species of a given spcomp.
    Data parameter is the value of SPCOMP - for example, 'PR  80PW  20'
    The function will return None if spcomp doesn't follow the coding scheme.
    The function will return a list of lead species (in case there's a tie) if spcomp follows the coding scheme.
    """
    try:
        if len(spcomp)> 0 and len(spcomp)%6 == 0:
            n = len(spcomp)/6
            spcList = [spcomp[6*i:6*i+3].strip().upper() for i in range(n)]
            percentList = [int(spcomp[6*i+3:6*i+6].strip()) for i in range(n)]
            spcompDict = dict(zip(spcList,percentList))

            maxPercent = sorted(percentList, reverse=True)[0] # highest number in percentList
            leadSpcList = [spc for spc, percent in spcompDict.items() if percent == maxPercent]
            return leadSpcList

        else:
            return None
    except:
        return None



#    ------------       Checker for PRI_ECO and SEC_ECO     --------------------

# Geographic Range
ecoG = ['A','B','G','S','U']
# Vegetative Modifier
ecoV = ['Tt','Tl','S','N','X','']
# Substrate Depth Modifier
ecoD = ['R','VS','S','M','MD','D','']
# Substrate moisture modifier
ecoM = ['d','f','h','m','s','v','w','x']
# Substrate Chemistry Modifier
ecoC = ['a','b','k','n','z']
# Vegetative cover clss modifier
ecoS = ['cTt','oTt','sTt','Tt ','Tl ','sTl','St ','sSt','Sl ','sSl','H  ','sH ','Nv ','X  ']

def ecoVal(data, fieldname, version = 2017):
    # assuming the data is not blank or null
    if len(data) >= 4:
        if len(data.strip()) <= 13:
            if data[0] in ecoG:
                try:
                    if int(data[1:4]) < 225 or int(data[1:4]) > 996:
                        if len(data) > 4:
                            if data[4:6].strip() in ecoV:
                                if len(data)>6:
                                    if data[6:8].strip() in ecoD:
                                        return None
                                    else:
                                        return ["Error","%s has invalid substrate depth modifier."%fieldname]
                            else:
                                return ["Error","%s has invalid vegetative modifier."%fieldname]
                    else:
                        return ["Error","%s has invalid ecosite number."%fieldname]
                except:
                    return ["Error","%s has invalid ecosite number."%fieldname]
            else:
                return ["Error","%s has incorrect geographic range code"%fieldname]
        else:
            return ["Error","%s has over 13 characters"%fieldname]
    else:
        return ["Error","%s is too short or does not follow the coding scheme."%fieldname]





def FMUCodeConverter(x):
    '''if the input x is fmu name, the output is the code and vice versa.
        Note that the input should be String format.'''
    try:
        return static_db[x][0]
    except:
        try:
            fmu = next(key for key, value in static_db.items() if value[0] == x)
            return fmu
        except Exception:
            print("ERROR: " + x + " is neither fmu name nor the code.")
            return None

def pathFinder(basePaths,fmu,plan,year):
    # concatenates the poth and folder names. for example, it returns "\\lrcpsoprfp00001\GIS-DATA\WORK-DATA\FMPDS\Abitibi_River\AWS\2017\_data\FMP_Schema.gdb"
    for b in basePaths:
        path = os.path.join(b,fmu,plan,str(year),'_data','FMP_Schema.gdb')
        if os.path.exists(path):
            gdbfilename = path
            break
    try:
        return gdbfilename
    except:
        print("ERROR: %s does not exist!" %path)
        print("Check if you have spelled the FMU correctly.")
        return "ERROR!! Could not find the geodatabase with the submission files!!!"


def fimdate(Fimdatecode):
    # input the fimdate such as 2010MAR29). Will return date format such as 2010-03-29
    Fimdateformat = "%Y%b%d"
    try:
        v= time.strptime(Fimdatecode,Fimdateformat)
        return datetime.date(v[0],v[1],v[2])
    except TypeError:
        return None
    except ValueError:
        return None

def findSubID(mainfolder):
    # input = \\lrcpsoprfp00001\GIS-DATA\WORK-DATA\FMPDS\Abitibi_River\AWS\2017, output = submission id number.
    files = os.listdir(mainfolder)
    try:
        fitxt = [s for s in files if "FI_SUBMISSION" in s.upper()] #list of files that has "fi_Submission" in its filename.
        return int(fitxt[0].split('.')[0].split('_')[-1]) #returning submission number
    except:
        try:
            lyrfile = [s for s in files if ".lyr" in s] #list of layer files (there should be just one).
            return int(lyrfile[0].split('.')[0].split('_')[-1]) # returning submission number at the end of layer filename.
        except Exception:
            return ''

def shortenList(lst):
    '''Input a long list and it will turn the list into a tooltip (only can see when the user hover over).'''
    if len(lst) < 4:
        return str(lst)
    else:
        return """<div class="tooltip">""" + str(lst)[:25] + """...<span class="tooltiptext">""" + str(lst) + """</span></div>"""

def shortenStr(string):
    '''Input a long string and it will turn the string into a tooltip (visible only when the user hover over).'''
    if len(string) < 40:
        return string
    else:
        return """<div class="tooltip">""" + string[:35] + """...<span class="tooltiptext">""" + string + """</span></div>"""


def sortError(errorListList, maxnum):
    ''' input should be errorDetail[lyr] and an integer. This function will return reduced error list in case there are thousands of same error type'''
    newList = []
##        uniqueError = [i[0].split(":")[1] for i in errorListList]

    for errorType in errorListList:
        error_count = len(errorType)
        if error_count >= maxnum:
            newList.append(errorType[:maxnum] + ['... and %s more errors (warnings) like this.'%str(error_count-maxnum)])
        else:
            newList.append(errorType)

    return newList


def findPDF(pdf):
    """ input = FIM_AWS_TechSpec_2017.pdf#page=111
    output = file://cihs.ad.gov.on.ca/mnrf/Groups/ROD/RODOpen/PDF/FIM_AWS_TechSpec_2017.pdf#page=111"""
    script_dir = os.path.split(__file__)[0]
    pdf_path = 'file:' + os.path.join(script_dir,'PDF',pdf)
    return pdf_path


# def standard_check(current_field, cursor, objectid, error_msg, if_statement, critical_error = True):
#     list_comprehension = """errorList = ["Error on OBJECTID %s: "%cursor[objectid] + error_msg  for row in cursor """ + if_statement + "]"
#     exec(list_comprehension)
#     cursor.reset()
#     if len(errorList) > 0:
#         errorDetail[lyr].append(errorList)
#         criticalError += 1
#         recordValCom[lyr].append("Error on %s record(s): The population of POLYID is mandatory."%len(errorList))

#     polyIDList = [cursor[f.index('POLYID')] for row in cursor if cursor[f.index('POLYID')] not in vnull ]
#     cursor.reset()
#     numDuplicates = len(polyIDList) - len(set(polyIDList))
#     if numDuplicates > 0:
#         criticalError += 1
#         recordValCom[lyr].append("Error on %s record(s): The POLYID attribute must contain a unique value."%numDuplicates)



def create_cursor(lyr_path, emf, f):
    """
    lyr_path is the full path to the feature class, shapefile or coverage.
    emf is the list of existing mandatory fields.
    f is the list of all fields in lyr_path.
    Output of this function is a cursor that only contains records where NOT all mandatory fields are blank or null.
    Function returns None if it fails.
    This function was created to eliminate the records that carries artifact polygons resulting from coverage donut holes.
    """
    import arcpy, os
    # arcpy.AddMessage("Running create_cursor function on %s"%lyr_path)
    try:
        
        lyr = lyr_path
        # example emf used: emf = ['HARVCAT','SILVSYS','ESTAREA','DSTBFU']

        # in the case of BMI/PCI/OPI, we don't need to test every field...
        if len(emf) > 20:
            emf = emf[:20]

        sqldict = dict(zip(emf,[None for i in emf])) #eg. {'ESTAREA': None, 'DSTBFU': None, 'HARVCAT': None, 'SILVSYS': None}
        cursor = arcpy.da.SearchCursor(lyr,emf)

        # grab the first record and examine it
        example = cursor.next() # eg. (u'REGULAR', u'CC', 0.0, u'SP1')
        for index, value in enumerate(example):
            if type(value) in (str, unicode):
                sqldict[emf[index]] = " IN (NULL,' ') "
            elif type(value) in (int, float):
                sqldict[emf[index]] = " IN (NULL, 0) "
            else:
                sqldict[emf[index]] = " IS NULL "

        # create sql that selects records that are not all nulls
        newsql = 'NOT ('
        for fieldname, sql in sqldict.items():
            newsql += '"' + fieldname + '"' + sql + 'AND '
        newsql = newsql[:-4] # cut off the last "AND ".
        newsql += ')'

        # arcpy.AddMessage("SELECT * FROM %s WHERE %s"%(lyr, newsql))
        new_cursor = arcpy.da.SearchCursor(lyr,f,newsql)
        return new_cursor
    except:
        # arcpy.AddWarning("Failed to run create_cursor function on %s"%lyr)
        pass


def find_IdField(f, dataformat):
    """
    this function returns the name of the most suitable id field for that dataformat.
    if the data doesn't have its typical id field, it will look for some other id field.
    f is the list of all existing fields
    dataformat is either 'coverage', 'feature classes' or 'shapefile'
    """
    if dataformat == 'feature classes':
        if 'OBJECTID' in f:
            return 'OBJECTID'
        elif 'OBJECTID_1' in f:
            return 'OBJECTID_1'            
        elif 'FID' in f:
            return 'FID'
        else:
            return f[0]
    else:
        if 'FID' in f:
            return 'FID'
        elif 'FID_1' in f:
            return 'FID_1'              
        elif 'OBJECTID' in f:
            return 'OBJECTID'            
        else:
            return f[0]


def getOntarioLogo():
    """
    this function should test if this ontario logo works before returning it
    However, urllib2.urlopen module doesn't seem to work on OPS network.
    """
    return 'https://www.ontario.ca/img/logo-ontario@2x.png'


def findDuplicateID(idList, idfieldname):
    """
    you must first check if the idList is not a blank list before using this function.
    This function will check the idList for any duplicates.
    It will then output the duplicate ID in a string format.
    """
    unique_id_list = []
    duplicate_id_list = []
    duplicate_counter = 0
    for i in idList:
        if i in unique_id_list:
            duplicate_id_list.append(i)
            duplicate_counter += 1
        else:
            unique_id_list.append(i)

    summary_msg = ''
    error_msg_list = []
    if duplicate_counter == 0:
        pass # the length of both summary_msg and error_msg_list stays zero.
    else:
        duplicates = set(duplicate_id_list)
        msg1 = "Error on %s record(s): The %s attribute must contain a unique value."%(duplicate_counter,idfieldname)
        summary_msg += msg1
        error_msg_list.append(msg1)
        error_msg_list.append('List of duplicate %s:'%idfieldname)
        error_msg_list.append(str(list(duplicates)))

    return summary_msg, error_msg_list




if __name__ == '__main__':

    # # testing findDuplicateID
    # idlist = [0,1,2,3,3,4,5,6,7,7,8,9,14,3,7,0,'','',None, None, None, 'abc','abc',999, 999,]
    # idfieldname = 'POLYID'
    # summary, error_list = findDuplicateID(idlist,idfieldname)
    # print(summary)
    # print(error_list)

    for k, v in static_db.items():
        print('%s, %s'%(k,v[0]))


    # findPDF('FIM_AWS_TechSpec_2017.pdf#page=50')

##    htmlstring = checkWatchFile(r'N:\WORK-DATA\FMPDS\Timiskaming\AWS\2017')
##    rep = open(r'N:\WORK-DATA\FMPDS\Timiskaming\AWS\2017\E00\mu280_aws_review_summary.html','w')
##    try:
##        rep.write(htmlstring)
##        rep.close()
##    except:
##        pass

##    for i in ['Cw  70La  20Sb  10','Pt 50Bf  30Bw  10Sb  10','Sb  40La  60','Pt  40Bw  40Sb  20Pb  10','']:
##        print spcVal(i, 'OSPCOMP')
##
##
##
##    errorList = []
##    warningList = []
##    for row in ['Cw  70La  20Sb  10','Pt 50Bf  30Bw  10Sb  10','Sb  40La  60','Pt  40Bw  40Sb  20Pb  10','']:
##        if row not in [None,'']:
##            check = spcVal(row,"OSPCOMP")
##            if check is None: ## when no error found
##                pass
##            elif check[0] == "Error":
##                errorList.append("%s on OBJECTID: %s"%(check[0],check[1]))
##            elif check[0] == "Warning":
##                warningList.append("%s on OBJECTID: %s"%(check[0],check[1]))
##
##
##    errorList = [['Warning on OBJECTID 195286: FORMOD attribute should be PF when OSC equals 4.',
##             'Warning on OBJECTID 195201: FORMOD attribute should be PF when OSC equals 4.',
##             'Warning on OBJECTID 195202: FORMOD attribute should be PF when OSC equals 4.',
##             'Warning on OBJECTID 195203: FORMOD attribute should be PF when OSC equals 4.',
##             'Warning on OBJECTID 195204: FORMOD attribute should be PF when OSC equals 4.',
##             'Warning on OBJECTID 195205: FORMOD attribute should be PF when OSC equals 4.',
##             'Warning on OBJECTID 195206: FORMOD attribute should be PF when OSC equals 4.',
##             'Warning on OBJECTID 195207: FORMOD attribute should be PF when OSC equals 4.',
##             'Warning on OBJECTID 195208: FORMOD attribute should be PF when OSC equals 4.'],
##             ['Warning on OBJECTID 802: DEVSTAGE should be LOWMGMT, LOWNAT, DEPHARV or DEPNAT if POLYTYPE = FOR and if UCCLO + OCCLO < 25.',
##             'Warning on OBJECTID 803: DEVSTAGE should be LOWMGMT, LOWNAT, DEPHARV or DEPNAT if POLYTYPE = FOR and if UCCLO + OCCLO < 25.',
##             'Warning on OBJECTID 806: DEVSTAGE should be LOWMGMT, LOWNAT, DEPHARV or DEPNAT if POLYTYPE = FOR and if UCCLO + OCCLO < 25.',
##             'Warning on OBJECTID 807: DEVSTAGE should be LOWMGMT, LOWNAT, DEPHARV or DEPNAT if POLYTYPE = FOR and if UCCLO + OCCLO < 25.',
##             'Warning on OBJECTID 808: DEVSTAGE should be LOWMGMT, LOWNAT, DEPHARV or DEPNAT if POLYTYPE = FOR and if UCCLO + OCCLO < 25.',
##             'Warning on OBJECTID 800: DEVSTAGE should be LOWMGMT, LOWNAT, DEPHARV or DEPNAT if POLYTYPE = FOR and if UCCLO + OCCLO < 25.']]
##
##    print sortError(errorList,2)

    # print(ecoVal('B065TtD n',"PRI_ECO"))
    # print(ecoVal('B065',"PRI_ECO"))
    # print(ecoVal('B65TtD n',"PRI_ECO"))
    # print(ecoVal('B365TtD n',"PRI_ECO"))
    # print(ecoVal('B999TtDn',"PRI_ECO"))
    # print(ecoVal('B06',"PRI_ECO"))


# Testing findLeadSpc function:
    # s1 = 'PR  80PW  20'
    # s2 = 'ab  70or  29'
    # s3 = ''
    # s4 = None
    # s5 = 'pj'
    # s6 = 'PR  20PW  80'
    # s7 = 'PR  40PW  40BW  20' # tie
    # for i in [s1,s2,s3,s4,s5,s6,s7]:
    #     print(findLeadSpc(i))


