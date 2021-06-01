version = 20210601
#-------------------------------------------------------------------------------
# Name:        MEA Tool
# Purpose:     Use this tool once you have a general idea of where MEA should be. This tool will help you decide whether your candidate area has enough MAFA and etc.
#
# Author:      kimdan
#
# Created:     19/07/2017
# Copyright:   (c) kimdan 2017
# Licence:     <your licence>
#
# Bug Fix:      2018-03-20
#               Candidate areas with donut holes will run fine (fixed the topology issue by self-unioning the candidate area layer)
#               2021-06-01
#               The tool no longer looks for NDD folder, but asks the user to specify the location of the gdb
#               where LIO data is held.
#               Aquatic Feeding Area is no longer a layer. it's in wildlife layer now.
#-------------------------------------------------------------------------------

import arcpy
import os

testing = True

fmu = str(arcpy.GetParameterAsText(0))  # eg. Nipissing. Must match the fmu name of the Forest Management Unit layer of LIO (except it shouldn't have "Forest" at the end.)
meafc = str(arcpy.GetParameterAsText(1)) # any polygon feature class will do. The feature class usually consists of polygons of area larger than 10,000ha.
workspace = str(arcpy.GetParameterAsText(2)) # This tool will generate analyzed MEA candidate areas as well as other feature classes. Specify a gdb where you'd like to store them.
ndd_path = str(arcpy.GetParameterAsText(3)) # traditionally this is "N:\NDD\GDDS-Internal-MNRF.gdb", but now users can input sharepoint location
olt = str(arcpy.GetParameterAsText(4)) # OLT moose carrying capacity shapefile or feature class
bmi = str(arcpy.GetParameterAsText(5)) # BMI or PCI that has "OWNER" field
arCC = str(arcpy.GetParameterAsText(6)) # Don't have to be AR. Polygons of previous harvests (preferablly clear cut) will do.
arSH = str(arcpy.GetParameterAsText(7))
arSE = str(arcpy.GetParameterAsText(8))
drvRoad = str(arcpy.GetParameterAsText(9)) # will be clipped, buffered by 500m and 1km
winterCov = str(arcpy.GetParameterAsText(10)) # also optional. This input must be the output of the Moose Winter Cover Delineator tool.


arcpy.env.workspace = workspace

arcpy.AddMessage("\nMEA_Tool v%s"%version)

# check if ndd_path is a gdb
if arcpy.Describe(ndd_path).dataType != 'Workspace':
    arcpy.AddError("The NDD path you specified is not a geodatabase.")

fcList = arcpy.ListFeatureClasses()
if len(fcList) > 0:
    arcpy.AddMessage("Following feature classes already exist in %s: \n%s"%(workspace,fcList))

unionList = [] # this list of fcs will be unioned to the candidate MEA later.

# copying over the candidate MEA
candidatefc = fmu.replace(' ','_') + '_MEA_Candidate'
fc = candidatefc
if fc not in fcList:
    arcpy.AddMessage("Copying over the candidate MEA to the workspace gdb and renaming it to %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features= meafc, out_path= workspace, out_name=fc)
else:
    arcpy.AddMessage("%s already exists."%fc)


# Creating LIO basedata cuts

# FMU boundary
mufc = fmu.replace(' ','_') + '_muBoundary'
fc = mufc
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features=os.path.join(ndd_path,"forest_management_unit"), out_path= workspace, out_name=fc, where_clause="FMU_NAME = '" + fmu + " Forest'")
else:
    arcpy.AddMessage("%s already exists."%fc)

# FMU boundary + 10km buffer
mufc10k = fmu.replace(' ','_') + '_muBoundary_Buff10k'
fc = mufc10k
in_fc = mufc
buffDistance = '10 Kilometers'
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.Buffer_analysis(in_fc, fc, buffDistance)
else:
    arcpy.AddMessage("%s already exists."%fc)


# !!! Changed in 2021: MAFA and Wintering Area are now in one layer called "WILDLIFE_ACTIVITY_AREA"
# WILDLIFE_ACTIVITY_AREA (clip to fmu + 10k buffer, then select by WILDLIFE_ACTIVITY_TYPE)
wildlife = fmu.replace(' ','_') + '_WildlifeActivityArea'
fc = wildlife
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.Clip_analysis(in_features=os.path.join(ndd_path,"WILDLIFE_ACTIVITY_AREA"), clip_features = mufc10k, out_feature_class = fc)
else:
    arcpy.AddMessage("%s already exists."%fc)

# deriving MAFA from Wildlife layer
fc = fmu.replace(' ','_') + '_MAFA'
whereClause = "WILDLIFE_ACTIVITY_TYPE = 'Moose Aquatic Feeding Area'"
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features = wildlife, out_path= workspace, out_name=fc, where_clause=whereClause)
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc)


# deriving wintering areas from Wildlife layer
fc = fmu.replace(' ','_') + '_WintArea_Moose'
whereClause = "WILDLIFE_ACTIVITY_TYPE in('Moose Early Wintering Area', 'Moose Late Wintering Area')"
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features = wildlife, out_path= workspace, out_name=fc, where_clause= whereClause)
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc)

fc = fmu.replace(' ','_') + '_WintArea_Deer'
whereClause = "WILDLIFE_ACTIVITY_TYPE in('White-tailed Deer Wintering Area (Stratum 2)', 'White-tailed Deer Yard (Stratum 1)')"
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features = wildlife, out_path= workspace, out_name=fc, where_clause= whereClause)
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc)

## end of change in 2021.06.01


# CLUPA (Clip to fmu+10k buffer, then select by Designation)

clupafc = fmu.replace(' ','_') + '_CLUPA'
fc = clupafc
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.Clip_analysis(in_features=os.path.join(ndd_path,"CLUPA_PROVINCIAL"), clip_features = mufc10k, out_feature_class = fc)
else:
    arcpy.AddMessage("%s already exists."%fc)


fc = fmu.replace(' ','_') + '_CLUPA_ConsReserve'
whereClause = "DESIGNATION_ENG = 'Conservation Reserve'"
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features = clupafc, out_path= workspace, out_name=fc, where_clause= whereClause)
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc)

fc = fmu.replace(' ','_') + '_CLUPA_EMA'
whereClause = "DESIGNATION_ENG = 'Enhanced Management Area'"
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features = clupafc, out_path= workspace, out_name=fc, where_clause= whereClause)
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc)

fc = fmu.replace(' ','_') + '_CLUPA_ForestReserve'
whereClause = "DESIGNATION_ENG = 'Forest Reserve'"
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features = clupafc, out_path= workspace, out_name=fc, where_clause= whereClause)
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc)

fc = fmu.replace(' ','_') + '_CLUPA_ProvPark'
whereClause = "DESIGNATION_ENG = 'Provincial Park'"
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features = clupafc, out_path= workspace, out_name=fc, where_clause= whereClause)
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc)

fc = fmu.replace(' ','_') + '_CLUPA_ProvWildLife'
whereClause = "DESIGNATION_ENG = 'Provincial Wildlife Area'"
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features = clupafc, out_path= workspace, out_name=fc, where_clause= whereClause)
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc)

fc = fmu.replace(' ','_') + '_CLUPA_Wilderness'
whereClause = "DESIGNATION_ENG = 'Wilderness Area'"
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_features = clupafc, out_path= workspace, out_name=fc, where_clause= whereClause)
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc)


# OHN Waterbody (Clip to the fmu + 10k)

waterbfc = fmu.replace(' ','_') + '_OHNwaterbody'
fc = waterbfc
if fc not in fcList:
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.Clip_analysis(in_features=os.path.join(ndd_path,"OHN_WATERBODY"), clip_features = meafc, out_feature_class = fc)
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc) ## for example, ["Nipissing_MAFA34", "Nipissing_MAFA12", "Nipissing_CLUPA_ConsReserve"...]


# OLT's carrying capacity output
if len(olt)>0:
    oltfc = fmu.replace(' ','_') + '_OLTcc'
    if oltfc not in fcList:
        try:
            arcpy.AddMessage("Creating a new fc: %s..."%oltfc)
            arcpy.FeatureClassToFeatureClass_conversion(in_features=olt, out_path= workspace, out_name=oltfc, where_clause='''"MNKMSQ">0''')
            # add new field called MNKMSQ_cat
            arcpy.AddField_management(in_table = oltfc, field_name = "MNKMSQ_CAT", field_type = "Text", field_length=50)
            # calculate field using code block
            arcpy.AddMessage("Running field calculation on %s..."%oltfc)
            codeBlock = '''def f(x):\n  if x < 0.2:\n    return "0 to 0.2"\n  elif x<0.3:\n    return "0.2 to 0.3"\n  elif x<0.4:\n    return "0.3 to 0.4"\n  else:\n    return "0.4 and up"'''
            arcpy.CalculateField_management(in_table=oltfc, field="MNKMSQ_CAT", expression="f(!MNKMSQ!)", expression_type="PYTHON_9.3", code_block=codeBlock)
        except:
            arcpy.AddMessage("\nERROR - failed to create a new fc: %s...\n"%oltfc)

        # dissolve using the MNKSMQ_CAT - 0 to 0.2, 0.2 to 0.3, 0.3 to 0.4, 0.4 and up.
        oltfcdislv = oltfc + "_dslv"
        if oltfcdislv not in fcList:
            arcpy.AddMessage("Creating a new fc: %s..."%oltfcdislv)
            arcpy.Dissolve_management(in_features=oltfc, out_feature_class=oltfcdislv, dissolve_field="MNKMSQ_CAT")
        else:
            arcpy.AddMessage("%s already exists."%oltfcdislv)
    else:
        arcpy.AddMessage("%s already exists."%oltfc)

    # Split the oltfcdislv output into 4 feature classes
    for cat in ["0 to 0.2", "0.2 to 0.3", "0.3 to 0.4", "0.4 and up"]:
        suffix = cat.replace(' ','').replace('.','')
        fc = fmu.replace(' ','_') + '_OLTcc_' + suffix
        whereClause = "MNKMSQ_CAT = '" + cat + "'"
        if fc not in fcList:
            arcpy.AddMessage("Creating a new fc: %s..."%fc)
            arcpy.FeatureClassToFeatureClass_conversion(in_features = oltfcdislv, out_path= workspace, out_name=fc, where_clause= whereClause)
        else:
            arcpy.AddMessage("%s already exists."%fc)
        unionList.append(fc)


# Wetland (Clipped to the fmu + 10k then dissolved)
wetlandfc = fmu.replace(' ','_') + '_WETLAND'
fc = wetlandfc
if fc not in fcList:
    try:
        arcpy.Delete_management("Wetland_temp")
    except:
        pass
    arcpy.AddMessage("Creating a new fc: %s..."%fc)
    arcpy.Clip_analysis(in_features=os.path.join(ndd_path,"WETLAND"), clip_features = meafc, out_feature_class = "Wetland_temp")
    arcpy.Dissolve_management(in_features="Wetland_temp", out_feature_class=fc)
    arcpy.Delete_management("Wetland_temp")
else:
    arcpy.AddMessage("%s already exists."%fc)
unionList.append(fc)


# drivable roads (Clipped to the fmu + 10k then dissolved then buffered by 500m and 1km)
if len(drvRoad)>0:
    drvroadfc = fmu.replace(' ','_') + '_drvRd'
    fc = drvroadfc
    if fc not in fcList:
        arcpy.AddMessage("Creating a new fc: %s..."%fc)
        arcpy.Clip_analysis(in_features= drvRoad, clip_features = mufc10k, out_feature_class = fc)
    else:
        arcpy.AddMessage("%s already exists."%fc)

    # buffer by 500m and 1000m
    for i in ['500','1000']:
        fc = fmu.replace(' ','_') + '_drvRd_' + i
        if fc not in fcList:
            try:
                arcpy.Delete_management("drvroadbuff_temp1")
                arcpy.Delete_management("drvroadbuff_temp2")
            except:
                pass
            arcpy.AddMessage("Creating a new fc: %s..."%fc)
            arcpy.Buffer_analysis(in_features=drvroadfc, out_feature_class="drvroadbuff_temp1", buffer_distance_or_field= i + " Meters")
            arcpy.Clip_analysis(in_features= "drvroadbuff_temp1", clip_features = meafc, out_feature_class = "drvroadbuff_temp2")
            arcpy.Dissolve_management(in_features="drvroadbuff_temp2", out_feature_class=fc)
            arcpy.Delete_management("drvroadbuff_temp1")
            arcpy.Delete_management("drvroadbuff_temp2")
        unionList.append(fc)


# BMI ownership 2,3,4,6
if len(bmi)>0:
    bmifc = fmu.replace(' ','_') + '_bmiOwner2346'
    if bmifc not in fcList:
        try:
            arcpy.Delete_management("bmi_temp")
        except:
            pass
        arcpy.AddMessage("Creating a temp fc: bmi_temp...")
        try:
            whereClause = "OWNER in('2','3','4','6')"
            arcpy.FeatureClassToFeatureClass_conversion(in_features = bmi, out_path= workspace, out_name="bmi_temp", where_clause= whereClause)
        except:
            arcpy.AddMessage("ERROR: Make sure your BMI or PCI has OWNER field with correct coding!!")

        # dissolving
        arcpy.AddMessage("Creating a new fc: %s..."%bmifc)
        arcpy.Dissolve_management(in_features="bmi_temp", out_feature_class=bmifc, dissolve_field="OWNER")
    unionList.append(bmifc)

    # deleting the temp file
    try:
        arcpy.Delete_management("bmi_temp")
    except:
        pass

# AR clear cuts
if len(arCC)>0:
    arCCfc = fmu.replace(' ','_') + '_ARcc'
    if arCCfc not in fcList:
        arcpy.AddMessage("Creating a new fc: %s"%arCCfc)
        arcpy.Dissolve_management(in_features=arCC, out_feature_class=arCCfc)
    unionList.append(arCCfc)

# AR Shelterwood
if len(arSH)>0:
    arSHfc = fmu.replace(' ','_') + '_ARsh'
    if arSHfc not in fcList:
        arcpy.AddMessage("Creating a new fc: %s"%arSHfc)
        arcpy.Dissolve_management(in_features=arSH, out_feature_class=arSHfc)
    unionList.append(arSHfc)

# AR Selection
if len(arSE)>0:
    arSEfc = fmu.replace(' ','_') + '_ARse'
    if arSEfc not in fcList:
        arcpy.AddMessage("Creating a new fc: %s"%arSEfc)
        arcpy.Dissolve_management(in_features=arSE, out_feature_class=arSEfc)
    unionList.append(arSEfc)

# Moose Winter Cover
if len(winterCov)>0:
    # Check if the layer has MooseWinterCover attribute.
    arcpy.AddMessage("Working on Moose Winter Cover...")
    wintCov_fieldList = [f.name for f in arcpy.ListFields(winterCov)]

    if "MooseWinterCover" in wintCov_fieldList:
        # Dissolving Winter Cover layer
        winterCovfc = fmu.replace(' ','_') + '_WintCov'
        if winterCovfc not in fcList:
            arcpy.Dissolve_management(in_features=winterCov, out_feature_class=winterCovfc, dissolve_field="MooseWinterCover", multi_part="SINGLE_PART", unsplit_lines="DISSOLVE_LINES") # changed MULTI_PART to SINGLE_PART

        # HVHC
        fc = fmu.replace(' ','_') + '_HVHC'
        whereClause = "MooseWinterCover = 'HVHC'"
        if fc not in fcList:
            arcpy.AddMessage("Creating a new fc: %s..."%fc)
            arcpy.FeatureClassToFeatureClass_conversion(in_features = winterCovfc, out_path= workspace, out_name=fc, where_clause= whereClause)
        else:
            arcpy.AddMessage("%s already exists."%fc)
        unionList.append(fc)

        # HVLC
        fc = fmu.replace(' ','_') + '_HVLC'
        whereClause = "MooseWinterCover = 'HVLC'"
        if fc not in fcList:
            arcpy.AddMessage("Creating a new fc: %s..."%fc)
            arcpy.FeatureClassToFeatureClass_conversion(in_features = winterCovfc, out_path= workspace, out_name=fc, where_clause= whereClause)
        else:
            arcpy.AddMessage("%s already exists."%fc)
        unionList.append(fc)

        # LVHC
        fc = fmu.replace(' ','_') + '_LVHC'
        whereClause = "MooseWinterCover = 'LVHC'"
        if fc not in fcList:
            arcpy.AddMessage("Creating a new fc: %s..."%fc)
            arcpy.FeatureClassToFeatureClass_conversion(in_features = winterCovfc, out_path= workspace, out_name=fc, where_clause= whereClause)
        else:
            arcpy.AddMessage("%s already exists."%fc)
        unionList.append(fc)

        # LVLC
        fc = fmu.replace(' ','_') + '_LVLC'
        whereClause = "MooseWinterCover = 'LVLC'"
        if fc not in fcList:
            arcpy.AddMessage("Creating a new fc: %s..."%fc)
            arcpy.FeatureClassToFeatureClass_conversion(in_features = winterCovfc, out_path= workspace, out_name=fc, where_clause= whereClause)
        else:
            arcpy.AddMessage("%s already exists."%fc)
        unionList.append(fc)

    else:
        # if "MooseWinterCover" attribute is not found
        arcpy.AddWarning("Can't find MooseWinterCover attribute in the input layer.\nYou will have to analyze Moose Winter Cover manually.")

################################################################################
###################          UNIONING ALL DATA       ###########################
################################################################################

# Unioning fcs created above using only FID
fcUnion = fmu.replace(' ','_') + '_fcUnion'
fcstring = ''

for i in unionList:
    fcstring += i + " #;"
fcstring = fcstring[:-1] # no need the semicolon for the last item.

if fcUnion in fcList:
    arcpy.AddMessage("Deleting old union file: %s..."%fcUnion)
    arcpy.Delete_management(fcUnion) # delete and re-create if such union file already exists

arcpy.AddMessage("Creating a new fc: %s..."%fcUnion)
arcpy.AddMessage("Unioning the following feature classes: \n%s"%unionList)
arcpy.Union_analysis(in_features=fcstring, out_feature_class= fcUnion, join_attributes="ONLY_FID", cluster_tolerance="", gaps="GAPS")




# Union the above fc to the candidate MEA

meaTemp1 = fmu.replace(' ','_') + '_meaTemp1'
meaTemp2 = fmu.replace(' ','_') + '_meaTemp2'
meaTemp3 = fmu.replace(' ','_') + '_meaTemp3'

try:
    arcpy.Delete_management(meaTemp1) # making sure these temp files are not already there
    arcpy.Delete_management(meaTemp2)
    arcpy.Delete_management(meaTemp3)
except:
    pass

# meaTemp1
# need to union candidatefc with itself with "NO_GAPS". (this is to fill the donut holes with FID -1)
arcpy.AddMessage("Self unioning the MEA candidate to fill the donut hole...")
arcpy.Union_analysis(in_features= candidatefc + ' #', out_feature_class= meaTemp1, join_attributes="ONLY_FID", cluster_tolerance="", gaps="NO_GAPS") # no gaps - this will actually allow having gaps


# meaTemp2
arcpy.AddMessage("Unioning the information to the candidate MEA...")
arcpy.Union_analysis(in_features= fcUnion + ' #;' + meaTemp1 + ' #', out_feature_class= meaTemp2, join_attributes="ALL", cluster_tolerance="", gaps="GAPS") # no gaps - this will actually allow having gaps


# meaTemp3 - we only need information within the MEA candidate area
whereClause = "FID_" + candidatefc + " > 0"  ## for example, "FID_Nipissing_MEA_Candidate > 0"
arcpy.AddMessage("Deleting spatial information outside the MEA candidate area...")
arcpy.FeatureClassToFeatureClass_conversion(in_features=meaTemp2, out_path= workspace, out_name= meaTemp3, where_clause= whereClause)


# calculating areas (this will create a new field called "AREA_GEO")
arcpy.AddMessage("Calculating area of individual polygons of the union output...")
arcpy.AddGeometryAttributes_management(Input_Features=meaTemp3, Geometry_Properties="AREA_GEODESIC", Length_Unit="", Area_Unit="HECTARES", Coordinate_System="PROJCS['MNR_Lambert_Conformal_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',930000.0],PARAMETER['False_Northing',6430000.0],PARAMETER['Central_Meridian',-85.0],PARAMETER['Standard_Parallel_1',44.5],PARAMETER['Standard_Parallel_2',53.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]")

# Creating new fields and populating them with the area calculated above
areaHaFields = []
arcpy.AddMessage("Adding new fields for area population...")
for i in unionList:
    fieldname = i + '_AreaHa'
    arcpy.AddMessage("Working on " + fieldname)
    try:
        arcpy.AddField_management(in_table = meaTemp3, field_name = fieldname, field_type = "FLOAT")
        arcpy.CalculateField_management(in_table= meaTemp3, field= fieldname, expression="populateArea( !FID_" + i + "!, !AREA_GEO! )", expression_type="PYTHON_9.3", code_block="def populateArea(x, areageo):\n  if x>0:\n    return areageo\n  else:\n    return 0")
    except:
        arcpy.AddMessage("Could not add a new field: %s"%fieldname)
    areaHaFields.append(fieldname) ## for example, ["Nipissing_MAFA34_AreaHa", ...]


# Use dissolve to turn them back into MEA candidate area with summarized area fields

meaFinal = fmu.replace(' ','_') + '_MEA_AreaAnalysis'
arcpy.AddMessage("Repairing self-intersecting polygons...")

arcpy.RepairGeometry_management(in_features=meaTemp3, delete_null="DELETE_NULL")    # Reparing geometry - if skip this part, some self-intersecting polygons won't dissolve correctly

arcpy.AddMessage("Dissolving and summarizing...")
try:
    arcpy.Delete_management(meaFinal)
except:
    pass

statField = ''
for i in areaHaFields:
    statField += i + " SUM;"
statField = statField[:-1] ## to remove the last semicolon

arcpy.Dissolve_management(in_features=meaTemp3, out_feature_class=meaFinal, dissolve_field="FID_"+ candidatefc, statistics_fields=statField, multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")


# Calculating area of each MEA candidate in ha (this will create a new field called "AREA_GEO")
arcpy.AddGeometryAttributes_management(Input_Features=meaFinal, Geometry_Properties="AREA_GEODESIC", Length_Unit="", Area_Unit="HECTARES", Coordinate_System="PROJCS['MNR_Lambert_Conformal_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',930000.0],PARAMETER['False_Northing',6430000.0],PARAMETER['Central_Meridian',-85.0],PARAMETER['Standard_Parallel_1',44.5],PARAMETER['Standard_Parallel_2',53.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]")


# Add new fields for area percent calculation and populate them

for i in unionList:
    areaHa = i + "_AreaHa"
    areaPercent = i + "_AreaPercent"
    try:
        arcpy.AddMessage("Adding and populating new fields:\n%s, %s"%(areaHa, areaPercent))

        arcpy.AddField_management(in_table = meaFinal, field_name = areaHa, field_type = "FLOAT")
        arcpy.CalculateField_management(in_table= meaFinal, field= areaHa, expression="!SUM_" + areaHa + "!", expression_type="PYTHON_9.3", code_block="")
        arcpy.DeleteField_management(meaFinal, "SUM_" + areaHa)

        arcpy.AddField_management(in_table = meaFinal, field_name = areaPercent, field_type = "FLOAT")
        arcpy.CalculateField_management(in_table= meaFinal, field= areaPercent, expression="(!" + areaHa + "!/!AREA_GEO!) * 100", expression_type="PYTHON_9.3", code_block="")
    except:
        arcpy.AddMessage("ERROR: Could not add new fields: %s, %s"%(areaHa, areaPercent))

arcpy.AddMessage("Finalizing...")
totAreaF = "MEA_Total_AreaHa"
arcpy.AddField_management(in_table = meaFinal, field_name = totAreaF, field_type = "FLOAT")
arcpy.CalculateField_management(in_table= meaFinal, field= totAreaF, expression="!AREA_GEO!", expression_type="PYTHON_9.3", code_block="")
arcpy.DeleteField_management(meaFinal, "AREA_GEO")

# deleting temp files
if not testing:
    try:
        arcpy.Delete_management(meaTemp1) # delete temporary files
        arcpy.Delete_management(meaTemp2)
        arcpy.Delete_management(meaTemp3)
    except:
        pass


arcpy.AddMessage("\nDone!!\nYour final product feature class is %s.\n"%meaFinal)


