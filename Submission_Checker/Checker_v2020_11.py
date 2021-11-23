#-------------------------------------------------------------------------------
# Name:        	FI Checker

checker_version = '2021.11'

# Purpose:	   	This tool checks the FMP, AR or AWS submission (according to the 
#				FIM Technical Specifications 2009 or 2017) and outputs a validation report 
#				in html format.The report will be saved at the same folder level where your 
#				geodatabase is saved. This validation report is equivalent to stage 1 and 
#				stage 2 checks of the current (2017) FI portal.
#
#			   
# Author:      Ministry of Natural Resources and Forestry (MNRF)
#
# Created:     24/02/2017
# Copyright:   MNRF 2017
#
# Updates:	May 24, 2018
#			Added error_limit variable to give the user an option to create a full or shortened error detail section.
#			Any further updates can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog
#			
#-------------------------------------------------------------------------------
print("Importing Arcpy...")
import arcpy
import Modules.Reference as R

# user inputs:
plan  = arcpy.GetParameterAsText(0) ## Must be one from aws, ar and fmp. not case-sensitive.
fmu = arcpy.GetParameterAsText(1) ## case-sensitive. can't have spaces - ie Big_Pic
year = int(arcpy.GetParameterAsText(2)) ## must be an integer
fmpStartYear = int(arcpy.GetParameterAsText(3)) ## must be an integer
workspace = arcpy.GetParameterAsText(4) ## gdb where the submission feature classes are stored.
dataformat = arcpy.GetParameterAsText(5) # eg. 'shapefile','feature class' or 'coverage'
tech_spec_version = arcpy.GetParameterAsText(6) # "Old (2009)" or "Current"
tech_spec_version = "2020" if tech_spec_version == "Latest" else "2009"
SubID = arcpy.GetParameterAsText(7) # optional. cant have special character since the filename will include submission id. Also, the Reference.findSubID will try to find the submission ID in fmu/plan/year/ folder.
error_limit = str(arcpy.GetParameterAsText(8)) # "Limit to 50 errors per error type" or "Full Report"

if error_limit == 'Limit to 50 errors per error type':
	error_limit = 50
else:
	error_limit = 999999 # need to have some upper limit due to the html file size limitation.

from Modules.CheckAll import Check
try:
	class_check = Check(plan,fmu,year,fmpStartYear,workspace, dataformat, tech_spec_version, error_limit, checker_version, SubID)
	class_check.run()
finally:
	arcpy.AddMessage("\nTool version: v%s"%checker_version)




