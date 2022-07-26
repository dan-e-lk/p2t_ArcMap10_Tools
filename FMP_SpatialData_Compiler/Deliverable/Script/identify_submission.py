

# submissionLookUp = {'FMP': 	['ERU', 'FDP', 'PCI', 'PAG', 'PCC', 'AOC', 'PRC', 'BMI', 'PRT', 'PRP', 'PHR', 'ORB', 'OPI'],
# 			'AR': 	['SIP', 'RDS', 'AGG', 'NDB', 'TND', 'FTG', 'RGN', 'HRV', 'WTX', 'SGR', 'PRT', 'SCT'],
# 			'AWS':	['SRC', 'SHR', 'SRA', 'SRG', 'SAG', 'SWC', 'STT', 'SRP', 'AGP', 'SAC', 'SPT', 'SSP', 'SOR', 'SEA']}

fmuLookUp = {
#           fmu                     code        plan start years    region
        'Abitibi_River':        [   '110',      [2012, 2022],       'NE'    ],
        'Algoma':               [   '615',      [2010, 2020],       'NE'    ],
        'Algonquin_Park':       [   '451',      [2010, 2020],       'S'     ],
        'Armstrong':            [   '444',      [2005],             ''      ], #outdated?
        'Bancroft_Minden':      [   '220',      [2011, 2021],       'S'     ],
        'Big_Pic':              [   '067',      [2007, 2017],       'NE'    ], # will be a part of Pic_Forest in 2019
        'Black_River':          [   '370',      [2006],             ''      ], #outdated?
        'Black_Spruce':         [   '035',      [2011, 2021],       'NW'    ],
        'Caribou':              [   '175',      [2008, 2018],       'NW'    ],
        'Crossroute':           [   '405',      [2007, 2017],       'NW'    ],
        'Dog_River_Matawin':    [   '177',      [2009, 2019],       'NW'    ],
        'Dryden':               [   '535',      [2011, 2021],       'NW'    ],
        'English_River':        [   '230',      [2009, 2019],       'NW'    ],
        'French_Severn':        [   '360',      [2009, 2019],       'S'     ],
        'Gordon_Cosens':        [   '438',      [2010, 2020],       'NE'    ],
        'Hearst':               [   '601',      [2007, 2017],       'NE'    ],
        'Kenogami':             [   '350',      [2011, 2021],       'NW'    ],
        'Kenora':               [   '644',      [2012, 2022],       'NW'    ],
        'Lac_Seul':             [   '702',      [2011, 2021],       'NW'    ],
        'Lake_Nipigon':         [   '815',      [2011, 2021],       'NW'    ],
        'Lakehead':             [   '796',      [2007, 2017],       'NW'    ],
        'Magpie':               [   '565',      [2009, 2019],       'NE'    ],
        'Missinaibi':           [   '574',      [2021],             'NE'    ],        
        'Martel':               [   '509',      [2011, 2021],       'NE'    ],
        'Mazinaw_Lanark':       [   '140',      [2011, 2021],       'S'     ],
        'Nagagami':             [   '390',      [2011, 2021],       'NE'    ],
        'Nipissing':            [   '754',      [2009, 2019],       'NE'    ],
        'Northshore':           [   '680',      [2010, 2020],       'NE'    ],
        'Ogoki':                [   '415',      [2008, 2018],       'NW'    ],
        'Ottawa_Valley':        [   '780',      [2011, 2021],       'S'     ],
        'Pic_Forest':           [   '966',      [2019],             'NE'    ], # Amalgamation of Big_Pic and Pic_River as of 2019 plan
        'Pic_River':            [   '965',      [2006, 2013],       'NE'    ], # will be a part of Pic_Forest in 2019
        'Pineland':             [   '421',      [2011, 2021],       'NW'    ],
        'Red_Lake':             [   '840',      [2008, 2018],       'NW'    ],
        'Romeo_Malette':        [   '930',      [2009, 2019],       'NE'    ],
        'Sapawe':               [   '853',      [2010, 2020],       'NW'    ],
        'Spanish':              [   '210',      [2010, 2020],       'NE'    ],
        'Sudbury':              [   '889',      [2010, 2020],       'NE'    ],
        'Temagami':             [   '898',      [2009, 2019],       'NE'    ],
        'Timiskaming':          [   '280',      [2011, 2021],       'NE'    ],
        'Trout_Lake':           [   '120',      [2009, 2019],       'NW'    ],
        'Wabigoon':             [   '130',      [2008, 2018],       'NW'    ],
        'Whiskey_Jack':         [   '490',      [2012, 2022],       'NW'    ],
        'White_River':          [   '060',      [2008, 2018],       'NE'    ],
        'Whitefeather':         [   '994',      [2012, 2022],       'NW'    ]
        }


def identifySubmission(file_fullpath):

        import re, os

        filename = os.path.split(file_fullpath)[1]
        inv_type = 'unknown'
        fmuCode = 'unknown'
        fmuName = 'unknown' # same as inv_name
        inv_year = 'unknown'
        sub_id = 'unknown'

        regEx = re.compile(r"""MU(\d\d\d)_(\d\d)(\D\D\D)""") # this will catch string such as 'MU966_2019_BMI'

        mo = regEx.search(filename.upper())
        if mo != None:
                fmuCode = mo.group(1) # '966'
                inv_year = mo.group(2) # '08'
                inv_type = mo.group(3) # 'BMI'

        if int(inv_year) > 70:
                inv_year = '19' + inv_year
        else:
                inv_year = '20' + inv_year                

        # finding fmuName from fmuCode
        for k,v in fmuLookUp.items():
                if v[0] == fmuCode:
                        fmuName = k
                        break

        # inv_type, fmuCode, fmuName, inv_year must be identified - raise error if it wasn't identified.
        if inv_type == 'unknown' or fmuCode == 'unknown' or fmuName == 'unknown' or inv_year == 'unknown':
                raise Exception("The filename must contain 'MU<fmucode>_<year><layername>'. The following input filename is invalid:\n%s\nThis error also occur if the tool can't recognize the FMU code."%file_fullpath)


        # to look for submission id, we need to find the 'fi_submission_99999.txt' file two folder levels up from the file
        directory = os.path.dirname(os.path.dirname(os.path.dirname(file_fullpath)))
        files = os.listdir(directory)
        # in the directory, if there's a file that starts with 'fi_sub' and contains 5 consecutive number, that number is assigned to our sub_id.
        for f in files:
                if 'FI_SUB' in f.upper():
                        try:
                                search_result = re.search(r'\d{5}',f) # searching for consecutive 5 digit number
                                sub_id = search_result.group(0)
                                break
                        except:
                                pass

        result = {
                "inv_name": fmuName,
                "inv_descr": "",
                "path": file_fullpath,
                "inv_type": inv_type,
                "inv_year": inv_year,
                "sub_id": sub_id
                }


        return result
        # result look like {'inv_type': 'HRV', 'inv_name': 'Nagagami', 'sub_id': '22693', 'inv_descr': '', 'inv_year': '2016', 'path': 'N:\\WORK-DATA\\FMPDS\\Nagagami\\AR\\2016\\_data\\FMP_Schema.gdb\\mu390_16hrv00'}



if __name__ == '__main__':
        result = identifySubmission(r'N:\WORK-DATA\FMPDS\Nagagami\AR\2016\_data\FMP_Schema.gdb\mu390_16hrv00')
        print result