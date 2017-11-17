#!/usr/bin/env python

import rasterio as rst
import numpy as np
from rasterio.features import shapes
import geopandas as gp
import pandas as pd
import os
from shapely.geometry import Polygon
from rdp import rdp
from skimage.filters import gaussian
from matplotlib import pyplot as plt 


def get_xy_coords(dst):
    """
    Extract X and Y coordinates from rasterio dataset
    Parameters
    ----------
    |    dst : rasterio.DatasetReader
    
    Returns
    -------
        (dx, dy) : tuple with coordinate arrays
    """
    try:
        dx = (dst.bounds.right - dst.bounds.left) / dst.width
        dy = (dst.bounds.top - dst.bounds.bottom) / dst.height
    except:
        raise

    return dx, dy


def _extract_polygon(src_data, dx, dy, minval, maxval, transform=None):
    """
    """
    src_gauss = gaussian(np.where(src_data>minval, 1, 0), 1.2)
    mask = np.where(src_gauss >= 0.5, 1, 0)
    # TODO add matplotlib contouring here

    results = ({'properties': {'value': minval}, 'geometry': s}
               for i, (s, v) in enumerate(shapes(src_gauss.astype(rst.float32),
                                          mask=mask,
                                          transform=transform)))
    geoms=list(results)
    return geoms


def extract_polygons(src_data, levels, dx, dy, transform=None, maxval=101):
    """
    """

    gpd_prev = None
    gpd_diff = None

    for level in levels:

        output_path = 'cntrs-{:02d}.geojson'.format(level)
        if os.path.exists(output_path):
            os.remove(output_path)

        geoms = _extract_polygon(src_data,
                                 dx,
                                 dy,
                                 level,
                                 maxval,
                                 transform=transform)

        gpd_orig = gp.GeoDataFrame.from_features(geoms)
        gpd_current = gpd_orig

        gpd_current.crs = {'init': 'epsg:3413'}

        if gpd_prev is None:
            gpd_prev = gpd_current
        else:
            gpd_diff = gp.overlay(gpd_current,
                                  gpd_prev,
                                  how='difference')
            gp_new = pd.concat([gpd_prev, gpd_diff], ignore_index=True)
            gpd_prev = gp_new.copy()

    try:
       gp_new.to_file(output_path, driver='GeoJSON')
    except:
       gpd_current.to_file(output_path, driver='GeoJSON')


def main():
    # src = rst.open('./issmall.tif')
    src = rst.open('/home/mikhail/Projects/IsfrekvensPolygons/isfrekvens-masked_epsg3413.tif')
    dx, dy = get_xy_coords(src)
    src_data = src.read(1)
    levels = [1, 10, 40, 70, 90, 99][::-1]

    extract_polygons(src_data, levels, dx, dy, transform=src.transform)

if __name__ == "__main__":
    main()

