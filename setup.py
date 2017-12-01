from setuptools import setup

setup(
    name='python-isoband-polygons',
    version='0.1',
    packages=[''],
    url='',
    license='',
    author='Mikhail Itkin',
    author_email='itkin.m@gmail.com',
    description='Python package for creating contoured polygons',
    install_requires=['rasterio',
                      'geopandas',
                      'contours',
                      'scikit-image'],
    test_requires=['nose']
)
