# This script requires fmptable1_sample.html saved in the same folder as this script.
# Updated addtion of SEEDTREE on BelowRegen and Forest Stands


import arcpy
import os, datetime, webbrowser, inspect
import FMP_Table_Functions as ftf


############     defining primary parameters    ############

inputbmi = arcpy.GetParameterAsText(0)
outputfolder = arcpy.GetParameterAsText(1)
fu_field = arcpy.GetParameterAsText(2)

############   defining secondary parameters    ############
age_increment = [
(0,20),
(21,40),
(41,60),
(61,80),
(81,100),
(101,120),
(121,140),
(141,160),
(161,180),
(181,200),
(201,999)] # must have at least 2 age groups for the html to work properly

ftf.logger("\nAge increment values:\n%s"%age_increment,'info')

prot_for_sql = """ "FORMOD" = 'PF' """  # protection forest
prod_for_sql = """ "FORMOD" in ('RP','MR') """  # production forest
unavailable_sql = """ "AVAIL" = 'U' """
available_sql = """ "AVAIL" = 'A' """
dev_field = "NEXTSTG" # the values of this field will be used to populated stage of development column.

manFields = ['POLYTYPE', 'AGE', 'FORMOD','AVAIL', dev_field, fu_field] # !!!!!!!! This is the list of fields used in the below list of SQLs

############             Script Body            ############

# Checking if the input PCI has all the fields needed to create the FMP1 table
ftf.logger("\nChecking mandatory fields...")

existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputbmi)]

existingManFields = list(set(manFields)&set(existingFields))
if len(existingManFields) != len(manFields):
    ftf.logger("\nMISSING MANDATORY FIELD(S)! \nYour input file must include the following fields:\n%s"%manFields, 'critical')

if 'SHAPE_AREA' in existingFields:
    AreaField = 'SHAPE_AREA'
    manFields.append('SHAPE_AREA')
elif 'AREA' in existingFields:
    AreaField = 'AREA'
    manFields.append('AREA')    
else:
    ftf.logger("\nMISSING MANDATORY FIELD! \nYour input file must have either 'Shape_Area' field or 'Area' field.\n", 'critical')

# creating the report html file on the output folder as specified above.
today = datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')
bmi_filename = os.path.split(inputbmi)[1]
reportfilename = "FMP3Table_%s_%s.html"%(bmi_filename, today) # eg. FMP3Table_MU210_20PCI00_2017-10-10.html
reportfile = os.path.join(outputfolder, reportfilename)
rep = open(reportfile,'w')

# Copying the html code from FMP_Table_Functions.py
htmlstring = ftf.head_str.replace("*FMPFileName",inputbmi) # css/style and the h1 title

# creating a unique list(set) of forest units.
fu_set = set()
with arcpy.da.SearchCursor(inputbmi,[fu_field],'''"POLYTYPE" = 'FOR' and "''' + fu_field + '''" is not Null''') as cursor:
    for row in cursor:
        fu_set.add(str(row[0]))

fu_list = list(sorted(fu_set))        
ftf.logger("\nList of forest units found:\n%s"%fu_list)


# we will consolidate the information in the form of a dictionary before creating html file

summary_dict = {forestunit: [[v] for v in age_increment] for forestunit in fu_list}
totals_dict = {forestunit: [] for forestunit in fu_list}
sql_dict = {forestunit: [] for forestunit in fu_list}

# for example, {'BW1': [[(1, 20)], [(21, 40)], [(41, 60)], [(61, 80)], [(81, 100)], [(101, 120)], [(121, 140)], [(141, 160)], 
# [(161, 180)], [(181, 200)], [(201, 999)]], 'SB1': [[(1, 20)],

ftf.logger("\nsummary_dictionary so far:\n%s"%summary_dict,'debug')

# loop through each Forest Unit
f = manFields + [AreaField] # mandatory fields plus area field.
prot_for_grandtotal = 0
prod_unavail_grandtotal = 0
prod_avail_grandtotal = 0

for fu, value in summary_dict.items():
    ftf.logger("\n\tWorking on %s..."%fu)
    prot_total = 0
    prod_unavail_total = 0
    prod_avail_total = 0

    prot_for_sql_full = '''"POLYTYPE" = 'FOR' AND "%s" = '%s' AND %s'''%(fu_field, fu, prot_for_sql)
    prod_for_unavil_sql_full = '''"POLYTYPE" = 'FOR' AND "%s" = '%s' AND %s AND %s'''%(fu_field, fu, prod_for_sql,unavailable_sql)
    prod_for_sod_sql_full = '''"POLYTYPE" = 'FOR' AND "%s" = '%s' AND "%s" is not Null AND "%s" not in ('', ' ') '''%(fu_field, fu, dev_field, dev_field)
    prod_for_avail_sql_full = '''"POLYTYPE" = 'FOR' AND "%s" = '%s' AND %s AND %s'''%(fu_field, fu, prod_for_sql,available_sql)

    # loop through each age group
    for i, agegroup in enumerate(value):
        age_from = agegroup[0][0] # eg. 21
        age_to = agegroup[0][1]  # eg. 40
        ftf.logger("\t\tCalculating area for Age Group %s to %s"%(age_from, age_to))

        # protection forest
        area = 0
        with arcpy.da.SearchCursor(inputbmi,f,prot_for_sql_full) as cursor:
            for row in cursor:
                if row[f.index('AGE')] >= age_from and row[f.index('AGE')] <= age_to:
                    area += row[f.index(AreaField)]
        summary_dict[fu][i].append(area/10000)
        prot_total += area/10000
        prot_for_grandtotal += area/10000

        # production forest - unavailable
        area = 0
        with arcpy.da.SearchCursor(inputbmi,f,prod_for_unavil_sql_full) as cursor:
            for row in cursor:
                if row[f.index('AGE')] >= age_from and row[f.index('AGE')] <= age_to:
                    area += row[f.index(AreaField)]
        summary_dict[fu][i].append(area/10000)
        prod_unavail_total += area/10000
        prod_unavail_grandtotal += area/10000

        # production forest - stage of development
        set_of_SoM = set()
        with arcpy.da.SearchCursor(inputbmi,f,prod_for_sod_sql_full) as cursor:
            for row in cursor:
                if row[f.index('AGE')] >= age_from and row[f.index('AGE')] <= age_to:
                    set_of_SoM.add(str(row[f.index(dev_field)]))
        if len(set_of_SoM) > 0:
            summary_dict[fu][i].append(list(set_of_SoM))
        else:
            summary_dict[fu][i].append(['N/A'])

        # production forest - available
        area = 0
        with arcpy.da.SearchCursor(inputbmi,f,prod_for_avail_sql_full) as cursor:
            for row in cursor:
                if row[f.index('AGE')] >= age_from and row[f.index('AGE')] <= age_to:
                    area += row[f.index(AreaField)]
        summary_dict[fu][i].append(area/10000)
        prod_avail_total += area/10000
        prod_avail_grandtotal += area/10000

    totals_dict[fu].extend([prot_total, prod_unavail_total,prod_avail_total])
    sql_dict[fu].extend([prot_for_sql_full, prod_for_unavil_sql_full, prod_for_sod_sql_full, prod_for_avail_sql_full])

# At this point all the numbers have been collected and stored in dictionary format. 
ftf.logger("\nsummary_dictionary:\n%s"%summary_dict,'debug')
ftf.logger("\ntotals:\n%s"%totals_dict, 'debug')


# generating one html table per forest unit
ftf.logger("\nCreating FMP3 tables...")
for fu, value in sorted(summary_dict.items()):
    ftf.logger('\t%s'%fu, 'debug')

    # populating table header tooltips
    replace_dict = {'*ProtForQ' :           sql_dict[fu][0], 
                    '*ProdForUnavailQ' :    sql_dict[fu][1], 
                    '*SoMQ' :               sql_dict[fu][2], 
                    '*ProdForAvailQ' :      sql_dict[fu][3]}
    eachTableHead = ftf.eachTableHead
    for k,v in replace_dict.items():
        eachTableHead = eachTableHead.replace(k,v)
    htmlstring += eachTableHead

    # populating the first row
    replace_dict = {'*NumOfAgeGroups':str(len(age_increment)),
                    '*ForUnit':       fu,
                    '*AgeGroup':      '%s - %s'%(str(value[0][0][0]),str(value[0][0][1])),
                    '*Prot':          str(round(value[0][1],1)),
                    '*Unavail':       str(round(value[0][2],1)),
                    '*SoM':           str(value[0][3]),
                    '*Avail':         str(round(value[0][4],1))}
    eachTable1stRow = ftf.eachTable1stRow
    for k,v in replace_dict.items():
        eachTable1stRow = eachTable1stRow.replace(k,v)    
    htmlstring += eachTable1stRow

    # populating all rows in between
    if len(age_increment) > 2:
        for i, agegroup in enumerate(age_increment[1:-1]):
            replace_dict = {'*AgeGroup':      '%s - %s'%(str(value[i+1][0][0]),str(value[i+1][0][1])),
                            '*Prot':          str(round(value[i+1][1],1)),
                            '*Unavail':       str(round(value[i+1][2],1)),
                            '*SoM':           str(value[i+1][3]),
                            '*Avail':         str(round(value[i+1][4],1))}
            eachTableMidRow = ftf.eachTableMidRow         
            for k,v in replace_dict.items():
                eachTableMidRow = eachTableMidRow.replace(k,v)    
            htmlstring += eachTableMidRow

    # populating the last row of the age groups
    replace_dict = {'*AgeGroup':      '%s - %s'%(str(value[-1][0][0]),str(value[-1][0][1])),
                    '*Prot':          str(round(value[-1][1],1)),
                    '*Unavail':       str(round(value[-1][2],1)),
                    '*SoM':           str(value[-1][3]),
                    '*Avail':         str(round(value[-1][4],1))}
    eachTableLastRow = ftf.eachTableLastRow
    for k,v in replace_dict.items():
        eachTableLastRow = eachTableLastRow.replace(k,v) 
    htmlstring += eachTableLastRow

    # populating the summary row
    replace_dict = {'*ForUnitSubtotal':     '%s Subtotal:'%fu,
                    '*ProtTotal':           str(round(totals_dict[fu][0],1)),
                    '*UnavailTotal':        str(round(totals_dict[fu][1],1)),
                    '*AvailTotal':          str(round(totals_dict[fu][2],1))}
    eachTableSummaryRow = ftf.eachTableSummaryRow
    for k,v in replace_dict.items():
        eachTableSummaryRow = eachTableSummaryRow.replace(k,v) 
    htmlstring += eachTableSummaryRow

    # adding a line between each table
    htmlstring += '<br>'

# creating extra information and footnote
ftf.logger("\nCreating the footnote...")
total_area = 0
total_polytype_for = 0
try:
    with arcpy.da.SearchCursor(inputbmi,f,'') as cursor:
        for row in cursor:
            total_area += row[f.index(AreaField)]
            if row[f.index('POLYTYPE')] == 'FOR':
                total_polytype_for += row[f.index(AreaField)]
except:
    pass

extraInfo = {
    '*TotalArea':       str(round(total_area/10000,1)),
    '*TotalPolytypeFor':str(round(total_polytype_for/10000,1)),
    '*TotalProtection': str(round(prot_for_grandtotal,1)),
    '*TotProdUnavail':  str(round(prod_unavail_grandtotal,1)),
    '*TotProdAvail':    str(round(prod_avail_grandtotal,1)),
    '*BMIused':         inputbmi,
    '*pythonscript':    str(inspect.getfile(inspect.currentframe())),
    '*reportlocation':  reportfile,
    '*dateandtime':     str(datetime.datetime.now())
    }
footnoteStr = ftf.footnoteStr
for k, v in extraInfo.items():
    footnoteStr = footnoteStr.replace(k,v)
htmlstring += footnoteStr






rep.write(htmlstring)

ftf.logger('\n\n****  Your report is saved here  ****')
ftf.logger(reportfile + '\n')

rep.close()
webbrowser.open(reportfile,new=2)
