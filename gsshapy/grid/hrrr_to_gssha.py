# -*- coding: utf-8 -*-
##
##  hrrr_to_gssha.py
##  GSSHApy
##
##  Created by Alan D Snow, 2016.
##  License BSD 3-Clause

import logging
import numpy as np
import pandas as pd
from os import mkdir, path, remove
import requests
import xarray as xr

from .grid_to_gssha import GRIDtoGSSHA

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
# HELPER FUNCTIONS
#------------------------------------------------------------------------------

def get_grib_subset(grb,lat0,lat1,lon0,lon1):
    """
    Extracts a subset from the grib file based on lat/lon bounds
    """
    lats,lons = grb.latlons()

    ##determine the bounds of the data with grid preservation
    lat_where = np.where((lats >= lat0) & (lats <= lat1))[0]
    lon_where = np.where((lons >= lon0) & (lons <= lon1))[1]

    max_lat_index = lat_where.max()
    min_lat_index = lat_where.min()
    max_lon_index = lon_where.max()
    min_lon_index = lon_where.min()

    ##extract the subset of data
    return (grb.values[min_lat_index:max_lat_index, min_lon_index:max_lon_index],
            lats[min_lat_index:max_lat_index, min_lon_index:max_lon_index],
            lons[min_lat_index:max_lat_index, min_lon_index:max_lon_index])

def download_hrrr_for_gssha(main_directory,
                            forecast_start_date_string, #EX. '20160913'
                            forecast_start_hour_string, #EX. '00' to '23'
                            leftlon=-180, rightlon=180,
                            toplat=90,bottomlat=-90):
    """
    Function to download HRRR data for GSSHA

    URL:
        http://nomads.ncep.noaa.gov/cgi-bin/filter_hrrr_2d.pl

    Args:
        main_directory(str): Location of the output for the forecast data.
        forecast_start_date_string(str): String for day of forecast. Ex. '20160913'
        forecast_start_hour_string(str): String for hour of forecast start. Ex. '02'
        leftlon(Optional[double,int]): Left bound for longitude. Default is -180.
        rightlon(Optional[double,int]): Right bound for longitude. Default is 180.
        toplat(Optional[double,int]): Top bound for latitude. Default is 90.
        bottomlat(Optional[double,int]): Bottom bound for latitude. Default is -90.

    Returns:
        downloaded_file_list(list): List of paths to downloaded files.

    Example::

        from gsshapy.grid.hrrr_to_gssha import download_hrrr_for_gssha

        hrrr_folder = '/HRRR'
        leftlon = -95
        rightlon = -75
        toplat = 35
        bottomlat = 30
        downloaded_file_list = download_hrrr_for_gssha(hrrr_folder,'20160914','01',
                                                       leftlon,rightlon,toplat,bottomlat)

    """
    out_directory = path.join(main_directory, forecast_start_date_string)

    try:
        mkdir(out_directory)
    except OSError:
        pass

    forecast_timestep_hour_string_array = ['00', '01', '02', '03', '04',
                                           '05', '06', '07', '08', '09',
                                           '10', '11', '12', '13', '14',
                                           '15', '16', '17', '18']
    downloaded_file_list = []
    for forecast_timestep_hour_string in forecast_timestep_hour_string_array:
        file_name = 'hrrr.t{0}z.wrfsfcf{1}.grib2'.format(forecast_start_hour_string, forecast_timestep_hour_string)
        payload = {
                   'file': file_name,
                   'lev_10_m_above_ground': 'on',
                   'lev_2_m_above_ground': 'on',
                   'lev_entire_atmosphere': 'on',
                   'lev_surface': 'on',
                   'var_DSWRF': 'on',
                   'var_PRATE': 'on',
                   'var_PRES': 'on',
                   'var_RH': 'on',
                   'var_TMP': 'on',
                   'var_UGRD': 'on',
                   'var_VGRD': 'on',
                   'var_TCDC': 'on',
                   'subregion': '',
                   'leftlon': str(leftlon),
                   'rightlon': str(rightlon),
                   'toplat': str(toplat),
                   'bottomlat': str(bottomlat),
                   'dir': '/hrrr.{0}'.format(forecast_start_date_string),
                   }

        r = requests.get('http://nomads.ncep.noaa.gov/cgi-bin/filter_hrrr_2d.pl', params=payload, stream=True)

        if r.status_code == requests.codes.ok:
            out_file = path.join(out_directory, file_name)
            downloaded_file_list.append(out_file)
            with open(out_file, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024):
                    fd.write(chunk)
        else:
            log.error("Problem downloading {0}".format(file_name))
            for filename in downloaded_file_list:
                try:
                    remove(filename)
                except OSError:
                    pass
            downloaded_file_list = []
            break

    return downloaded_file_list

#------------------------------------------------------------------------------
# MAIN CLASS
#------------------------------------------------------------------------------
class HRRRtoGSSHA(GRIDtoGSSHA):
    """This class converts the HRRR output data to GSSHA formatted input.
    This class inheris from class:`GRIDtoGSSHA`.

    Attributes:
        gssha_project_folder(str): Path to the GSSHA project folder
        gssha_project_file_name(str): Name of the GSSHA elevation grid file.
        lsm_input_folder_path(str): Path to the input folder for the LSM files.
        lsm_search_card(str): Glob search pattern for LSM files. Ex. "*.grib2".
        lsm_lat_var(Optional[str]): Name of the latitude variable in the LSM netCDF files. Defaults to 'lat'.
        lsm_lon_var(Optional[str]): Name of the longitude variable in the LSM netCDF files. Defaults to 'lon'.
        lsm_time_var(Optional[str]): Name of the time variable in the LSM netCDF files. Defaults to 'time'.
        lsm_lat_dim(Optional[str]): Name of the latitude dimension in the LSM netCDF files. Defaults to 'lat'.
        lsm_lon_dim(Optional[str]): Name of the longitude dimension in the LSM netCDF files. Defaults to 'lon'.
        lsm_time_dim(Optional[str]): Name of the time dimension in the LSM netCDF files. Defaults to 'time'.
        output_timezone(Optional[tzinfo]): This is the timezone to output the dates for the data. Default is UTC.
                                           This option does NOT currently work for NetCDF output.

    Example::

        from gsshapy.grid import HRRRtoGSSHA

        l2g = HRRRtoGSSHA(gssha_project_folder='E:\\GSSHA',
                          gssha_project_file_name='gssha.prj',
                          lsm_input_folder_path='E:\\GSSHA\\hrrr-data',
                          lsm_search_card="*.grib2",
                          )

        # example data var map
        data_var_map_array = [
                               ['precipitation_rate', 'PRATE_P0_L1_GLC0'],
                               ['pressure', 'PRES_P0_L1_GLC0'],
                               ['relative_humidity', 'RH_P0_L103_GLC0'],
                               ['wind_speed', ['UGRD_P0_L103_GLC0', 'VGRD_P0_L103_GLC0']],
                               ['direct_radiation_cc', ['DSWRF_P0_L1_GLC0', 'TCDC_P0_L10_GLC0']],
                               ['diffusive_radiation_cc', ['DSWRF_P0_L1_GLC0', 'TCDC_P0_L10_GLC0']],
                               ['temperature', 'TMP_P0_L1_GLC0'],
                               ['cloud_cover_pc', 'TCDC_P0_L10_GLC0'],
                              ]

    """
    def __init__(self,
                 gssha_project_folder,
                 gssha_project_file_name,
                 lsm_input_folder_path,
                 lsm_search_card,
                 lsm_lat_var='gridlat_0',
                 lsm_lon_var='gridlon_0',
                 lsm_time_var='time',
                 lsm_lat_dim='ygrid_0',
                 lsm_lon_dim='xgrid_0',
                 lsm_time_dim='time',
                 output_timezone=None,
                 ):
        """
        Initializer function for the HRRRtoGSSHA class
        """
        super(HRRRtoGSSHA, self).__init__(gssha_project_folder,
                                          gssha_project_file_name,
                                          lsm_input_folder_path,
                                          lsm_search_card,
                                          lsm_lat_var,
                                          lsm_lon_var,
                                          lsm_time_var,
                                          lsm_lat_dim,
                                          lsm_lon_dim,
                                          lsm_time_dim,
                                          output_timezone)

    @property
    def xd(self):
        """get xarray dataset file handle to LSM files"""
        if self._xd is None:
            path_to_lsm_files = path.join(self.lsm_input_folder_path,
                                          self.lsm_search_card)
            def extract_date(ds):
                for var in ds.variables:
                    if 'initial_time' in ds[var].attrs.keys():
                        grid_time = pd.to_datetime(ds[var].attrs['initial_time'],
                                                   format="%m/%d/%Y (%H:%M)")
                        if 'forecast_time' in ds[var].attrs.keys():
                            time_units = 'h'
                            if 'forecast_time_units' in ds[var].attrs.keys():
                                time_units =  str(ds[var].attrs['forecast_time_units'][0])
                            grid_time += np.timedelta64(int(ds[var].attrs['forecast_time'][0]),
                                                        time_units)

                        return ds.assign(time=grid_time)
                raise ValueError("Time attribute missing: {0}".format(self.search_time_attr))

            self._xd = xr.open_mfdataset(path_to_lsm_files,
                                         concat_dim='time',
                                         preprocess=extract_date,
                                         engine='pynio')
            self._xd.lsm.y_var = self.lsm_lat_var
            self._xd.lsm.x_var = self.lsm_lon_var
            self._xd.lsm.time_var = self.lsm_time_var
            self._xd.lsm.y_dim = self.lsm_lat_dim
            self._xd.lsm.x_dim = self.lsm_lon_dim
            self._xd.lsm.time_dim = self.lsm_time_dim
            self._xd.lsm.to_datetime()
        return self._xd
