

txtstring = """
#submission is the FI Portal Submission Number
#If submission is not filled in, will use the filename of metadata file to identify submission
submission= $SubID

#fmu and FMU_Num are the name and number of the unit
#If fmu is not filled in, will use the filesystem location to identify fmu
fmu= $fmuName

#If fmu_num is not filled in, will use the filesystem location to identify fmu, then lookup fmu_num
fmu_num= $fmuCode

#product is the product type, which should be in the list ['AWS','AR','FMP','EFRI']
#If product is not filled in, will use the filesystem location to identify product
product= $submType

#Applicable Year (Fiscal year, starting April 1)
#If year is not filled in, will use the filesystem location to identify year
year= $submYear

#status should be in the list ['Approved','Submitted','Denied','AcceptedForReview']
status=Submitted

#dates should be of the for YYYY-MM-DD
#dates left blank will be ignored
date_submitted= 
date_approved=
date_downloaded= $yearmonthdate

#Users can use full names or system names
downloader= $username

#Export paths can be UNC, or local to the machine, and will have the fmu, product and year added to the end
#Multiple export paths are acceptable
export_path= $outputFolder

#Filetype from the list ['E00','SHP,'GDB'], detected if not spec'date_approved
filetype= $filetype
"""


def writeMetadata(outputFolder,SubID,fmuName,fmuCode,submType,submYear,filetype,tempFolder):
	import os, getpass, datetime

	# print('Writing metadata file for %s %s %s...'%(fmuName,submType,SubID))
	
	yearmonthdate = datetime.datetime.now().strftime('%Y-%m-%d')


	username = getpass.getuser()

	varList = ['outputFolder','SubID','fmuName','fmuCode','submType','submYear','filetype','yearmonthdate','username']

	newtxtstring = txtstring
	for var in varList:
		newtxtstring = newtxtstring.replace('$'+var,str(eval(var)))

	metaFileName = os.path.join(tempFolder,'fi_Submission_' + str(SubID) + '.txt')
	meta = open(metaFileName,'w')
	meta.write(newtxtstring)
	meta.close()


#testing
if __name__ == '__main__':
	writeMetadata(r'N:\WORK-DATA\FMPDS\Temagami\AWS\2018','a','b','d','f','e','r')