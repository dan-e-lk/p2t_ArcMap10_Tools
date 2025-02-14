# Developed by Daniel Kim and Glen Watt on Dec 2024.
# Glen has run rigorous testing 
# This tool is based on FEC_EcositePredictor.xlsx (included in reference folder) which is based on OWHAMTool which has its root in
#   1997 Field Guide to Forest Ecosystems of Central Ontario (included in reference folder)
# By using this tool we can ensure the FEC CODE values (ecosite values 11-35 from Central Ontario FEC Manual) that relates 
#   to the Old Growth Definition Report (older policy) can be assigned with confidence to our inventory products to support the old growth project.
# This will allow you to query forest stands for potential old growth eligibility based on predicted ecosite values in any inventory product/vintage (old or T1).


version = "202502"

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

            # sort (only works on python >3.7)
            try:
                row_spompy_sorted = dict(sorted(row_spcompy.items()))
                row_spcompy = row_spompy_sorted
            except:
                pass
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

    # # Mark end time
    # endtime = datetime.now()
    # msg += print2('End of process: %(end)s.' %{'end':endtime.strftime('%Y-%m-%d %H:%M:%S')})
    # msg += print2('Duration of process: %(duration)s seconds.\n' %{'duration':(endtime - starttime).total_seconds()})

    return msg







# calculating fec ecosite numbers and finding the max value
def fec_ecosite(inputfc, SCfield, msg):
    # this function requires SPCOMPy field populated with parsed simplified species code

    # need something here to check if SC field exists

    # grab coefficients and fec codes
    parent_folder = os.path.split(__file__)[0]
    msg += print2("Loading %s..."%coeff)
    l_coeff = list(csv.DictReader(open(os.path.join(parent_folder,coeff))))
    coeff_dict = {i['Ecosite_Num']:i for i in l_coeff}

    msg += print2("Loading %s..."%fec_code)
    l_fec_code = list(csv.DictReader(open(os.path.join(parent_folder,fec_code))))
    fec_code_dict = {i['HU']:i['HU_NAME'] for i in l_fec_code}

    if debug:
        msg += print2("\n\ncoeff_dict:\n%s"%coeff_dict)
        msg += print2("fec_code_dict:\n%s\n\n"%fec_code_dict)

    # create a new fields to store FEC_VAR, FEC_PROB_SUM, FEC_CODE, FEC_NAME
    new_fields = {
    'FEC_CODE':     ['TEXT', 10, True],
    'FEC_NAME':     ['TEXT', 10, True]
    }
    for fname, detail in new_fields.items():
        msg += print2("\nCreating a new field: %s"%fname)
        ftype = detail[0]
        flength = detail[1]
        arcpy.AddField_management(in_table = inputfc, field_name = fname, field_type = ftype, field_length=flength)


    # calculate FEC_VAR (K0 to K30)
    msg += print2("\nCalculating K0 to K30 for each record...")
    fec_var_dict = {'K%s'%i:0 for i in range(31)} #eg. {'K0':0, 'K1':0, ... 'K30':0}
    fec_var_dict['K0']=1 # because K0 is always 1.
    fec_var_tbl = {} # dictionary of dictionary where key is the oid and value is the fec_var_dict filled out
    oid_fieldname = arcpy.Describe(inputfc).OIDFieldName
    f = [spcompy_fname, SCfield, oid_fieldname]
    with arcpy.da.SearchCursor(inputfc, f, "POLYTYPE='FOR' AND %s IS NOT NULL"%SCfield) as cursor:
        for row in cursor:
            s = eval(row[0]) #spcompy dictionary
            site_cls = row[1]
            oid = row[-1]
            fvar = fec_var_dict.copy()
            try:
                # groupings
                TolHrwd = s['MH']+s['YB']+s['BE']
                OtherHrwd = s['QR']+s['OW']+s['OB']+s['MS']+s['BD']+s['CH']+s['AW']+s['AB']+s['IW']+s['EW']+s['OH']
                IntHrwd = s['PO']+s['BW']
                Conifer = s['PW']+s['PR']+s['PJ']+s['SW']+s['SB']+s['BF']+s['HE']+s['CE']+s['LA']+s['OC']
                Oak = s['QR']+s['OW']+s['OB']

                # calculating Kn values
                fvar['K1'] = round(s['MH']**0.5, 4)
                fvar['K2'] = round(s['YB']**0.5, 4)
                fvar['K3'] = round(s['BE']**0.5, 4)
                fvar['K4'] = round(Oak**0.5, 4)
                fvar['K5'] = round(s['MS']**0.5, 4)
                fvar['K6'] = round(s['BD']**0.5, 4)
                fvar['K7'] = round((s['AW']+s['CH'])**0.5, 4)
                fvar['K8'] = round(s['IW']**0.5, 4)
                fvar['K9'] = round(s['PO']**0.5, 4)
                fvar['K10'] = round(s['BW']**0.5, 4)
                if s['PW']<30 and s['PR']<20 and s['PJ']<20 and Oak<20 and s['BE']<20 and s['IW']<20:
                    fvar['K11'] = round((s['AB']+s['EW'])**0.5, 4)
                fvar['K12'] = round(s['PW']**0.5, 4)
                fvar['K13'] = round(s['PR']**0.5, 4)
                fvar['K14'] = round(s['PJ']**0.5, 4)
                fvar['K15'] = round(s['SW']**0.5, 4)
                fvar['K16'] = round(s['BF']**0.5, 4)
                fvar['K17'] = round(s['SB']**0.5, 4)
                fvar['K18'] = round(s['HE']**0.5, 4)
                fvar['K19'] = round(s['CE']**0.5, 4)
                if not (s['PW']>10 or s['PR']>10 or s['PJ']>10 or Oak>10 or s['BE']>10 or s['IW']>10):
                    fvar['K20'] = round(s['LA']**0.5, 4)
                fvar['K21'] = round(TolHrwd**0.5, 4)
                fvar['K22'] = round(OtherHrwd**0.5, 4)
                fvar['K23'] = round(IntHrwd**0.5, 4)
                fvar['K24'] = round(Conifer**0.5, 4)
                if s['PR']>=50:
                    fvar['K25'] = 1
                # if PW+PR+PJ>=30 and PJ<75 and PR<50 and ((PW>0 and PJ>0) or (PR>0 and PJ>0)): # this can be simplified to...
                # if PW+PR+PJ>=30 and PR<50 and 0<PJ<75 and (PW>0 or PR>0):
                # if s['PW']+s['PR']+s['PJ']>=30 and s['PR']<50 and 0<s['PJ']<75 and (s['PW']>0 or s['PR']>0): # simplified version
                if s['PW']+s['PR']+s['PJ']>=30 and s['PJ']<75 and s['PR']<50 and ((s['PW']>0 and s['PJ']>0) or (s['PR']>0 and s['PJ']>0)): # original version
                    fvar['K26'] = 1
                if s['PW']+s['PR']+s['PJ']>10 and s['PO']>0 and Oak>0 and TolHrwd+OtherHrwd-Oak<=10:
                    fvar['K27'] = 1
                if s['PO']+s['BW']+s['MS']>=50 and s['MH']<50 and Conifer<50:
                    fvar['K28'] = 1
                if Oak>0 and s['MH']>0 and s['PW']<20 and s['PR']==0 and s['PJ']==0 and s['BE']<=10 and s['BD']<10 and IntHrwd >= TolHrwd:
                    fvar['K29'] = 1
                if site_cls < 1:
                    site_cls = 1
                elif site_cls > 3:
                    site_cls = 3
                fvar['K30'] = site_cls

                fec_var_tbl[oid] = fvar

                # sort (only works on python >3.7)
                try:
                    fvar_sorted = dict(sorted(fvar.items()))
                    fvar = fvar_sorted
                except:
                    pass

            except:
                msg += print2("ERROR while working on %s %s. Check the SPCOMP and %s"%(OIDFieldName,oid,tbl_spp),'error')
                raise


    # calculate FEC_PROB_SUM (11 to 35) and everything else
    msg += print2("\nCalculating FEC probability sum and the most probable FEC name..")
    fec_prob_dict = {str(i):0 for i in range(11,36)} #eg. {11:0, 12:0, ... 35:0}
    fec_prob_tbl = {} # debug use only - dictionary of dictionary where key is the oid and value is the fec_prob_dict filled out
    f = ['FEC_CODE','FEC_NAME', oid_fieldname]
    with arcpy.da.UpdateCursor(inputfc, f, "POLYTYPE='FOR'") as cursor:
        for row in cursor:
            oid = row[-1]
            fvar = fec_var_tbl[oid]
            fprob = fec_prob_dict.copy() # eg. {'11': 37.1975, '12': -361.5228, '13': 33.2090, ...}

            # multiplying values of FECVAR {'K0': 1, 'K1': 5.4772,...} with the fec coefficients
            for econum in fec_prob_dict.keys():
                for Kn, v in fvar.items():
                    fprob[econum] += v*float(coeff_dict[econum][Kn]) # eg. 1 * -199.05 for the K0 and econum 11

            # round up to 3 decimal - why 3? no particular reason...
            for econum, prob_sum in fprob.copy().items():
                fprob[econum] = round(prob_sum,3)

            # debug only
            fec_prob_tbl[oid] = fprob

            # find max value of fprob
            max_value = max(fprob.values())
            fec_code_econum = [econum for econum, prob_sum in fprob.items() if prob_sum == max_value][0]
            fec_name = fec_code_dict[fec_code_econum]

            # update and commit
            row[0] = fec_code_econum
            row[1] = fec_name
            cursor.updateRow(row)


    # in debug mode, we will write down the transitory k0-k30 values and the fec probability values to the data itself so we can check.
    if debug:
        msg += print2("\nDEBUG MODE: creating and populating FEC_VAR and FEC_PROB_SUM...")
        new_fields = {
        'FEC_VAR':     ['TEXT', 1000, True],
        'FEC_PROB_SUM':['TEXT', 1000, True]
        }
        for fname, detail in new_fields.items():
            ftype = detail[0]
            flength = detail[1]
            arcpy.AddField_management(in_table = inputfc, field_name = fname, field_type = ftype, field_length=flength)        

        f = ['FEC_VAR','FEC_PROB_SUM', oid_fieldname]
        with arcpy.da.UpdateCursor(inputfc, f, "POLYTYPE='FOR'") as cursor:
            for row in cursor:
                oid = row[-1]
                row[0] = str(fec_var_tbl[oid])
                row[1] = str(fec_prob_tbl[oid])
                cursor.updateRow(row)






    # Mark end time
    endtime = datetime.now()
    msg += print2('End of process: %(end)s.' %{'end':endtime.strftime('%Y-%m-%d %H:%M:%S')})
    msg += print2('Duration of process: %(duration)s seconds.\n' %{'duration':(endtime - starttime).total_seconds()})

    return msg







if __name__ == '__main__':
    inputfc = arcpy.GetParameterAsText(0) # this should be bmi or pci - this tool adds fields to input fc
    spcompfield = arcpy.GetParameterAsText(1).upper() # almost always 'SPCOMP'
    SCfield = arcpy.GetParameterAsText(2).upper() # almost always 'SC'
    debug_mode = arcpy.GetParameterAsText(3) # true or false

    global starttime
    starttime = datetime.now()
    msg = print2('Start of process: %(start)s.' %{'start':starttime.strftime('%Y-%m-%d %H:%M:%S')})

    global debug
    debug = False
    if debug_mode == 'true': debug = True

    ##### PART 1 - SPCOMP Parser
    # if you just run this function below, all you do is creating SPCOMPY field and populating with parsed spc info
    msg = spParse2(inputfc,spcompfield,msg) 


    ##### PART 2 - FEC ECOSITE
    msg = fec_ecosite(inputfc, SCfield, msg)


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