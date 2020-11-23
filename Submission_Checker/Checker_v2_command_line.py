#-------------------------------------------------------------------------------
# Name:        	checker_v2

checker_version = '2020.11'

# Purpose:	   	This tool checks the FMP, AR or AWS submission (according to the 
#				FIM Technical Specifications 2009 or 2017) and outputs a validation report 
#				in html format.The report will be saved at the same folder level where your 
#				geodatabase is saved. This validation report is equivalent to stage 1 and 
#				stage 2 checks of the current (2017) FI portal.
#
#			   
# Author:      Ministry of Natural Resources and Forestry (MNRF)
#-------------------------------------------------------------------------------

print("Importing Arcpy...")
import arcpy
import sys
import Modules.Reference as R



# # user inputs:
plan  = sys.argv[1] ## Must be one from aws, ar and fmp. not case-sensitive.
fmu = sys.argv[2] ## case-sensitive. can't have spaces - ie Big_Pic
year = int(sys.argv[3]) ## Submission year - eg. 2020
fmpStartYear = int(sys.argv[4]) ## must be an integer
workspace = sys.argv[5] ## gdb/folder where the submission feature classes are stored.


dataformat = sys.argv[6] # has to be 'shp','fc','cov'.
dataformat_dict = {'shp':'shapefile', 'fc':'feature class', 'cov':'coverage'}
dataformat = dataformat_dict[dataformat]


tech_spec_version = sys.argv[7] # 'old' or 'new'
if tech_spec_version == 'old':
	tech_spec_version = "2009"
else:
	tech_spec_version = "2020"

error_limit = sys.argv[8] # 'limit' or 'nolimit'
if error_limit == 'nolimit':
	error_limit = 999999
else:
	error_limit = 50


SubID = sys.argv[9] # cant have special character since the filename will include submission id. Also, the Reference.findSubID will try to find the submission ID in fmu/plan/year/ folder.


from Modules.CheckAll import Check
try:
	class_check = Check(plan,fmu,year,fmpStartYear,workspace, dataformat, tech_spec_version, error_limit, checker_version, SubID)
	class_check.run()
finally:
	print("\nTool version: v%s"%checker_version)