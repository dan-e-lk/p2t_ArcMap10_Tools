# Area-capped and area-weighted random block selection tool.
# Area-capped means instead of selecting a target number of records, the tool selects 
# 	a number of record until the sum of the selected area meets the target area.
# Area-weighted means the greater the area, the greater the chance that it will be picked.
# Usually the target area is 10% of the total area of all records
# 
# Workflow
# 1.	Input: shapefile or geodatabase that contains FTG-AR block spatial data
# 2.	Calculate the total area of all blocks and convert it to Ha.
# 3.	Calculate the Target Area (10% of the Total Area)
# 4.	Start randomly selecting (while giving area-weighted discrimination) FTG-AR blocks until the cumulative area of selected blocks reach the target area.
# 5.	Export/output the selected blocks.

import arcpy, os
from datetime import datetime

