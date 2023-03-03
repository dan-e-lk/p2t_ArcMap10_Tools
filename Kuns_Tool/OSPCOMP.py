# this script works best with Shapefiles

fc = arcpy.GetParameterAsText(0)
forestCompField = arcpy.GetParameterAsText(1)
PolyTypeField = arcpy.GetParameterAsText(2)
ObjectIDField = arcpy.GetParameterAsText(3)
SCfield = arcpy.GetParameterAsText(4)
STKG = arcpy.GetParameterAsText(5)
FullSpecieslist = ["AB", "AW", "AX","BD","BE","BF","BN","BW","YB","CB","CE","CH","CW","EW","EX","HE","HI","IW","LA","MH","MR","MS","OB","RO","OW","PB","PL","PJ","PO","PR","PT","PW","SB","SR","SW","SX"]
NewAddedSpecies = ["OH","PS","SN","CR","MX","OC","OX","PX"]
import arcpy
from itertools import groupby
for specie in FullSpecieslist:
    arcpy.AddField_management(fc, specie, "FLOAT")
    #arcpy.CalculateField_management(fc, specie, 0)
arcpy.AddField_management(fc, "SFU", "TEXT")
arcpy.AddMessage("Done with adding all the fields!")
FullSpecieslist.extend(("SFU",SCfield,ObjectIDField,PolyTypeField,STKG,forestCompField,"OH","PS","SN","CR","MX","OC","OX","PX"))
for specie in NewAddedSpecies:
    arcpy.AddField_management(fc, specie, "FLOAT")
    arcpy.CalculateField_management(fc, specie, 0) # uncommented this line
expression = arcpy.AddFieldDelimiters(fc,PolyTypeField) + " = 'FOR'"
cursor = arcpy.da.UpdateCursor(fc,FullSpecieslist,expression)
for row in cursor:
    if row[41] is None:
        arcpy.AddWarning ("Poly ID {0} species comp field has Null value".format(row[38]))
    elif row[41].isspace == True:
        arcpy.AddWarning ("Poly ID {0} species comp field has no character".format(row[38]))
    else:
        if len(row[41])%6 != 0:
            arcpy.AddWarning ("Poly ID {0} is not formatted properly".format(row[38]))
        n = 3
        aList=[]
        for k,g in groupby(str(row[41]),str.isalpha):
            aList.append((''.join(list(g))).replace(" ",""))
        for element in aList:
            bIndex = aList.index(element)
            j = element.replace(" ","")
            if j.isalpha() == True:
                if (j.lower() != "by") and (j.upper() not in FullSpecieslist) and (j.lower() != "or" ):
                    arcpy.AddWarning ("Poly ID {0} has specie {1} not in sql list.".format(row[38],j))
                else:
                    if j.lower() == "by":
                        j = "YB"
                    elif j.lower() == "or":
                        j ="RO"
                    aIndex = FullSpecieslist.index(j.upper())
                    row[aIndex] = float(aList[bIndex+1])
        if (row[29]>=70) and (row[31]<30):
            row[36] = "PR"
        elif (row[31]+row[29]>=50) and (row[31]>row[29]) and ((row[31]+row[29])*row[40] >=30) and (row[23]+row[22]+row[24]<20):
            row[36] = "PWUS4"
        elif (row[31]+row[29]+row[23]+row[24]+row[22]>=50) and (row[31]>=row[23]+row[22]+row[24]) and ((row[31]+row[29]+row[23]+row[22]+row[24])*row[40] >=30) and (row[23]+row[22]+row[24]>=20):
            row[36] = "PWOR"
        elif (row[31]+row[29]>=30) and ((row[31]+row[29])*row[40] >=30):
            row[36] = "PWUSC"
        elif ( (row[31]>=row[15]) and (row[31]>=row[34]) and (row[31]>(row[10]+row[12])) and (row[31]>=row[23]) and ((row[31]+row[29]) >=30) and ((row[31]+row[29]+row[34]+row[15]+row[23]+row[27]+row[10]+row[12])*row[40] >=30)) and ((row[31]+row[29]+row[27]+row[34]+row[32]+row[33]+row[35]+row[15]+row[5]+row[10]+row[12]+row[18])>=80):
            row[36] = "PWUSC"
        elif (row[31]>=row[29]) and ((row[31]+row[29])>=30) and ((row[31]+row[29])*row[40] >=30):
            row[36] = "PWUSH"
        elif (row[31]>=row[29]) and (row[31]>=row[15]) and (row[31]>=row[34]) and (row[31]>(row[10]+row[12])) and (row[31]>=row[23])  and (row[31]+row[29]>=30) and ((row[31]+row[29]+row[34]+row[15]+row[23]+row[27]+row[10]+row[12])*row[40] >=30) and (row[31]+row[29]+row[27]+row[34]+row[33]+row[35]+row[32]+row[15]+row[5]+row[10]+row[12]+row[18] <80):
            row[36] = "PWUSH"
        elif (row[31]+row[29]>=30) and (row[31]+row[29]>=row[15]) and (row[31]+row[29]>=row[34]) and (row[31]+row[29]>=row[32]+row[33]+row[35]) and (row[31]+row[29]>=(row[10]+row[12])) and (row[31]+row[29]>=row[23]):
            row[36] = "PWST"
        elif (row[27]>=70) and (row[19]+row[0]+row[1]+row[3]+row[4]+row[11]+row[13]+row[17]+row[23]+row[8]+row[24]+row[22]+row[28]+row[30]+row[25]+row[26]+row[7]+row[20]+row[21]+row[2]+row[9]+row[14]+row[16]+row[6]<=20):
            row[36] = "PJ1"
        elif (((row[27]+row[32]+row[33]+row[35]+row[29]>=70) or ((row[27]>=50) and (row[27]+row[32]+row[33]+row[35]+row[5]+row[34]+row[15]+row[31]+row[29]+row[10]+row[12]+row[18]>=70) and (row[5]+row[34]+row[15]+row[31]+row[10]+row[12]+row[18]<=20))) and (row[27]>=row[32]+row[33]+row[35])):
            row[36] = "PJ2"
        elif (row[15]>=40): 
            row[36] = "HE"
        elif (row[10]+row[12]>=40) and ((row[10]+row[12])>=row[32]+row[33]+row[35]+row[18]+row[5]) and (row[24]+row[22]+row[13]+row[17]+row[11]+row[19]+row[0]+row[1]+row[3]+row[4]+row[23]+row[8]+row[28]+row[25]+row[30]+row[26]+row[7]+row[20]+row[21]+row[14]+row[9]+row[2]+row[16]+row[6]<30):
            row[36] = "CE"
        elif (row[32]+row[33]+row[35]>=80) and (row[19]+row[1]+row[3]+row[4]+row[11]+row[17]+row[23]+row[24]+row[22]+row[8]+row[29]+row[6]+row[16]+row[9]==0) and (row[31]+row[27]<=10):
            row[36] = "SB"
        elif (row[32]+row[35]+row[33]+row[10]+row[12]+row[18]>=80) and (row[19]+row[1]+row[3]+row[4]+row[11]+row[17]+row[23]+row[24]+row[22]+row[8]+row[29]+row[9]+row[16]+row[6]==0) and (row[31]+row[27]<=10):
            row[36] = "LC"
        elif (row[32]+row[34]+row[33]+row[35]+row[5]+row[10]+row[12]+row[18]+row[31]+row[27]+row[29]+row[15]>=70) and ((row[5]+row[10]+row[12]+row[31]+row[18]+row[34]+row[15]<=20) or (row[27]>=30)):
            row[36] = "SP1"
        elif (row[34]+row[33]+row[32]+row[35]+row[31]+row[29]+row[27]+row[5]+row[10]+row[12]+row[18]+row[15]>=70):
            row[36] = "SF"
        elif (row[8]>=40):
            row[36] = "BY"
        elif (row[23]>=row[19]+row[4]) and (row[23]>=30) and (row[23]+row[19]+row[1]+row[0]+row[4]+row[3]+row[8]+row[31]+row[29]+row[34]+row[15]+row[2]>=40):
            row[36] = "OAK"
        elif ((row[3]+row[1]+row[11]+row[23]+row[24]+row[22]+row[9]>=30) or ((row[4]+row[23]+row[24]+row[22]>=30) or (row[4]>=20))):
            row[36] = "HDSL2"
        elif (row[19]+row[1]+row[3]+row[4]+row[11]+row[13]+row[17]+row[23]+row[8]+row[24]+row[22]+row[15]+row[14]+row[9]>=50) and (row[28]+row[30]+row[25]+row[26]+row[7]+row[5]<=30) and (row[37] <= 2):
            row[36] = "HDSL1"
        elif (row[10]+row[12]+row[0]+row[18]+row[32]+row[2]+row[33]+row[35]>=30) and ((row[0]+row[2]>=20) or (row[0]+row[2]+row[20]+row[21]+row[8]>=30)):
            row[36] = "LWMW"
        elif (row[19]+row[1]+row[3]+row[4]+row[11]+row[13]+row[17]+row[23]+row[8]+row[24]+row[22]+row[15]+row[9]+row[16]+row[14]+row[6]>=50):
            row[36] = "HDUS"
        elif (row[28]+row[30]+row[25]+row[26]>=50) and (row[19]+row[0]+row[1]+row[3]+row[4]+row[11]+row[13]+row[17]+row[23]+row[8]+row[24]+row[22]+row[28]+row[25]+row[30]+row[26]+row[7]+row[20]+row[21]+row[2]+row[6]+row[9]+row[14]+row[16]>=70): 
            row[36] = "PO"
        elif (row[28]+row[30]+row[25]+row[26]+row[7]>=50) and (row[19]+row[0]+row[1]+row[3]+row[4]+row[11]+row[13]+row[17]+row[23]+row[8]+row[24]+row[22]+row[28]+row[30]+row[25]+row[26]+row[7]+row[20]+row[21]+row[2]+row[6]+row[9]+row[14]+row[16]>=70):
            row[36] = "BW"
        elif ((row[34]+row[31]+row[29]+row[10]+row[12]+row[19]+row[8]+row[1]+row[11]+row[3]+row[23]+row[24]+row[22]+row[17]+row[4]+row[15]+row[9]+row[16]+row[6])*row[40]>=30):
            row[36] = "MWUS"
        elif (row[27]+row[31]+row[29]>=20):
            row[36] = "MWD"
        else:
            row[36] = "MWR"
        cursor.updateRow(row)
del row
del cursor  
