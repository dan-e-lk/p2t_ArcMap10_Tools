version = "1"
debug = False

import Reference as R # Reference.py should be located in the same folder as this file.
import arcpy, os, csv
from messages import print2
from messages import output
from datetime import datetime

##########    settings    #############

fec_ecosite_fieldname = 'FEC_ECO_NUM' # change the fieldname if you want
fec_ecosite_desc_fieldname = 'FEC_ECO_DESC'
spcompy_fname = 'SPCOMPy' # this field will be created to store parsed SPCOMP values
# example of spcompy value: {'BD': 0, 'BE': 10, 'BF': 0, 'OC': 0, 'YB': 10, 'MH': 60, 'UKN': 0, 'AB': 0, 'HE': 0, 'PR': 0, 'PW': 0, 'PT': 20, 'LA': 0, 'PB': 0, 'PJ': 0, 'PO': 0, 'PL': 0, 'CH': 0, 'SPC_Check': 'Pass', 'IW': 0, 'CE': 0, 'AW': 0, 'QR': 0, 'OH': 0, 'SW': 0, 'OB': 0, 'BW': 0, 'HI': 0, 'MR': 0, 'OW': 0, 'SB': 0, 'EX': 0}

# use these csv files (must be saved in the same folder as this script)
tbl_spp = "tbl_spp_fec_eco_use_only.csv" # must have two fields: 'spc' and 'spc_simp'
coeff = "coeff_ecosite_GLSL.csv"
fec_code = "FEC_Code.csv"
unknown_spc_code = 'UKN'

#######################################


def spParse2(inputfc,spcompfield, msg):

    # make sure the fc has the necessary fields
    msg += print2("Checking your input data...")
    mand_fields = ['POLYTYPE'] # add more if needed
    mand_fields.append(spcompfield)
    existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
    for fname in mand_fields:
        if fname not in existingFields:
            msg += print2("%s field not found!"%spcompfield, 'error')

    # load tbl_spp csv file in memory in the format of "list of dictionaries"
    msg += print2("Loading %s..."%tbl_spp)
    parent_folder = os.path.split(__file__)[0]
    l_tbl_spp = list(csv.DictReader(open(os.path.join(parent_folder,tbl_spp))))
    # eg. [{'spc_desc': 'ash, black', 'spc': 'Ab', 'spc_simp': 'AB'}, {'spc_desc': 'mountain-ash, any/mix', 'spc': 'Am', 'spc_simp': 'OH'}, ... ]
    # need this in dictionary format
    d_tbl_spp = {i['spc'].upper():i['spc_simp'].upper() for i in l_tbl_spp} # eg. {'BD': 'BD',... 'BG': 'BW', 'WB': 'OH', 'BB': 'OH',...}
    if debug:
        for row in l_tbl_spp:
            msg += print2(str(row))
    msg += print2("Species code will be simplified based on this:")
    msg += print2(str(d_tbl_spp))


    # generate spcompy
    spcompy = {spc:0 for spc in set(d_tbl_spp.values())} # eg. {'BD': 0, 'BE': 0, 'BF': 0, ...}
    msg += print2("\nFull list of simplified species codes:")
    msg += print2(str(sorted(spcompy.keys()))) # ['AB', 'AW', 'BD', 'BE', 'BF', 'BW', 'CE', 'CH', 'EX', 'HE', 'HI', 'IW', 'LA', 'MH', 'MR', 'OB', 'OC', 'OH', 'OW', 'PB', 'PJ', 'PL', 'PO', 'PR', 'PT', 'PW', 'QR', 'SB', 'SW', 'YB']
    # add other useful fields
    spcompy['SPC_Check'] = ''
    spcompy[unknown_spc_code] = 0

    # create a new field to store spcompy
    msg += print2("\nCreating a new field: %s"%spcompy_fname)
    arcpy.AddField_management(in_table = inputfc, field_name = spcompy_fname, field_type = "TEXT", field_length=1000)
    mand_fields.append(spcompy_fname)


    # Examining the SPCOMP field and filling out the spcompy dictionary
    SppOccurSet = set()    ## Create a set to contain a unique list of species with occurances in the inventory.
    SppOccurSet_simp = set() # unique list of species occurance but the simple version
    SppOccurDict = dict()   ## Create a dictionary to contain a count of the species occurances in the inventory.
    SppOccurDict_simp = dict()   ## Ccontain a count of the species occurances in the inventory, but using the simpler species code
    sppErrorCount = 0  ## If the spcomp value is invalid, count them.
    recordCount = 0 ## just to count the number of records
    spcompPopulCount = 0  ## number of records with spcomp value populated.
    unknown_spc_lst = [] # when the species code cannot be found in tbl_spp.csv, it's added here

    msg += print2("\nPopulating %s field..."%spcompy_fname)
    f = mand_fields
    with arcpy.da.UpdateCursor(inputfc, mand_fields, "POLYTYPE='FOR'") as cursor:
        for row in cursor:
            recordCount += 1
            row_spcompy = spcompy.copy()

            if row[f.index(spcompfield)] not in [None, '', ' ']: ## if SPCOMP field is none, the spcVal function won't work
                spcompPopulCount += 1
                ValResult = R.spcVal(row[f.index(spcompfield)],spcompfield) ## ValResult example: ["Pass", {'AX':60,'CW':40}]
            
                if ValResult[0] != "Error":
                    for k, v in ValResult[1].items(): # ValResult example: {'AX':60,'CW':40}
                        k = str(k) # eg. 'AX'
                        try:
                            spc_simp = d_tbl_spp[k]
                        except KeyError(): # this happens if a rare spc code exists in SPCOMP value but it doesn't exist on the tbl_spp.csv
                            spc_simp = unknown_spc_code
                            unknown_spc_lst.append(k) # when the species code cannot be found in tbl_spp.csv, it's added here
                        row_spcompy[spc_simp] += v # for example, k = 'AX' and v = 60, then it will be added to spcompy['AW'] because 'AX':'AW' according to the d_tbl_spp

                        SppOccurSet.add(k)         ## Once the species code and value 'passes' add that species to the species occurance list.
                        SppOccurSet_simp.add(spc_simp)

                        # just for reporting
                        if SppOccurDict.has_key(k) == True:
                            SppOccurDict[k] += 1    ## Once the species code and value 'passes; add that species to the speciec orrurance list and increment count by one.
                        else:
                            SppOccurDict[k] = 1
                        if SppOccurDict_simp.has_key(spc_simp) == True:
                            SppOccurDict_simp[spc_simp] += 1    ## Once the species code and value 'passes; add that species to the speciec orrurance list and increment count by one.
                        else:
                            SppOccurDict_simp[spc_simp] = 1

                    row_spcompy['SPC_Check'] = "Pass"

                else:
                    sppErrorCount += 1
                    row_spcompy['SPC_Check'] = "%s: %s"%(str(ValResult[0]), str(ValResult[1]))

            # write it to SPCOMPY field
            row[f.index(spcompy_fname)] = str(row_spcompy)
            cursor.updateRow(row)

    # list of species with occurrences
    SppOccurList = list(SppOccurSet)
    SppOccurList.sort()
    msg += print2("\n%s species with occurrences in the inventory:\n%s" %(spcompfield,SppOccurList))   ## Print the unique list of species with occurrences in the inventory.

    # Simplified list of species with occurrences
    SppOccurList_simp = list(SppOccurSet_simp)
    SppOccurList_simp.sort()
    msg += print2("\nSimplified species with occurrences in the inventory:\n%s" %(SppOccurList_simp))   ## Print the unique list of species with occurrences in the inventory.

    # table of spc and its occurrences
    if len(SppOccurDict) > 0:
        SppOccrCsv = '%s Species,Occurences'%spcompfield
        for spc, occ in sorted(SppOccurDict.items(), key=lambda (k,v): (v,k), reverse=True): # sort by the order of most commonly occurred to least.
            SppOccrCsv += '\n' + spc + ',' + str(occ)
        SppOccrCsv += '\n'
        msg += print2("\nThe list of species with occurrences in the inventory:\n%s" %SppOccrCsv)   ## Print the table of species and occurrences in the inventory.

    # table of spc and its occurrences
    if len(SppOccurDict_simp) > 0:
        SppOccrCsv = 'Simplified Species,Occurences'
        for spc, occ in sorted(SppOccurDict_simp.items(), key=lambda (k,v): (v,k), reverse=True): # sort by the order of most commonly occurred to least.
            SppOccrCsv += '\n' + spc + ',' + str(occ)
        SppOccrCsv += '\n'
        msg += print2("\nThe list of simplified species with occurrences in the inventory:\n%s" %SppOccrCsv)   ## Print the table of species and occurrences in the inventory.

    # Report errors
    msg += print2("Total Number of Records (POLYTYPE='FOR'): %s"%recordCount)
    msg += print2("Number of records with %s populated: %s"%(spcompfield,spcompPopulCount))
    if sppErrorCount > 0:
        msg += print2("Number of errors found in %s field: %s"%(spcompfield,sppErrorCount),  msgtype = 'warning')
    if len(unknown_spc_lst) >0:
        msg += print2("The following species code were not found in %s:"%tbl_spp, msgtype = 'warning')
        msg += print2(str(set(unknown_spc_lst)), msgtype = 'warning')

    # Mark end time
    endtime = datetime.now()
    msg += print2('End of process: %(end)s.' %{'end':endtime.strftime('%Y-%m-%d %H:%M:%S')})
    msg += print2('Duration of process: %(duration)s seconds.\n' %{'duration':(endtime - starttime).total_seconds()})

    return msg







# calculating fec ecosite numbers and finding the max value
def fec_ecosite(inputfc, msg):
    # this function requires SPCOMPy field populated with parsed simplified species code

    # need something here to check if SC field exists

    # grab coefficients and fec codes
    parent_folder = os.path.split(__file__)[0]
    msg += print2("Loading %s..."%coeff)
    l_coeff = list(csv.DictReader(open(os.path.join(parent_folder,coeff))))
    msg += print2("Loading %s..."%fec_code)
    l_fec_code = list(csv.DictReader(open(os.path.join(parent_folder,fec_code))))

    # create a new fields to store FEC_VAR, FEC_PROB_SUM, FEC_CODE, FEC_NAME
    new_fields = {
    'FEC_VAR':      ['TEXT',1000],
    'FEC_PROB_SUM': ['TEXT',1000],
    'FEC_CODE':     ['TEXT', 10],
    'FEC_NAME':     ['TEXT', 10]
    }
    for fname, detail in new_fields.items():
        msg += print2("\nCreating a new field: %s"%fname)
        ftype = detail[0]
        flength = detail[1]
        arcpy.AddField_management(in_table = inputfc, field_name = fname, field_type = ftype, field_length=flength)

    # calculate FEC_VAR (K0 to K30)
    fec_var_dict = {'K%s'%i:0 for i in range(31)} #eg. {'K0':0, 'K1':0, ... 'K30':0}
    fec_var_dict['K0']=1
    # f = [spcompy_fname, 'FEC_VAR','FEC_PROB_SUM','FEC_CODE','FEC_NAME']
    f = [spcompy_fname, 'FEC_VAR', 'SC']
    with arcpy.da.UpdateCursor(inputfc, f, "POLYTYPE='FOR'") as cursor:
        for row in cursor:
            spcompy = eval(row[0])
            fvar = fec_var_dict.copy()

            fvar['K1'] = round(spcompy['MH']**0.5, 4)
            fvar['K2'] = round(spcompy['YB']**0.5, 4)
            fvar['K3'] = round(spcompy['BE']**0.5, 4)
            fvar['K4'] = round(spcompy['QR']**0.5, 4)
            fvar['K5'] = round(spcompy['MS']**0.5, 4)
            fvar['K6'] = round(spcompy['BD']**0.5, 4)
            fvar['K7'] = round((spcompy['AW']+spcompy['CH'])**0.5, 4)
            fvar['K8'] = round(spcompy['IW']**0.5, 4)
            fvar['K9'] = round(spcompy['IW']**0.5, 4)



            # update and commit FEC_VAR field
            row[1] = str(fvar)
            cursor.updateRow(row)




    return msg







if __name__ == '__main__':
    inputfc = arcpy.GetParameterAsText(0) # this should be bmi or pci - this tool adds fields to input fc
    spcompfield = arcpy.GetParameterAsText(1).upper() # almost always 'SPCOMP'

    global starttime
    starttime = datetime.now()
    msg = print2('Start of process: %(start)s.' %{'start':starttime.strftime('%Y-%m-%d %H:%M:%S')})

    ##### PART 1 - SPCOMP Parser
    # if you just run this function below, all you do is creating SPCOMPY field and populating with parsed spc info
    msg = spParse2(inputfc,spcompfield,msg) 


    ##### PART 2 - FEC ECOSITE
    msg = fec_ecosite(inputfc, msg)


    ##### PART 3 - Write 'msg' into the log txt file
    ## Create the output path, considering whether or not the feature class is in a file geodatabase folder or not.
    ## folder path contining the workspace
    folder_path = arcpy.Describe(inputfc).path
    while arcpy.Describe(folder_path).dataType != 'Folder':
        folder_path = os.path.split(folder_path)[0]

    ## Create the output file name for the log
    outfile = os.path.split(inputfc)[1] + '_SPC2-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'

    # Create the log file.
    output(folder_path, outfile, msg)