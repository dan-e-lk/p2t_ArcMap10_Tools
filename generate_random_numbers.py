# ------------------------------------------------------------------------------
# Name:        Generation of random numbers
# Purpose:     Generate random numbers for use in sampling ESRI feature class
#              and layers attributes.
#
# Author:      littleto
#
# Created:     28-06-2018
# Copyright:   (c) littleto 2018
# Licence:     <your licence>
# ------------------------------------------------------------------------------
r"""
This module is for my random number generation functions.

    *** This module requires the arcpy module. ***
"""
import random
import arcpy


def rand_select_rec(lyr, no_of_random_selections=10):
    r"""
    Randomly select records of a feature class using random.randint.

    This function requires the ESRI Arc feature class OBJECTID field.

    *** The actual number of selection may be fewer than specified since the
        same number may be draw multiple times. ***

    NTS:
    I should probably rewrite this function using random "choice"... in
    hindsight; well, "Live and learn". Maybe one day in the future...

    Parameters
    ----------
    lyr : Name of the feature class layer
    no_of_random_selections : Number of random integers generated. The
                              actual number of selection may be fewer than
                              specified since the same number may be draw
                              multiple times.

    Returns
    -------
    None

    See Also
    --------
    <other information> : <information/description>

    Examples
    --------
    >>>

    Dependencies (modules)
    ------------
    random
    arcpy

    """

    max_of_rng = int(str(arcpy.GetCount_management(lyr))) + 1

    sample_set = str(tuple(set(random.randint(1, max_of_rng) for i in range(no_of_random_selections))))
    arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", "OBJECTID In " + sample_set)


def rand_sample_rec(lyr, no_of_random_selections=10):
    r"""
    Randomly select records of a feature class using random.sample.

    This function requires the ESRI Arc feature class OBJECTID field.

    Parameters
    ----------
    lyr : name of the feature class layer
    no_of_random_selections : the number of random integers generated.

    Returns
    -------
    <return> : <information/description>

    See Also
    --------
    <other information> : <information/description>

    Examples
    --------
    >>>

    Dependencies (modules)
    ------------
    random
    arcpy

    """

    all_sample = [row.getValue("OBJECTID") for row in arcpy.SearchCursor(lyr, fields="OBJECTID")]

    sample_set = str(tuple(set(random.sample(all_sample, no_of_random_selections))))
    arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", "OBJECTID In " + sample_set)


if __name__ == '__main__':
    pass
