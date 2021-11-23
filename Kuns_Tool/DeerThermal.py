fc = arcpy.GetParameterAsText(0)
Stkg = arcpy.GetParameterAsText(1)
Ht = arcpy.GetParameterAsText(2)
NewField= ["Grp1","Grp2","Grp3","Cov_Rank"]
for field in NewField:
    arcpy.AddField_management(fc, field, "FLOAT")
arcpy.AddField_management(fc, "CR_Temp", "FLOAT")
NewField.extend(("BF","CE","HE","SR","SW",Stkg,"SB","PR","PJ","PW","CW","SX",Ht,"CR_Temp"))
cursor = arcpy.da.UpdateCursor(fc,NewField)
for row in cursor:
    row[0] = (row[4]+ row[5] + row[6] + row[7] + row[8]+ row[14] + row[15]) * row[9]
    row[1] = (row[4]+ row[5] + row[6] + row[7] + row[8]+ row[14] + row[15] + row[10] + row[13]) * row[9]
    row[2] = (row[4]+ row[5] + row[6] + row[7] + row[8]+ row[14] + row[15] + row[10] + row[13] + row[11] + row[12]) * row[9]
    if row[16] >= 10:
        if row[2] > 0:
            row[3] = 1 
        if row[2] >= 30:
            row[3] = 2 
        if row[1] >= 30:
            row[3] = 3 
        if row[0] >= 30:
            row[3] = 4 
        if row[2] >= 60:
            row[3] = 5 
        if row[2] >= 60 and row[1] >= 30:
            row[3] = 6 
        if row[2] >= 60 and row[1] >= 60:
            row[3] = 7 
        if row[2] >= 60 and row[1] >= 30 and row[0] >= 30:
            row[3] = 8
        if row[2] >= 60 and row[1] >= 60 and row[0] >= 30:
            row[3] = 9 
        if row[2] >= 60 and row[1] >= 60 and row[0] >= 60:
            row[3] = 10 
    if row[16] >= 3:
        if (row[5] + row[6] + row[14]) * row[9] >= 30 and row[16] >= 5:
            row[17] = 5
        if ((row[5] + row[14]) * row[9]) >= 50 and row[16] >= 3:
            row[17] = 6
	if ((row[5] + row[14]) * row[9]) >= 60 and row[16] >= 3:
            row[17] = 7
        if ((row[5] + row[14]) + row[6]) * row[9] >= 60 and row[16] >= 3:
            row[17] = 7
	if row[3] < row[17]:
            row[3] = row[17]
    cursor.updateRow(row)
del row
del cursor 
