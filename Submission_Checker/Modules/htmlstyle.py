# The only purpose of this script is to provide CSS string to the checker tool report.
# Any further updates can be found here: \\cihs.ad.gov.on.ca\mnrf\Groups\ROD\RODOpen\Forestry\Tools_and_Scripts\FI_Checker\ChangeLog

import webbrowser

htmlStyle = '''
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css?family=Raleway:400,800" rel="stylesheet">
<style>
body {
    font-family: "Helvetica", "Tahoma";
    padding: 0 50px 0 50px;
}

#table {width:50%;}
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    max-width: 1400px;
}
th, td {
    padding: 3px;
    text-align: left;
}
#w {
    min-width: 500px;
}
table#t02 tr:nth-child(even) {
    background-color: #F2F5F0;
}
table#t02 tr:nth-child(odd) {
   background-color: #FCFCFB;
}
table#t02 th {
    background-color: #658254;
    color: white;
    font-size: 85%;
}
table#t01 th {
    border: 1px solid white;
    border-collapse: collapse;
}
table#t01 td {
    border: 1px solid white;
    border-collapse: collapse;
}

h1, h2, .collapsible {
    font-family: 'Raleway', sans-serif;
}

h1 {
    font-size: 1.5em;
    margin: 0;
    font-weight: bold;
    background: #000000;
    color: white;
    padding: 30px 0 10px 20px;
}

h2 {
    display: block;
    font-size: 1.3em;
    margin-top: 0;
    font-weight: bold;
    background: linear-gradient(to right, #DBE2D6, white);
    border-bottom: 1px solid #DBE2D6;
    padding: 5px 0 2px 5px;
}

.h2content {
    padding: 0 15px;
}

h3 {
    display: block;
    font-size: 1em;
    margin-top: 1em;
    margin-bottom: 1em;
    font-weight: bold;
    background: linear-gradient(to right, #EAEEE7, white);
    border-bottom: 1px solid #EAEEE7;
    padding: 5px 0 2px 5px;
}

h4 {
    display: block;
    margin-top: 1.33em;
    margin-bottom: 1.33em;
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

img {
    float: right;
    height: 50px;
    padding: 10px 10px 5px 0;
}
.infobox{
    float: right;
}
.infotexthead{
    font-weight: bold;
    background-color: #EEF2EC;
    padding: 10px 20px 10px 10px;
}
.infotext{
    padding: 5px 5px 5px 10px;
    line-height: 1.6;
    font-size: 0.9em;    
}

/* Hover for tooltip */

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

/* Collapsible content */

.collapsible {
    background: linear-gradient(to right, #DBE2D6, white);
    cursor: pointer;
    padding: 5px 0 2px 5px;
    width: 100%;
    border: none;
    text-align: left;
    font-weight: bold;
    font-size: 20px;
    margin-bottom: 5px;
}

.active, .collapsible:hover {
    background: #86af6d;
    color: white;
}

.content {
    padding: 0 15px;
    display: none;
    overflow: hidden;
    background-color: white;
}

#col-small {
    font-family: "Helvetica", "Tahoma";
    font-size: 0.8em;
    border-bottom: 1px solid #EAEEE7;
    padding: 5px 0 2px 5px;  
}

</style>
</head>
'''



jvscript = '''

<script>
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
    });
}
</script>

'''



if __name__ == '__main__':
    htmlfile = r'C:\TEMP\testhtml.html'
    rep = open(htmlfile,'w')
    rep.write(htmlStyle)

##    rep.write('''
##    <body>
##
##    <h1>This is h1</h1>
##    <h2>This is h2</h2>
##    <h3>This is h3</h3>
##    <h4>This is h4</h4>
##    <p id="p01">This is p01</p>
##    <p id="p02">This is p02</p>
##    <p id="p03">This is p03</p>
##    ''')


    rep.write('''
    <h1>AWS GSO Report on N:\WORK-DATA\FMPDS\Abitibi_River\AWS\2017\_data\FMP_Schema.gdb</h1>
    <h2>Report Summary</h2>
    <table id="t01">
      <tr><td>AWS Year:</td><td>2017</td></tr>
      <tr>
        <td>MU Number:</td>
        <td>110</td>
      </tr>
      <tr>
        <td>MU Name:</td>
        <td>Abitibi River Forest</td>
      </tr>
      <tr>
        <td>Date Reviewed:</td>
        <td>2017-02-28</td>
      </tr>
      <tr>
        <td>Submission ID:</td>
        <td>1234567</td>
      </tr>
    </table>

    <br>

    <table id="t02">
      <tr>
        <th>Layer File Name</th>
        <th>Layer Name</th>
        <th>Projection</th>
        <th>Existing Mandatory Fields</th>
        <th>Additional Fields</th>
        <th>Field Validation</th>
        <th>Field Definition Comments</th>
        <th>Record Validation</th>
        <th>Record Validation Comments</th>
        <th>FIM Reference</th>
      </tr>
      <tr>
        <td>MU110_17AGP00</td>
        <td>Existing Forestry Aggregate Pits</td>
        <td>UTM Z17</td>
        <td><small>['PIT_OPEN', 'PITCLOSE', 'CAT9APP']</small></td>
        <td><small>['PIT-ID','YearX']</small></td>
        <td><p id="p03">Invalid</p></td>
        <td>'PIT_ID' is missing</td>
        <td><p id="p01">Valid</p></td>
        <td>N/A</td>
        <td><a href="https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=42" target="_blank">4.2.20</a></td>
      </tr>
      <tr>
        <td>MU110_17SRA01</td>
        <td>Scheduled Existing Road Activities</td>
        <td>UTM Z17</td>
        <td><small>['AWS_YR', 'ROADID', 'ROADCLAS']</small></td>
        <td><small></small></td>
        <td><p id="p01">Valid</p></td>
        <td>N/A</td>
        <td><p id="p03">Invalid</p></td>
        <td>- 2 record(s) where AWS_YR = 2017 but not one of DECOM, MAINTAIN, MONITOR, and ACCESS is Y.</br>- 1 record(s) where AWS_YR = 2016</td>
        <td><a href="https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=18" target="_blank">4.2.8</a></td>
      </tr>
      <tr>
        <td>More layers....</td>
        <td>Other layer</td>
        <td>UTM Z17</td>
        <td><small>['AWS_YR', 'ROADID', 'ROADCLAS']</small></td>
        <td><small></small></td>
        <td><p id="p01">Valid</p></td>
        <td>N/A</td>
        <td><p id="p03">Invalid</p></td>
        <td>- 1 record(s) where AWS_YR = 2016</td>
        <td></td>
      </tr>
    </table>


    Missing layers: ['SRP', 'SPT']<br>
    <small>
    Note that some of the additional fields such as 'OBJECTID' have been added during data processing.<br>
    Other footnotes....<br>
    </small>

    <br>

    <h2>Checking Coverage</h2>
    The table below summarizes the watchfile located here: url...
    <table id="t02">
      <tr>
        <th>Coverage File Name</th>
        <th>Node Errors</th>
        <th>Label Errors</th>
        <th>Precision</th>
        <th>Projection</th>
      </tr>
      <tr>
        <td>coveragefilename</td>
        <td><p id="p03">Found 3 dangling nodes</p></td>
        <td><p id="p03">Found 113 polygons without a label</p></td>
        <td><p id="p01">Double</p></td>
        <td>UTM Z17</td>
      </tr>
    </table>

    <br>

    <h2>Error Detail</h2>

    <table id="t01">
    <tr><td>OBJECTID 6: ERROR (DECOM <> Y AND MAINTAIN <> Y AND MONITOR <> Y AND ACCESS <> Y) where AWS_YR equals the fiscal year</tr></td>
    <tr><td>OBJECTID 7: ERROR (DECOM <> Y AND MAINTAIN <> Y AND MONITOR <> Y AND ACCESS <> Y) where AWS_YR equals the fiscal year</tr></td>
    <tr><td>More error messeges like this.....</tr></td>
    </table>

    </body>
    </html>''')

    rep.close()
    webbrowser.open(htmlfile,new=2)