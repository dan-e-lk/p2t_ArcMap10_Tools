import Script.main

# Remember to run this script from your ArcGIS's python (which is version 2 and has arcpy)

# verify the path of your input json file
# json_file = r'C:\DanielKimWork\_FRI_All\Processed\NWR_allExcept_WF_KEN\NWR2.json'
# json_file = r'C:\DanielKimWork\_FRI_All\Processed\GLSL\GLSL.json'
json_file = r'C:\DanielK_Workspace\_Compiler_outputs\All_NER\compiler_run_202108172231.json'


Script.main.main(json_file)