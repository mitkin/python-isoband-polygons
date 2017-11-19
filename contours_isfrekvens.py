#!/usr/bin/env python

import rasterio as rst
import numpy as np
from rasterio.features import shapes
import geopandas as gp
import pandas as pd
import os
from shapely.geometry import Polygon, MultiPolygon
from rdp import rdp
from skimage.filters import gaussian
from matplotlib import pyplot as plt
from contours.core import shapely_formatter as shapely_fmt
from contours.quad import QuadContourGenerator


def get_xy_coords(dst):
    """
    Extract X and Y coordinates from rasterio dataset
    Parameters
    ----------
    |    dst : rasterio.DatasetReader
    
    Returns
    -------
        (x, y) : tuple with coordinate arrays
    """
    try:
        dx = dst.res[0]
        dy = dst.res[1]
    except:
        raise

    x = np.linspace(dst.bounds.left + dx/2., dst.bounds.right - dx/2., dst.width)
    y = np.linspace(dst.bounds.bottom + dy/2., dst.bounds.top - dy/2., dst.height)

    return x, y


def _extract_polygon(src_data, dx, dy, minval, maxval, transform=None, src=None):
    """
    """
    src_gauss = gaussian(np.where(src_data > minval, 1, 0),
                         sigma=0.75,
                         preserve_range=True)

    # src_gauss = np.ma.array(src_gauss, mask=(src_data==0))

    x, y = np.meshgrid(dx, dy)
    c = QuadContourGenerator.from_rectilinear(dx, dy, np.flipud(src_gauss), shapely_fmt)

    contour = c.filled_contour(min=0.354, max=100.0)

    results = ({'properties': {'value': minval}, 'geometry': s}
               for i, s in enumerate(contour))
    geoms=list(results)
    return geoms


def extract_polygons(src_data, levels, dx, dy, transform=None, maxval=101, src=None):
    """
    """

    gpd_prev = None
    gpd_diff = None

    for level in levels:

        output_path = 'cntrs-{:02d}.geojson'.format(int(level))
        if os.path.exists(output_path):
            os.remove(output_path)

        geoms = _extract_polygon(src_data,
                                 dx,
                                 dy,
                                 level,
                                 maxval,
                                 transform=transform,
                                 src=src)

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
    levels = [0.1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99.9][::-1]

    extract_polygons(src_data,
                     levels,
                     dx,dy,
                     transform=src.transform,
                     src=src)

if __name__ == "__main__":
    main()

