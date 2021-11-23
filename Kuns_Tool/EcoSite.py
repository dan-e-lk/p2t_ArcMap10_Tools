fc = arcpy.GetParameterAsText(0)
ECOField = arcpy.GetParameterAsText(1)
BeginWith = ECOField[0:3]
import arcpy
NewField = [BeginWith+"Geo", BeginWith+"EcoNu",BeginWith+"Vege",BeginWith+"Depth",BeginWith+"Moist",BeginWith+"Chem",BeginWith+"Class",BeginWith+"EcoKey"]
depValue = ["R","S","VS","M","D","MD"]
moisValue = ["d","f","h","m","s","v","w","x"]
chemValue = ["a","b","k","n","z"]
classValue = ["Tt","cTt","oTt","sTt","Tl","sTl","St","sSt","Sl","sSl","H","sH","Nv","X"]
for field in NewField:
    arcpy.AddField_management(fc, field, "TEXT")
NewField.append(ECOField)
print NewField
cursor = arcpy.da.UpdateCursor(fc,NewField)
for row in cursor:
    if (row[8] is not None) and (row[8].isspace() == False):
        row[0] = row[8][0]
        row[1] = row[8][1:4]
        if int(row[1]) <= 7:
            row[7] = "2"
        elif int(row[1]) <= 28:
            row[7] = "3"
        elif int(row[1]) <= 43:
            row[7] = "4"
        elif int(row[1]) <= 59:
            row[7] = "5"
        elif int(row[1]) <= 76:
            row[7] = "6"
        elif int(row[1]) <= 92:
            row[7] = "7"
        elif int(row[1]) <= 108:
            row[7] = "8"
        elif int(row[1]) <= 125:
            row[7] = "9"
        elif int(row[1]) <= 156:
            row[7] = "10"
        elif int(row[1]) <= 188:
            row[7] = "11"
        elif int(row[1]) <= 200:
            row[7] = "12a"
        elif int(row[1]) <= 221:
            row[7] = "13"
        elif int(row[1]) <= 224:
            row[7] = "10"
        else: 
            row[7] = "12b"
        if len(row[8]) > 4: 
            if row[8][4:] == "X":
                row[2] = row[8][4:]
            else:
                row[2] = row[8][4:6]
                if len(row[8]) > 6:
                    for i in depValue:
                        if i in row[8][6:]:
                            row[3] = i
                    for i in moisValue:
                        if i in row[8][6:]:
                            row[4] = i
                    for i in chemValue:
                        if i in row[8][6:]:
                            row[5] = i
                    for i in classValue:
                        if i in row[8][6:]:
                            row[6] = i
        cursor.updateRow(row)
del row
del cursor 
