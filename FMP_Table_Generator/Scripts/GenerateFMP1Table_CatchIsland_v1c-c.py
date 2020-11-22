# This script requires fmptable1_sample.html saved in the same folder as this script.
# Updated addtion of SEEDTREE on BelowRegen and Forest Stands
version = '1c-c'

import arcpy
import os, datetime, webbrowser, inspect

testing = True

## Use the following two lines if running straight from the script
##inputpci = r'C:\DanielK_Workspace\FMP_LOCAL\Spanish\PCI\2020\_data\FMP_Schema.gdb\MU210_20PCI00'
##outputfolder = r'C:\DanielK_Workspace\FMP_LOCAL'

inputpci = arcpy.GetParameterAsText(0)
outputfolder = arcpy.GetParameterAsText(1)


arcpy.AddMessage("You are using Generate FMP1 Table Tool v"+version + '\n')
# Checking if the input PCI has all the fields needed to create the FMP1 table
arcpy.AddMessage("Checking mandatory fields...")

manFields = ['POLYTYPE', 'DEVSTAGE', 'OWNER','FORMOD','MGMTCON1'] # !!!!!!!! This is the list of fields used in the below list of SQLs

existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputpci)]

existingManFields = list(set(manFields)&set(existingFields))
if len(existingManFields) != len(manFields):
    raise Exception("MISSING MANDATORY FIELD(S)! \nYour input file must include the following fields:\n%s"%manFields)

if 'SHAPE_AREA' in existingFields:
    AreaField = 'SHAPE_AREA'
    manFields.append('SHAPE_AREA')
elif 'AREA' in existingFields:
    AreaField = 'AREA'
    manFields.append('AREA')    
else:
    raise Exception("MISSING MANDATORY FIELD! \nYour input file must have either 'Shape_Area' field or 'Area' field.\n")

# creating the report html file on the output folder as specified above.
today = datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')
reportfilename = "FMP1Table_%s_%s.html"%(os.path.split(inputpci)[1], today) # eg. FMP1Table_MU210_20PCI00_2017-10-10.html
reportfile = os.path.join(outputfolder, reportfilename)
rep = open(reportfile,'w')

# Copying the html code from the sample file and saving it in a string variable
sample = open(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],'fmptable1_sample_CatchIsland.html'))
htmlstring = ''
for line in sample:
    htmlstring += line
sample.close()

# Handling non-mandatory fields: MGMTCON2 and MGMTCON3.

if 'MGMTCON2' in existingFields and 'MGMTCON3' in existingFields:
    MGMTCON23isISLD = """ OR "MGMTCON2" = 'ISLD' OR "MGMTCON3" = 'ISLD' """
    MGMTCON23isnotISLD = """ AND "MGMTCON2" <> 'ISLD' AND "MGMTCON3" <> 'ISLD' """
elif 'MGMTCON2' in existingFields:
    MGMTCON23isISLD = """ OR "MGMTCON2" = 'ISLD' """
    MGMTCON23isnotISLD = """ AND "MGMTCON2" <> 'ISLD' """
else:
    MGMTCON23isISLD, MGMTCON23isnotISLD = '',''

# Dictionary of SQL Queries

sql = {

'WatCroMan':    [""" "POLYTYPE" = 'WAT' AND "OWNER" = '1' """],
'WatCroOth':    [""" "POLYTYPE" = 'WAT' AND "OWNER" in('5','7') """],
'WatPatCro':    [""" "POLYTYPE" = 'WAT' AND "OWNER" = '2' """],
'WatOthNon':    [""" "POLYTYPE" = 'WAT' AND "OWNER" in('3','4','6','8','9','0') """],
'WatTot':       [""" "POLYTYPE" = 'WAT' """],

'AgrCroMan':    [""" "POLYTYPE" = 'DAL' AND "OWNER" = '1' """],
'AgrCroOth':    [""" "POLYTYPE" = 'DAL' AND "OWNER" in('5','7') """],
'AgrPatCro':    [""" "POLYTYPE" = 'DAL' AND "OWNER" = '2' """],
'AgrOthNon':    [""" "POLYTYPE" = 'DAL' AND "OWNER" in('3','4','6','8','9','0') """],
'AgrTot':       [""" "POLYTYPE" = 'DAL' """],

'GraCroMan':    [""" "POLYTYPE" = 'GRS' AND "OWNER" = '1' """],
'GraCroOth':    [""" "POLYTYPE" = 'GRS' AND "OWNER" in('5','7') """],
'GraPatCro':    [""" "POLYTYPE" = 'GRS' AND "OWNER" = '2' """],
'GraOthNon':    [""" "POLYTYPE" = 'GRS' AND "OWNER" in('3','4','6','8','9','0') """],
'GraTot':       [""" "POLYTYPE" = 'GRS' """],

'UncCroMan':    [""" "POLYTYPE" = 'UCL' AND "OWNER" = '1' """],
'UncCroOth':    [""" "POLYTYPE" = 'UCL' AND "OWNER" in('5','7') """],
'UncPatCro':    [""" "POLYTYPE" = 'UCL' AND "OWNER" = '2' """],
'UncOthNon':    [""" "POLYTYPE" = 'UCL' AND "OWNER" in('3','4','6','8','9','0') """],
'UncTot':       [""" "POLYTYPE" = 'UCL' """],

'OthCroMan':    [""" "POLYTYPE" = 'ISL' AND "OWNER" = '1' """],
'OthCroOth':    [""" "POLYTYPE" = 'ISL' AND "OWNER" in('5','7') """],
'OthPatCro':    [""" "POLYTYPE" = 'ISL' AND "OWNER" = '2' """],
'OthOthNon':    [""" "POLYTYPE" = 'ISL' AND "OWNER" in('3','4','6','8','9','0') """],
'OthTot':       [""" "POLYTYPE" = 'ISL' """],

'SNFCroMan':    [""" "POLYTYPE" in('WAT','DAL','GRS','UCL','ISL') AND "OWNER" = '1' """],
'SNFCroOth':    [""" "POLYTYPE" in('WAT','DAL','GRS','UCL','ISL') AND "OWNER" in('5','7') """],
'SNFPatCro':    [""" "POLYTYPE" in('WAT','DAL','GRS','UCL','ISL') AND "OWNER" = '2' """],
'SNFOthNon':    [""" "POLYTYPE" in('WAT','DAL','GRS','UCL','ISL') AND "OWNER" in('3','4','6','8','9','0') """],
'SNFTot':       [""" "POLYTYPE" in('WAT','DAL','GRS','UCL','ISL') """],

'TreCroMan':    [""" "POLYTYPE" = 'TMS' AND "OWNER" = '1' """],
'TreCroOth':    [""" "POLYTYPE" = 'TMS' AND "OWNER" in('5','7') """],
'TrePatCro':    [""" "POLYTYPE" = 'TMS' AND "OWNER" = '2' """],
'TreOthNon':    [""" "POLYTYPE" = 'TMS' AND "OWNER" in('3','4','6','8','9','0') """],
'TreTot':       [""" "POLYTYPE" = 'TMS' """],

'OpeCroMan':    [""" "POLYTYPE" = 'OMS' AND "OWNER" = '1' """],
'OpeCroOth':    [""" "POLYTYPE" = 'OMS' AND "OWNER" in('5','7') """],
'OpePatCro':    [""" "POLYTYPE" = 'OMS' AND "OWNER" = '2' """],
'OpeOthNon':    [""" "POLYTYPE" = 'OMS' AND "OWNER" in('3','4','6','8','9','0') """],
'OpeTot':       [""" "POLYTYPE" = 'OMS' """],

'BruCroMan':    [""" "POLYTYPE" = 'BSH' AND "OWNER" = '1' """],
'BruCroOth':    [""" "POLYTYPE" = 'BSH' AND "OWNER" in('5','7') """],
'BruPatCro':    [""" "POLYTYPE" = 'BSH' AND "OWNER" = '2' """],
'BruOthNon':    [""" "POLYTYPE" = 'BSH' AND "OWNER" in('3','4','6','8','9','0') """],
'BruTot':       [""" "POLYTYPE" = 'BSH' """],

'RocCroMan':    [""" "POLYTYPE" = 'RCK' AND "OWNER" = '1' """],
'RocCroOth':    [""" "POLYTYPE" = 'RCK' AND "OWNER" in('5','7') """],
'RocPatCro':    [""" "POLYTYPE" = 'RCK' AND "OWNER" = '2' """],
'RocOthNon':    [""" "POLYTYPE" = 'RCK' AND "OWNER" in('3','4','6','8','9','0') """],
'RocTot':       [""" "POLYTYPE" = 'RCK' """],

'SNPCroMan':    [""" "POLYTYPE" in('TMS','OMS','BSH','RCK') AND "OWNER" = '1' """],
'SNPCroOth':    [""" "POLYTYPE" in('TMS','OMS','BSH','RCK') AND "OWNER" in('5','7') """],
'SNPPatCro':    [""" "POLYTYPE" in('TMS','OMS','BSH','RCK') AND "OWNER" = '2' """],
'SNPOthNon':    [""" "POLYTYPE" in('TMS','OMS','BSH','RCK') AND "OWNER" in('3','4','6','8','9','0') """],
'SNPTot':       [""" "POLYTYPE" in('TMS','OMS','BSH','RCK') """],

# 'SitCroMan':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" = 'PF' AND "OWNER" = '1' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
# 'SitCroOth':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" = 'PF' AND "OWNER" in('5','7') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
# 'SitPatCro':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" = 'PF' AND "OWNER" = '2' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
# 'SitOthNon':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" = 'PF' AND "OWNER" in('3','4','6','8','9','0') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
# 'SitTot':       [""" "POLYTYPE" = 'FOR' AND "FORMOD" = 'PF' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],

'IslCroMan':    [""" "POLYTYPE" = 'FOR' AND "OWNER" = '1' AND ("MGMTCON1" = 'ISLD' """ + MGMTCON23isISLD + ')'],
'IslCroOth':    [""" "POLYTYPE" = 'FOR' AND "OWNER" in('5','7') AND ("MGMTCON1" = 'ISLD' """ + MGMTCON23isISLD + ')'],
'IslPatCro':    [""" "POLYTYPE" = 'FOR' AND "OWNER" = '2' AND ("MGMTCON1" = 'ISLD' """ + MGMTCON23isISLD + ')'],
'IslOthNon':    [""" "POLYTYPE" = 'FOR' AND "OWNER" in('3','4','6','8','9','0') AND ("MGMTCON1" = 'ISLD' """ + MGMTCON23isISLD + ')'],
'IslTot':       [""" "POLYTYPE" = 'FOR' AND ("MGMTCON1" = 'ISLD' """ + MGMTCON23isISLD + ')'],

'SPTCroMan':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" = 'PF' AND "OWNER" = '1' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'SPTCroOth':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" = 'PF' AND "OWNER" in('5','7') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'SPTPatCro':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" = 'PF' AND "OWNER" = '2' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'SPTOthNon':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" = 'PF' AND "OWNER" in('3','4','6','8','9','0') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'SPTTot':       [""" "POLYTYPE" = 'FOR' AND "FORMOD" = 'PF' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],

'RecCroMan':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" in('DEPHARV','DEPNAT','LASTCUT','SEEDTREE') AND "OWNER" = '1' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],  ## Added Lastcut and Seedtree Nov 1 ,2018
'RecCroOth':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" in('DEPHARV','DEPNAT','LASTCUT','SEEDTREE') AND "OWNER" in('5','7') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'RecPatCro':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" in('DEPHARV','DEPNAT','LASTCUT','SEEDTREE') AND "OWNER" = '2' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'RecOthNon':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" in('DEPHARV','DEPNAT','LASTCUT','SEEDTREE') AND "OWNER" in('3','4','6','8','9','0') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'RecTot':       [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" in('DEPHARV','DEPNAT','LASTCUT','SEEDTREE') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],

'BelCroMan':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" in('LOWMGMT', 'LOWNAT','NEWPLANT','NEWSEED','NEWNAT') AND "OWNER" = '1' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'BelCroOth':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" in('LOWMGMT', 'LOWNAT','NEWPLANT','NEWSEED','NEWNAT') AND "OWNER" in('5','7') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'BelPatCro':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" in('LOWMGMT', 'LOWNAT','NEWPLANT','NEWSEED','NEWNAT') AND "OWNER" = '2' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'BelOthNon':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" in('LOWMGMT', 'LOWNAT','NEWPLANT','NEWSEED','NEWNAT') AND "OWNER" in('3','4','6','8','9','0') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'BelTot':       [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" in('LOWMGMT', 'LOWNAT','NEWPLANT','NEWSEED','NEWNAT') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],

'ForCroMan':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" not in('DEPHARV','DEPNAT','LASTCUT','LOWMGMT', 'LOWNAT','NEWPLANT','NEWSEED','NEWNAT','SEEDTREE') AND "OWNER" = '1' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD], 
'ForCroOth':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" not in('DEPHARV','DEPNAT','LASTCUT','LOWMGMT', 'LOWNAT','NEWPLANT','NEWSEED','NEWNAT','SEEDTREE') AND "OWNER" in('5','7') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'ForPatCro':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" not in('DEPHARV','DEPNAT','LASTCUT','LOWMGMT', 'LOWNAT','NEWPLANT','NEWSEED','NEWNAT','SEEDTREE') AND "OWNER" = '2' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'ForOthNon':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" not in('DEPHARV','DEPNAT','LASTCUT','LOWMGMT', 'LOWNAT','NEWPLANT','NEWSEED','NEWNAT','SEEDTREE') AND "OWNER" in('3','4','6','8','9','0') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'ForTot':       [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "DEVSTAGE" not in('DEPHARV','DEPNAT','LASTCUT','LOWMGMT', 'LOWNAT','NEWPLANT','NEWSEED','NEWNAT','SEEDTREE') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],

'SPDCroMan':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "OWNER" = '1' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'SPDCroOth':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "OWNER" in('5','7') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'SPDPatCro':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "OWNER" = '2' AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'SPDOthNon':    [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "OWNER" in('3','4','6','8','9','0') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],
'SPDTot':       [""" "POLYTYPE" = 'FOR' AND "FORMOD" in('RP','MR') AND "MGMTCON1" <> 'ISLD' """ + MGMTCON23isnotISLD],

'SPFCroMan':    [""" "POLYTYPE" = 'FOR' AND "OWNER" = '1' """],
'SPFCroOth':    [""" "POLYTYPE" = 'FOR' AND "OWNER" in('5','7') """],
'SPFPatCro':    [""" "POLYTYPE" = 'FOR' AND "OWNER" = '2' """],
'SPFOthNon':    [""" "POLYTYPE" = 'FOR' AND "OWNER" in('3','4','6','8','9','0') """],
'SPFTot':       [""" "POLYTYPE" = 'FOR' """],

'SFOCroMan':    [""" "POLYTYPE" in('FOR','TMS','OMS','BSH','RCK') AND "OWNER" = '1' """],
'SFOCroOth':    [""" "POLYTYPE" in('FOR','TMS','OMS','BSH','RCK') AND "OWNER" in('5','7') """],
'SFOPatCro':    [""" "POLYTYPE" in('FOR','TMS','OMS','BSH','RCK') AND "OWNER" = '2' """],
'SFOOthNon':    [""" "POLYTYPE" in('FOR','TMS','OMS','BSH','RCK') AND "OWNER" in('3','4','6','8','9','0') """],
'SFOTot':       [""" "POLYTYPE" in('FOR','TMS','OMS','BSH','RCK') """],

'TOTCroMan':    [""" "OWNER" = '1' """],
'TOTCroOth':    [""" "OWNER" in('5','7') """],
'TOTPatCro':    [""" "OWNER" = '2' """],
'TOTOthNon':    [""" "OWNER" in('3','4','6','8','9','0') """],
'TOTTot':       [""" "POLYTYPE" is not null and "POLYTYPE" not in ('',' ') """],

'TOTCroAll':	[""" "OWNER" in('1','5','7') """],
'TOTNonAll':	[""" "OWNER" in('2','3','4','6','8','9','0') """],

}


# Creating the search cursor

f = manFields
for k, v in sql.iteritems():
    area=0
    cursor = arcpy.da.SearchCursor(inputpci,f,v[0])
    for row in cursor:
        area += row[f.index(AreaField)]
    area = area/10000
    arcpy.AddMessage("Calculating %s..."%k)
    v.append(area)
##    v.append(format(int(round(area)),',d')) # round down to nearest integer and turn into a string with thousand separators
    v.append('{:,.1f}'.format(area)) # round down to nearest hundredth and turn into a string with thousand separators
    ## at this point the sql will look like... 'WatCroMan':   [""" "POLYTYPE" = 'WAT' AND "OWNER" = '1' """, 1442.334, '1,442.33'],

    arcpy.AddMessage(v[2])
    # replacing the place holder with the actual area in the report html string
    htmlstring = htmlstring.replace(k + 'V', v[2],1)
    htmlstring = htmlstring.replace(k + 'Q', v[0],2)

# Title and footnote
arcpy.AddMessage("Adding Title and Footnote...")
extraInfo = {
    '*PCIFileName':     os.path.split(inputpci)[1],
    '*PCIused':         inputpci,
    '*pythonscript':    str(inspect.getfile(inspect.currentframe())),
    '*reportlocation':  reportfile,
    '*dateandtime':     str(datetime.datetime.now())
    }
for k, v in extraInfo.iteritems():
    htmlstring = htmlstring.replace(k,v)

rep.write(htmlstring)

arcpy.AddMessage('\n\n****  Your report is saved here  ****')
arcpy.AddMessage(reportfile + '\n')

rep.close()
webbrowser.open(reportfile,new=2)
