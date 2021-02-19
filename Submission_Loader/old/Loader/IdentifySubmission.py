from functions import print2
import os, re


submissionLookUp = {'FMP': 	['ERU', 'FDP', 'PCI', 'PAG', 'PCC', 'AOC', 'PRC', 'BMI', 'PRT', 'PRP', 'PHR', 'ORB', 'OPI'],
					'AR': 	['SIP', 'RDS', 'AGG', 'NDB', 'TND', 'FTG', 'RGN', 'HRV', 'WTX', 'SGR', 'PRT', 'SCT','EST','PER'],
					'AWS':	['SRC', 'SHR', 'SRA', 'SRG', 'SAG', 'SWC', 'STT', 'SRP', 'AGP', 'SAC', 'SPT', 'SSP', 'SOR', 'SEA']}

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



def identifySubmission(SubmissionFolder):
	""" This tool does not convert or move any files around. Instead, the tool examines the input folder 
		and returns information such as submision type, year and etc.
		The submission folder must be unzipped completely for this function to work.
		An example of SubmissionFolder is "C:\\FIPDownload\\download_cart_2018-01-08\\Product Submission - 23035" """

	# figuring out the geospatial file type and file names
	shpfileList = []
	e00fileList = []
	gdbList = []
	pdfList = []
	# otherfileList = []

	walker = os.walk(SubmissionFolder)
	for foldername, subfolders, filenames in walker:
		for filename in filenames:
			if filename.upper().endswith('.SHP'):
				shpfileList.append(os.path.join(foldername,filename))
			elif filename.upper().endswith('.E00'):
				e00fileList.append(os.path.join(foldername,filename))
			elif filename.upper().endswith('.PDF'):
				pdfList.append(os.path.join(foldername,filename))
		for subfolder in subfolders:
			if subfolder.upper().endswith('.GDB'):
				gdbList.append(os.path.join(foldername,subfolder))

	# in case there are folders such as LAYERS\MU390_AWS.gdb\MU390_AWS.gdb, delete the fake geodatabases.
	if len(gdbList)>0:
		import arcpy
		for gdb in gdbList:
			if arcpy.Describe(gdb).dataType != 'Workspace':
				gdbList.remove(gdb)

	# Determining Submission Type, fmu name, and submission year
	submType = 'unknown'
	fmuCode = 'unknown'
	fmuName = 'unknown'
	submYear = 'unknown'

	regEx = re.compile(r"""MU(\d\d\d)_(\d\d\d\d)_(AR|AWS|FMP|PCI|BMI|OPI|INV|FMPDP|FMPC|FMPDPC)""") # this will catch string such as 'MU966_2019_BMI'
	walker = os.walk(SubmissionFolder)	
	for foldername, subfolders, filenames in walker:
		for subfolder in subfolders:
			mo = regEx.search(subfolder.upper())
			if mo != None:
				fmuCode = mo.group(1) # '966'
				submYear = mo.group(2) # '2019'
				submType = mo.group(3) # 'BMI'
				break
		if submType != 'unknown':
			break

	# raise error if the script was unable to find the submType and etc.
	if submType == 'unknown' or fmuCode == 'unknown' or submYear == 'unknown':
		raise Exception("The script could not find Submission Type, FMU Code and/or Submission Year.\
						\nAt least one folder must have the structure 'MU000_0000_XYZ_LAYERS'")

	# PCI, BMI, OPI is really FMP submission
	if submType in ['PCI','BMI','OPI','INV','FMPDP','FMPC','FMPDPC']:
		submType = 'FMP'

	# determining spatial data file type (format)
	filetype = 'unknown'
	filelist = []	
	if len(gdbList) > 0:
		for gdb in gdbList:
			if gdb[-7:-4].upper() in submissionLookUp[submType] + ['AWS','FMP'] or gdb[-6:-4].upper() == 'AR' or gdb[-9:-4].upper() == 'FMPDP': # to catch MU123_28PCI.gdb, MU123_28AWS.gdb, MU123_28AR.gdb or MU123_2028_FMPDP.gdb
				filetype = 'gdb'
				filelist = gdbList
				break
			elif gdb[-10:-4].upper() == 'FMPDPC' or gdb[-8:-4].upper() == 'FMPC': # to catch contingency plans such as MU966_2019_FMPDPC.gdb
				filetype = 'gdb'
				filelist = gdbList				
				break
	if len(shpfileList) > 0:
		for shp in shpfileList:
			if shp[-9:-6].upper() in submissionLookUp[submType] or shp[-10:-7].upper() in submissionLookUp[submType]: # to catch MU123_28SHR00.shp or MU12328SHR001.shp
				filetype = 'shp'
				filelist = shpfileList
				break
	if len(e00fileList) > 0:
		for e00 in e00fileList:
			if e00[-9:-6].upper() in submissionLookUp[submType] or e00[-10:-7].upper() in submissionLookUp[submType]: # to catch MU123_28SHR00.E00 or MU12328AOC000.E00
				filetype = 'e00'
				filelist = e00fileList
				break


	# finding fmuName from fmuCode
	for k,v in fmuLookUp.items():
		if v[0] == fmuCode:
			fmuName = k
			break
	if fmuName == 'unknown':
		raise Exception("FMU Code (%s) is invalid"%fmuCode)

	# print2("FMU Name: %s\nFMU Code: %s\nSubmission Type: %s\nSubmission Year: %s\nFile Type: %s"%(fmuName,fmuCode,submType,submYear,filetype))

	return [fmuName,fmuCode,submType,submYear,filetype,filelist,pdfList]

	# Example of filelist:
	# ['C:\\\\FIPDownload\\\\download_cart_2018-01-08\\\\Product Submission - 23035\\MU898_2018_AWS\\MU898_2018_AWS_LAYERS\\MU898_2018_AWS\\MU898_18AGP00.shp', 'C:\\\\FIPDownload\\\\download_cart_2018-01-08\\\\Product Submission - 23035\\MU898_2018_AWS\\MU898_2018_AWS_LAYERS\\MU898_2018_AWS\\MU898_18SAC01.shp',...


	# another way to find submission type:
	# if len(shpfileList) > 0:
	# 	for shpfile in shpfileList:
	# 		for submissiontype, layerlist in submissionLookUp.items():
	# 			if shpfile[-9:-6] in layerlist:
	# 				submType = submissiontype
	# 				break


if __name__ == '__main__':
	identifySubmission(r'C:\\FIPDownload\\download_cart_2018-01-08\\Product Submission - 23035')