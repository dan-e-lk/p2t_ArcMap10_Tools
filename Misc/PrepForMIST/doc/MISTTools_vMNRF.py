# ------------------------------------------------------------------------------
#                   Tembec Forest Resource Management
# ------------------------------------------------------------------------------
# Name:        MISTTools
# Purpose:     Toolbox designed to shoehorn a 2017 FIM compliant eFRI into MIST
#
# Author:      grant.mccartney
#
# Created:     12/03/2018
# Copyright:   (c) grant.mccartney 2018
#-------------------------------------------------------------------------------
# Notes:
#
# ------------------------------------------------------------------------------
#  History:    Grant McCartney     12/03/2018 - initial code
#               Daniel Kim          14/03/2018 - minor updates
#
# ==============================================================================

print('importing arcpy...')
import os, arcpy


def CopyMistBMI(inForest):
    arcpy.MakeFeatureLayer_management(inForest, "bmiLyr",)
    arcpy.SelectLayerByAttribute_management("bmiLyr", "NEW_SELECTION", "POLYTYPE = 'FOR' AND OWNER IN ('1', '5', '7') AND DEVSTAGE NOT IN ('DEPHARV', 'DEPNAT', 'NEWNAT', 'NEWPLANT', 'NEWSEED')")
    stands = arcpy.GetCount_management("bmiLyr")
    print ("{0} stands are being copied to a MIST inventory file".format(stands)),
    arcpy.CopyFeatures_management ("bmiLyr", "mistbmi")
    print ("mistbmi feature class created")

    if arcpy.Exists("mistbmi"):
        inForest = os.path.join(WS,"mistbmi")

    print inForest





################################################################################
def MISTFields(inForest):

    fields = [f.name for f in arcpy.ListFields(inForest)]

    print ("Current bmi Fields: {0}".format(fields))

    print
    if "AGESTR" not in fields:
        arcpy.AddField_management(inForest, "AGESTR", "TEXT", "", "", 1)

    if "AREA" not in fields:
        arcpy.AddField_management(inForest, "AREA", "DOUBLE")

    if "CCLOSTKG" not in fields:
        arcpy.AddField_management(inForest, "CCLOSTKG", "DOUBLE")

    if "ECOPCT1" not in fields:
        arcpy.AddField_management(inForest, "ECOPCT1", "SHORT")

    if "ECOSITE1" not in fields:
        arcpy.AddField_management(inForest, "ECOSITE1", "TEXT", "", "", 10 )

    if "ECOSRC" not in fields:
        arcpy.AddField_management(inForest, "ECOSRC", "TEXT", "", "", )

    if "SI" not in fields:
        arcpy.AddField_management(inForest, "SI", "TEXT", "", "", 5)

    if "SISRC" not in fields:
        arcpy.AddField_management(inForest, "SISRC", "TEXT", "", "", 8)

    if "WG" not in fields:
        arcpy.AddField_management(inForest, "WG", "TEXT", "", "", 2)





def MIST_DataPrep(inForest):
    """Translates 2017 FIM BMI to meet MIST (FIM 2009) validation requirements

"""

    fields = [f.name for f in arcpy.ListFields(inForest)]
    print fields

    with arcpy.da.UpdateCursor(inForest, ["SOURCE", "POLYTYPE", "DEVSTAGE", "AGESTR", "LEADSPC", "STKG", "AGE", "ECOSRC", "ECOSITE1", "ECO", "SEC_ECO", "ECOPCT1", "SISRC", "YIELD", "SI", "AREA", "Shape_Area", "SMZ" ], ) as cursor:
        for row in cursor:
#SOURCE
##########################
#set DIGITALP to DIGITAL

#set SUPINFO to PLOTFIXD
###########################
#MANAGED AND AVAIL | DONE IN BMITools
#ACCESS* | DONE IN BMITools

#DEVSTAGE
            if row[1] == "FOR":
                if row[2] in ("NAT", "ESTNAT"): #NAT & ESTNAT
                    row[2] = "FTGNAT"

                if row[2] == "ESTPLANT":    #ESTPLANT
                    row[2] = "FTGPLANT"

                if row[2] == "ESTSEED":    #ESTSEED
                    row[2] = "FTGSEED"



#AGESTR
            if row[1] == "FOR":
                row[3] = "E"

#SILVSYS | DONE IN BMITools

#LEADSPC
            if row[1] == "FOR":

                if row[4] == "Ab":
                    row[4] = "AX"

                if row[4] == "Bd":
                    row[4] = "OH"

                if row[4] == "Cw":
                    row[4] = "Ce"

                if row[4] == "Ew":
                    row[4] = "OH"

                if row[4] == "Ob":
                    row[4] = "OH"

                if row[4] == "Pl":
                    row[4] = "PO"

                if row[4] == "Pb":
                    row[4] = "PO"

                if row[4] == "Pt":
                    row[4] ="PO"

                if row[4] =="Sn":
                    row[4] = "SX"

#WG
#NEED SECOND CURSOR TO SET LEADSPC CHANGES ABOVE

#STKG
#3902 records > 2.5
#Many of the highly stocked stands (2.5-4) are PLOTVAR DATA
#these same high stocked records over 4 that were adjusted during BMITools

#Garnet's SQL selects all stands greater than 2.5 and sets them to 1....
#SHOULD THEY BE 2.5?
            if row[5] > 2.5:
                #row[5] = 1
                row[5] = 2.5


#SC | DONE
#YRORG
#YRUPD
#AGE
#3 stands were grown past 250 years old
# original ages are 240, 241 YRORG = 1767, 1768

            if row[1] == "FOR":
                if row[6] > 250:
                    row[6] = 250

#ECOSRC **IS THIS REQUIRED?
            row[7] = row[0]

#ECOSITE1
            row[8] = row[9]

#ECOPCT1
            if row[10] is not None:
                row[11] = 90
            else:
                row[11] = 100

#SISCR
            if row[1] == "FOR":
                row[12] = "ASSIGNED"
#SI
            if row[1] == "FOR":
                if row[13] == "PRSNT2":
                    row[14] = "PRNT2"
                else:
                    row[14] = row[13]
#AREA
            row[15] = row[16]

#SMZ
            row[17] = "GCF"

            cursor.updateRow(row)
    del cursor

    with arcpy.da.UpdateCursor(inForest, ["LEADSPC", "WG"]) as cursor:
        for row in cursor:
            WG = row[0]
            row[1] = WG.upper()

            cursor.updateRow(row)



if __name__ == '__main__':


    """User input and workspace setting """
    #Ask user for input forest inventory
    inForest = r'C:\DanielK_Workspace\FMP_LOCAL\Gordon_Cosens\BMI_20180311.gdb\MU438_20BMI00'



    WS = os.path.dirname(inForest)
    print ("Setting workspace environment to: {0}").format(WS)    
    arcpy.env.workspace = WS

    print("making a copy of the input..")
    CopyMistBMI(inForest)

    print ("Building MIST Inventory...")
    MISTFields(inForest)


    MIST_DataPrep(inForest)


    print ("DONE!")
