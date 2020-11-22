## This script was created by Daniel Kim on Aug 2017

## Use: Once you have candidate area or final area of Caribou Habitat Range,
##      use this script to calculate the total area of each of the habitat range
##      polygons and weighted average of forest age for each polygon.
##
## Inputs:
## Candidate DCHS: Feature Class of the candidate or final area of caribou
##      habitat range within a specific FMU. Your Candidate polygon must have
##      only one ObjectID field.
## eFIR: Feature Class of the inventory of that specific FMU. The inventory can
##      be eFRI, PCM, PCI, or BMI as long as it has the following fields:
##      POLYTYPE, POLYID, AGE.
## outputgdb: The tool will output a temporary feature class. Specify where you
##      want to store it.
## outputFolder: Specify the folder where you'd like to save the html report.



print "Importing Arcpy..."

import arcpy
import os, datetime, webbrowser

# user inputs:
CandidateDCHS = arcpy.GetParameterAsText(0)
eFRI = arcpy.GetParameterAsText(1) #feature class
outputgdb = arcpy.GetParameterAsText(2)
outputFolder = arcpy.GetParameterAsText(3)


#           Checking if the input tables have valid fields.

efriFields = [str(f.name).upper() for f in arcpy.ListFields(eFRI)]
for f in ['POLYTYPE','AGE']:
    if f not in efriFields:
        arcpy.AddMessage("ERROR!!!  Can't find %s field in your input file.")



#               clipping the eFRI to DCHS shape...

arcpy.AddMessage("clipping the eFRI to DCHS shape...")



clipOutputfc = outputgdb + r'/inv_clip_' + os.path.split(CandidateDCHS)[1]

# check if the clipOutputfc already exists - delete it if it already does.
try:
    arcpy.Delete_management(clipOutputfc)
except:
    pass

arcpy.Clip_analysis(in_features=eFRI, clip_features= CandidateDCHS, out_feature_class= clipOutputfc, cluster_tolerance="")




#              union the clip output to the candidate DCHS

arcpy.AddMessage("unioning the clip output to the candidate DCHS...")
unionOutputfc = outputgdb + r'/inv_clipunion_' + os.path.split(CandidateDCHS)[1]

# delete if the output feature class already exists
try:
    arcpy.Delete_management(unionOutputfc)
except:
    pass

arcpy.Union_analysis(in_features= clipOutputfc + " #;"+ CandidateDCHS + " #", out_feature_class= unionOutputfc, join_attributes="ALL", cluster_tolerance="", gaps="GAPS")

# delete the clipLOutputfc since it's no longer useful.
try:
    arcpy.Delete_management(clipOutputfc)
except:
    pass




#         Add a new field and calculate the area in hectare

arcpy.AddMessage("Adding a new field called 'New_Area_Ha' and calculating the area in hectare...")
# delete the field if it already exists
try:
    arcpy.DeleteField_management('POLY_AREA')
except:
    pass

arcpy.AddGeometryAttributes_management(Input_Features=unionOutputfc, Geometry_Properties="AREA", Length_Unit="", Area_Unit="HECTARES", Coordinate_System="PROJCS['MNR_Lambert_Conformal_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',930000.0],PARAMETER['False_Northing',6430000.0],PARAMETER['Central_Meridian',-85.0],PARAMETER['Standard_Parallel_1',44.5],PARAMETER['Standard_Parallel_2',53.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]")

#                   rename the POLY_AREA field

areaFieldName = 'New_Area_Ha'
# delete the field if it already exists
try:
    arcpy.DeleteField_management(areaFieldName)
except:
    pass
arcpy.AlterField_management(in_table=unionOutputfc, field="POLY_AREA", new_field_name = areaFieldName, new_field_alias="", field_type="DOUBLE", field_length="8", field_is_nullable="NULLABLE", clear_field_alias="false")




#             Now, for the actual calculation...
arcpy.AddMessage("Calculating Total Area and area weighted average of age...")

# we first need unique objectIDs of the DCHS.
try:
    cursor = arcpy.da.SearchCursor(CandidateDCHS,['OBJECTID'])
except RuntimeError:
    arcpy.AddWarning("Your DCHS layer doesn't have OBJECTID field. Convert it to a feature class and try again.")

objIdList = [int(cursor[0]) for row in cursor]
table = dict(zip(objIdList,[[] for i in objIdList]))


# create a list of fields we want to examine...
FIDField = "FID_" + os.path.split(CandidateDCHS)[1]  # for example, FID_All_V1
f = ['POLYTYPE','AGE',FIDField,areaFieldName]

cursor = arcpy.da.SearchCursor(unionOutputfc,f)

# Calculating the total area
for id in objIdList:
    areaList = [cursor[f.index(areaFieldName)] for row in cursor
                if cursor[f.index(FIDField)] == id]
    cursor.reset()
    totalArea = sum(areaList)
    table[id].append(totalArea)

    areaFORList = [cursor[f.index(areaFieldName)] for row in cursor
                if cursor[f.index(FIDField)] == id
                if cursor[f.index('POLYTYPE')] == 'FOR']
    cursor.reset()
    totalFORArea = sum(areaFORList)
    table[id].append(totalFORArea)

    ageTimesArea = [cursor[f.index(areaFieldName)] * cursor[f.index('AGE')] for row in cursor
                    if cursor[f.index(FIDField)] == id
                    if cursor[f.index('POLYTYPE')] == 'FOR']
    cursor.reset()
    try:
        weightedAvg = sum(ageTimesArea)/totalFORArea
    except:
        weightedAvg = 'N/A'
    table[id].append(weightedAvg)

if len(objIdList) < 500: arcpy.AddMessage(table)





# writing the report
arcpy.AddMessage("\nWriting the report...")
today = datetime.date.today()
output = os.path.join(outputFolder,'AreaWeightedAvg_Age_' + str(today) + '.html')
rep = open(output,'w')

htmlStyle = '''
<!DOCTYPE html>
<html>
<head>
<style>
body {
    font-family: "Helvetica", "Tahoma";
}

#table {width:50%;}
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
}
th, td {
    padding: 3px;
    text-align: left;
}
table#t02 tr:nth-child(even) {
    background-color: #eee;
}
table#t02 tr:nth-child(odd) {
   background-color:#fff;
}
table#t02 th {
    background-color: #708090;
    color: white;
}
table#t01 th {
    border: 1px solid white;
    border-collapse: collapse;
}
table#t01 td {
    border: 1px solid white;
    border-collapse: collapse;
}
h1 {
    display: block;
    font-size: 1.5em;
    margin-top: 0.67em;
    margin-bottom: 0.67em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
    background-color: #B8B8B8;
}

h2 {
    display: block;
    font-size: 1.3em;
    margin-top: 0.83em;
    margin-bottom: 0.83em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
    background-color: #E6E6E6;
}

h3 {
    display: block;
    font-size: 1em;
    margin-top: 1em;
    margin-bottom: 1em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
    background-color: #F1F1F1;
}

h4 {
    display: block;
    margin-top: 1.33em;
    margin-bottom: 1.33em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
}
#p01 {
    color: green;
    font-weight: bold;
}
#p02 {
    color: orange;
    font-weight: bold;
}
#p03 {
    color: red;
    font-weight: bold;
}

</style>
</head>
'''

rep.write(htmlStyle)
rep.write('''
<body>
<h2>Area Weighted Average of Age for each ObjectID</h2>
<p>
Input Candidate Area: %s
<br>
Input Inventory: %s
</p>
<br>
'''%(CandidateDCHS,eFRI))

rep.write('''
    <table id="t02">
      <tr>
        <th>Object ID</th>
        <th>Total Area (Ha)</th>
        <th>Area where POLYTYPE = FOR</th>
        <th>Age (Area weighted average)</th>
      </tr>
''')

htmlstring = ''
for id in objIdList:
    htmlstring += '<tr>'
    htmlstring += '<td>' + str(id) + '</td>'
    htmlstring += '<td>' + str(table[id][0]) + '</td>'
    htmlstring += '<td>' + str(table[id][1]) + '</td>'
    htmlstring += '<td>' + str(table[id][2]) + '</td>'
    htmlstring += '</tr>'
htmlstring += '</table>'

rep.write(htmlstring)

# foodnote

timeEnd = str(datetime.datetime.now())
rep.write('''
<br><br>
Note that only those records with POLYTYPE = FOR has been chosen to calcualte the weighted average.<br>
Time Run: %s
'''%timeEnd)

rep.write('</body>')

webbrowser.open(output,new=2)


