# uses arcpy's clip_management tool to clip a large imagery into pieces.
# the size of the small pieces depends on the grid feature class you specify. You can build your own grid using grid index features tool on arcmap.
# also, specify the unique id field.


import arcpy, os, re

def get_time():
    from datetime import datetime
    time_now = datetime.now()
    timestamp = time_now.strftime('%Y-%m-%d %H:%M:%S')
    time_suffix = time_now.strftime('%Y%m%d_%H%M%S')

def main(input_raster, grid_fc, unique_id_field, output_file_folder, output_file_name, compression, output_file_type = 'jp2'):
    """
    At this moment, jp2 is the only output file type.
    input_raster and grid_fc should have the same projection for ideal output.
    unique_id_field should be one of the fieldnames of the grid_fc and should be unique and consist of numbers.
    compression should be anywhere between 1 - 100. 1 being most compressed.
    output_file_name should be less than 21 characters and should not contain file extension
    """

    # check inputs
    try:
        int(compression)
    except:
        arcpy.AddError("Compression should be a number between 1 and 100.")
    if int(compression) < 1 or int(compression) > 100: arcpy.AddError("Compression should be a number between 1 and 100.")

    # output_file_name should not contain special characters and should be <= 20 char
    if re.match("^[\w\d_]*$",output_file_name):
        if len(output_file_name) <= 20:
            pass
        else:
            arcpy.AddError("Your output_file_name is too long!!")
    else:
        raise arcpy.AddError("Your output_file_name contains spaces, special characters or file extensions!!")

    # get unique ids and the minimum and maximum extent of each grid
    grid = {}
    total_count = 0
    ids = []

    for row in arcpy.da.SearchCursor(grid_fc, [unique_id_field,'SHAPE@']):
        extent = row[1].extent
        print('XMin: {}, YMin: {}'.format(extent.XMin, extent.YMin))
        print('XMax: {}, YMax: {}'.format(extent.XMax, extent.YMax))

        grid[str(row[0])] = ["%s %s %s %s"%(extent.XMin, extent.YMin, extent.XMax, extent.YMax)]
        total_count += 1
        ids.append(row[0])

    # set the environment(compression)
    arcpy.env.compression = "JPEG2000 %s"%compression

    # create file names
    zfill_num = len(str(max(ids)))  # if max number is 3021, all other numbers will be zero filled to make it 4 digits. eg. 0021.
    for uniqueid in grid.keys():
        new_filename = '%s_comp%s_%s.%s'%(output_file_name, compression, uniqueid.zfill(zfill_num), output_file_type)
        grid[uniqueid].append(new_filename)

    arcpy.AddMessage(str(grid))
    # At this point, grid dictionary looks like this:
    # {'135': ['451533.858946 5344007.32554 456533.858946 5349007.32554', 'omnr_romeo_comp25_135.jp2'], '134': ['446533.858946 5344007.32554 451533.858946 5349007.32554', 'omnr_romeo_comp25_134.jp2']}

    # create a temporary layer of the grid file so we can select and run
    arcpy.MakeFeatureLayer_management(grid_fc,"templyr")

    # run raster clip
    q = 0
    for k, v in grid.items():
        q += 1
        arcpy.AddMessage("Running Clip on %s = %s  (%s of %s)"%(unique_id_field, k, q, total_count))

        # select individual grid using the unique id provided
        sql = """ "%s" = %s  """%(unique_id_field, k) # for example, "PageNumber" = 134
        arcpy.SelectLayerByAttribute_management("templyr", "NEW_SELECTION", sql)

        out_raster = os.path.join(output_file_folder, v[1])  
        if os.path.isfile(out_raster):
            arcpy.AddMessage("%s already exists."%v[1])
        else:
            arcpy.Clip_management(in_raster=input_raster, rectangle=v[0], out_raster=out_raster, in_template_dataset=grid_fc, nodata_value="256", clipping_geometry="NONE", maintain_clipping_extent="NO_MAINTAIN_EXTENT")


    arcpy.SelectLayerByAttribute_management("templyr", "CLEAR_SELECTION")


if __name__ == '__main__':
    # input_raster = r'Y:\LiDAR_Testing\RomeoOrtho\compressed_bpa\omnr_romeo_malette.tif'
    # grid_fc = r'Y:\LiDAR_Testing\RomeoOrtho\Processed\GridIndex_romeo.gdb\romeo_buff5k_1k_edge_only' # it will clip to the rectangle of the shape boundary even if your grid is not rectangle.  Make sure the projection of the this fc is the same as the input raster.
    # unique_id_field = 'PageNumer2' # should be a number field
    # output_file_folder = r'Y:\LiDAR_Testing\RomeoOrtho\Processed\Clip\comp15_1km'
    # output_file_name = 'romeo_edges_2018_1km'
    # compression = '15'

    input_raster = arcpy.GetParameterAsText(0)
    grid_fc = arcpy.GetParameterAsText(1) # it will clip to the rectangle of the shape boundary even if your grid is not rectangle.  Make sure the projection of the this fc is the same as the input raster.
    unique_id_field = arcpy.GetParameterAsText(2) # should be a number field
    output_file_folder = arcpy.GetParameterAsText(3)
    output_file_name = arcpy.GetParameterAsText(4)
    compression = str(arcpy.GetParameterAsText(5))

    # for i in (input_raster, grid_fc, unique_id_field, output_file_folder, output_file_name, compression):
    #     arcpy.AddMessage(i)

    main(input_raster, grid_fc, unique_id_field, output_file_folder, output_file_name, compression)