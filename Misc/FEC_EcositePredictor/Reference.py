
SpcListInterp = ['AX', 'AB', 'AW', 'PL', 'PT', 'BD', 'BE', 'BG', 'BW', 'BY', 'BN', 'CE', 'CR', 'CW', 'CH', 'CB', 'CD', 'OC', 'PD', 'EX', 'EW', 'BF', 'OH', 'HE', 'HI', 'IW', 'LO', 'MX', 'MH', 'MR', 'MS', 'OX', 'OR', 'OW', 'PX', 'PJ', 'PR', 'PS', 'PW', 'PO', 'PB', 'SX', 'SB', 'SW', 'LA', 'WB', 'WI']

SpcListOther = ['AL', 'AQ', 'AP', 'AG', 'BC', 'BP', 'GB', 'BB', 'CAT', 'CC', 'CM', 'CP', 'CS', 'CT', 'ER', 'EU', 'HK', 'HL', 'HB', 'HM', 'HP', 'HS', 'HC', 'KK', 'LE', 'LJ', 'BL', 'LL', 'LB', 'GT', 'MB', 'MF', 'MM', 'MT', 'MN', 'MP', 'AM', 'EMA', 'MO', 'OBL', 'OB', 'OCH', 'OP', 'OS', 'OSW', 'PA', 'PN', 'PP', 'PC', 'PH', 'PE', 'RED', 'SC', 'SS', 'SK', 'SN', 'SR', 'SY', 'TP', 'HAZ']

def spcVal(data, fieldname, version = 2017): #sample data: 'Cw  70La  20Sb  10'
    #assuming the data is not None or empty string
    try:
        if len(data)%6 == 0:
            n = len(data)/6
            spcList = [data[6*i:6*i+3].strip().upper() for i in range(n)]
            percentList = [int(data[6*i+3:6*i+6].strip()) for i in range(n)]
            # build species to percent dictionary
            spcPercentDict = dict(zip(spcList,percentList)) # this should look like {'AX':60,'CW':40}

            if sum(percentList) == 100:
                if len(set(spcList)) == len(spcList):

                    correctList = list(set(spcList)&set(SpcListInterp))
                    # To save processing time, check the spc code with the most common spc list (SpcListInterp) first, if not found, check the other possible spc code
                    if len(correctList) != len(spcList):
                        correctList = list(set(spcList)&set(SpcListInterp + SpcListOther))

                    if len(correctList) == len(spcList):
                        return ['Pass',spcPercentDict]
                    else:
                        wrongList = list(set(spcList) - set(correctList))
                        return ["Error","%s has invalid species code(s): %s"%(fieldname,wrongList)]
                else:
                    return ["Error","%s has duplicate species codes"%fieldname]
            else:
                return ["Error","%s does not add up to 100"%fieldname]
        else:
            return ["Error", "%s does not follow the SSSPPPSSSPPP patern"%fieldname]
    except:
        return ["Error", "%s does not follow the SSSPPPSSSPPP patern"%fieldname]



# def csv_to_dict(in_csv):
#     import csv
#     with open(in_csv) as csvfile:
#         dict_lst = csv.DictReader(csvfile)
#     # returns list of dictionaries such as [{'first_name': 'John', 'last_name': 'Cleese'}, {{'first_name': 'Daniel', 'last_name': 'Kim'},...]
#     return dict_lst



if __name__ == '__main__':
    spcomp = "CW  70SB  20LA  10"
    print (spcVal(spcomp,"SPCOMP"))


    completeSpList = SpcListInterp + SpcListOther # this is our complete species list.
    completeSpList.sort()
    print(completeSpList)