##################################            logger             ######################################

import logging
import arcpy


# debug info warning error critical
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # change level to logging.INFO to hide debug stuff
# logging.basicConfig(filename = 'thislog.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.CRITICAL) # disables all except critical

def logger(msg,level='info'):
	if level == 'debug':
		logging.debug(msg)
		arcpy.AddMessage(msg)		
	elif level == 'info':
		logging.info(msg)
		arcpy.AddMessage(msg)
	elif level == 'warning':
		logging.warning(msg)
		arcpy.AddWarning(msg)
	elif level == 'critical':
		logging.critical(msg)
		arcpy.AddError(msg)
		raise Exception(msg)
	else:
		logging.info(msg)
		arcpy.AddMessage(msg) 
	

def avail_editor(total,parts_dict):
  """
  total = total available harvest area for a forest unit in a age class
  parts_dict = available harvest areas for a forest unit in a age class for a particular stage of management.
  for example, total = 200.331, parts_dict = {'SEEDTREE': 50.0, 'LASTCUT': 150.331}
  """
  if len(parts_dict) < 2:
    return str(round(total,1))
  else:
    return_str = "<details><summary><strong>%s</strong></summary>\n"%round(total,1)
    for SoM, area in parts_dict.items():
      return_str += '<small>(%s) %s</small><br>'%(SoM, round(area,2))
    return_str += "\n</details>"
    return return_str



##################################         FMP3 HTML/CSS        ######################################

head_str = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
    font-family: "Helvetica", "Tahoma";
    margin: 0 50px 10px 70px;
}
h1 {
    margin: 0 -50px 0 -70px;
    padding: 30px 10px 10px 50px;
    font-size: 1.5em;
    background-color: #618c02;
    color: white;
}

table {
    width: 90%;
    min-width: 800px;
    max-width: 1600px;
}
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
}
td {
    padding: 1px;
    text-align: right;
}
th {
    padding: 5px;
    text-align: center;
}
td.leftb {
	border-left: 2px solid black;
}
td.bottomb {
	border-bottom: 2px solid black;
}
td.rightb {
	border-right: 2px solid black;
}
td.topb {
	border-top: 2px solid black;
}
td.txtleft {
  text-align: left;
}
td.txtcenter {
	text-align: center;
}
td.nobottomborder {
	border-bottom: solid transparent;
}
td.noleftborder {
	border-left: solid transparent;
}
td.norightborder {
	border-right: solid transparent;
}
td.rightalign {
	text-align: right;
}
td.shaded {
  background-color: #e3f7b9; /* light green */
}


table#t01 th {
  background-color: #77ad01; /* leafy green */
  color: white;
  border: 2px solid black;
}

<!--  Hover for tooltip  -->
.tooltip {
  position: relative;
  display: inline-block;
  border-bottom: 1px dotted black;
}

.tooltip .tooltiptext {
  visibility: hidden;
  width: auto;
  background-color: black;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 5px 2px;
  font-size: 70%;

  /* Position the tooltip */
  position: absolute;
  z-index: 1;


}

.tooltip:hover .tooltiptext {
    visibility: visible;
}

</style>
</head>
<body>

<h1>FMP 3 Table for <small>*FMPFileName</small></h1>
<small>
  *Forest Units are based on <strong>*ForestUnitField</strong>.    **Stage of Management is defined by <strong>*SoM</strong>.<br>
  Use Google Chrome or Firefox to use the full functionality of the report.
</small>
<br><br><br>
"""

eachTableHead = """
<table id="t01">
  <tr><!--  row 1  -->
    <th rowspan = "2">Forest Unit *</th>
    <th rowspan = "2">Age Class</th>
    <th rowspan = "2">	<div class="tooltip">Protection<br>Forest (ha)<span class="tooltiptext">*ProtForQ</span></div>	</th>
    <th colspan = "3">Production Forest</th>
  </tr>
  <tr><!--  row 2  -->
    <th>	<div class="tooltip">Unavailable (ha)<span class="tooltiptext">*ProdForUnavailQ</span></div>	</th>
    <th>	<div class="tooltip">Stage of Management **<span class="tooltiptext">*SoMQ</span></div>			</th>
    <th>	<div class="tooltip">Available (ha)<span class="tooltiptext">*ProdForAvailQ</span></div>		</th> 
  </tr>
  """

eachTable1stRow = """
  <tr>
    <td rowspan = "*NumOfAgeGroups" class="rightb leftb txtcenter"><strong>*ForUnit<strong></td>
    <td class = "nobottomborder txtcenter">*AgeGroup</td>
    <td class = "nobottomborder">*Prot</td>
    <td class = "nobottomborder">*Unavail</td>
    <td class = "nobottomborder txtcenter"><small>*SoM</small></td>    
    <td class = "nobottomborder rightb">*Avail</td>
  </tr>
"""

eachTableMidRow = """
  <tr>
    <td class = "nobottomborder txtcenter">*AgeGroup</td>
    <td class = "nobottomborder">*Prot</td>
    <td class = "nobottomborder">*Unavail</td>
    <td class = "nobottomborder txtcenter"><small>*SoM</small></td>    
    <td class = "nobottomborder rightb">*Avail</td>
  </tr>
"""
eachTableLastRow = """
  <tr>
    <td class = "txtcenter">*AgeGroup</td>
    <td>*Prot</td>
    <td>*Unavail</td>
    <td class = "txtcenter"><small>*SoM</small></td>    
    <td class = "rightb">*Avail</td>
  </tr>
"""

eachTableSummaryRow = """
  <tr>
    <td colspan = "2" class="topb bottomb leftb"><strong>*ForUnitSubtotal</strong></td>
    <td class="topb bottomb"><strong>*ProtTotal</strong></td>
    <td class="topb bottomb"><strong>*UnavailTotal</strong></td>
    <td class="topb bottomb txtcenter">--</td>    
    <td class="topb bottomb rightb"><strong>*AvailTotal</strong></td>
  </tr>
</table>
<br>
"""

footnoteStr = """
<hr>
<p>
  Total FMU Area:    *TotalArea ha<br>
  Total area where POLYTYPE = FOR:    *TotalPolytypeFor ha<br>
  Total Protection Forest:    *TotalProtection ha<br>
  Total Production Forest - Unavailable:    *TotProdUnavail ha<br>
  Total Production Forest - Available:    *TotProdAvail ha
</p>
<p><small>
	PCI/BMI used: *BMIused<br>
	Python Script used: *pythonscript<br>
  Script version: *version
	Report saved in: *reportlocation<br>
	Date and Time run: *dateandtime<br>
	<br>This tool was created by the NER Resources Information and Analysis Unit in 2018.

</p></small>
</body>
</html>
"""




if __name__ == '__main__':
  print(avail_editor(500, {}))
  print(avail_editor(1000.34241, {'a': 700.3342, 'b':300.1112}))