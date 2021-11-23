fc = arcpy.GetParameterAsText(0)
SCfield = arcpy.GetParameterAsText(1)
ObjectIDField = arcpy.GetParameterAsText(2)
PolyTypeField = arcpy.GetParameterAsText(3)
STKG = arcpy.GetParameterAsText(4)
Age = arcpy.GetParameterAsText(5)
FullFieldlist = ["AB", "AW", "AX","BD","BE","BF","BN","BW","YB","CB","CE","CH","CW","EW","EX","HE","HI","IW","LA","MH","MR","MS","OB","RO","OW","PB","PL","PJ","PO","PR","PT","PW","SB","SR","SW","SX","OH","PS","SN","CR","MX","OC","OX","PX",SCfield,ObjectIDField,PolyTypeField,STKG,Age,"BaArea"]
import arcpy
arcpy.AddField_management(fc, "BaArea", "FLOAT")
expression = arcpy.AddFieldDelimiters(fc,PolyTypeField) + " = 'FOR'"
cursor = arcpy.da.UpdateCursor(fc,FullFieldlist,expression)
from BaTable import BaInfo
for row in cursor:
    # Set variables
    AB = row[0]
    AW = row[1]
    AX = row[2]
    BD = row[3]
    BE = row[4]
    BF = row[5]
    BN = row[6]
    BW = row[7]
    YB = row[8]
    CB = row[9]
    CE = row[10]
    CH = row[11]
    CW = row[12]
    EW = row[13]
    EX = row[14]
    HE = row[15]
    HI = row[16]
    IW = row[17]
    LA = row[18]
    MH = row[19]
    MR = row[20]
    MS = row[21]
    OB = row[22]
    RO = row[23]
    OW = row[24]
    PB = row[25]
    PL = row[26]
    PJ = row[27]
    PO = row[28]
    PR = row[29]
    PT = row[30]
    PW = row[31]
    SB = row[32]
    SR = row[33]
    SW = row[34]
    SX = row[35]
    OH = row[36]
    PS = row[37]
    SN = row[38]
    CR = row[39]
    MX = row[40]
    OC = row[41]
    OX = row[42]
    PX = row[43]
    if row[48]%5 <> 0:
        to5 = 5 - row[48]%5
    else:
        to5 = 0
    ac5 = row[48] + to5
    if ac5 > 255:
        ac5 = 255
    SCAC = str(row[44]) + str(ac5)
    BaPW = BaInfo[SCAC][0]
    BaPR = BaInfo[SCAC][1]
    BaPJ = BaInfo[SCAC][2]
    BaSB = BaInfo[SCAC][3]
    BaSW = BaInfo[SCAC][4]
    BaOC = BaInfo[SCAC][5]
    BaHE = BaInfo[SCAC][6]
    BaPO = BaInfo[SCAC][7]
    BaBW = BaInfo[SCAC][8]
    BaOH = BaInfo[SCAC][9]
    STKGvalue = row[47]/100
    Ba = 0
    # end of Setting variables

    # Start calculation
    if AB <> 0:
        Ba = Ba+ AB * STKGvalue * BaOH 
    if AW <> 0:
        Ba = Ba+ AW * STKGvalue * BaOH
    if AX <> 0:
        Ba = Ba+ AX * STKGvalue * BaOH
    if BD <> 0:
        Ba = Ba+ BD * STKGvalue * BaOH
    if BE <> 0:
        Ba = Ba+ BE * STKGvalue * BaOH
    if BF <> 0:
        Ba = Ba+ BF * STKGvalue * BaSB
    if BN <> 0:
        Ba = Ba+ BN * STKGvalue * BaOH
    if BW <> 0:
        Ba = Ba+ BW * STKGvalue * BaBW
    if YB <> 0:
        Ba = Ba+ YB * STKGvalue * BaOH
    if CB <> 0:
        Ba = Ba+ CB * STKGvalue * BaOH
    if CE <> 0:
        Ba = Ba+ CE * STKGvalue * BaSB
    if CH <> 0:
        Ba = Ba+ CH * STKGvalue * BaOH
    if CR <> 0:
        Ba = Ba+ CR * STKGvalue * BaSB
    if CW <> 0:
        Ba = Ba+ CW * STKGvalue * BaSB
    if EW <> 0:
        Ba = Ba+ EW * STKGvalue * BaOH
    if EX <> 0:
        Ba = Ba+ EX * STKGvalue * BaOH
    if HE <> 0:
        Ba = Ba+ HE * STKGvalue * BaHE
    if HI <> 0:
        Ba = Ba+ HI * STKGvalue * BaOH
    if IW <> 0:
        Ba = Ba+ IW * STKGvalue * BaOH
    if LA <> 0:
        Ba = Ba+ LA * STKGvalue * BaPJ
    if MH <> 0:
        Ba = Ba+ MH * STKGvalue * BaOH
    if MR <> 0:
        Ba = Ba+ MR * STKGvalue * BaOH
    if MS <> 0:
        Ba = Ba+ MS * STKGvalue * BaOH
    if MX <> 0:
        Ba = Ba+ MX * STKGvalue * BaOH
    if OB <> 0:
        Ba = Ba+ OB * STKGvalue * BaOH
    if OC <> 0:
        Ba = Ba+ OC * STKGvalue * BaSB
    if OH <> 0:
        Ba = Ba+ OH * STKGvalue * BaOH
    if RO <> 0:
        Ba = Ba+ RO * STKGvalue * BaOH
    if OW <> 0:
        Ba = Ba+ OW * STKGvalue * BaOH
    if OX <> 0:
        Ba = Ba+ OX * STKGvalue * BaOH
    if PB <> 0:
        Ba = Ba+ PB * STKGvalue * BaPO
    if PJ <> 0:
        Ba = Ba+ PJ * STKGvalue * BaPJ
    if PL <> 0:
        Ba = Ba+ PL * STKGvalue * BaPO
    if PO <> 0:
        Ba = Ba+ PO * STKGvalue * BaPO
    if PR <> 0:
        Ba = Ba+ PR * STKGvalue * BaPR
    if PS <> 0:
        Ba = Ba+ PS * STKGvalue * BaPR
    if PT <> 0:
        Ba = Ba+ PT * STKGvalue * BaPO
    if PW <> 0:
        Ba = Ba+ PW * STKGvalue * BaPW
    if PX <> 0:
        Ba = Ba+ PX * STKGvalue * BaPW
    if SB <> 0:
        Ba = Ba+ SB * STKGvalue * BaSB
    if SN <> 0:
        Ba = Ba+ SN * STKGvalue * BaSB
    if SR <> 0:
        Ba = Ba+ SR * STKGvalue * BaSB
    if SW <> 0:
        Ba = Ba+ SW * STKGvalue * BaSW
    if SX <> 0:
        Ba = Ba+ SX * STKGvalue * BaSW
    row[49] = Ba
    cursor.updateRow(row)
del row
del cursor  
