"""
********************************************************************************
* Name: Read a file in and write it back out
* Author: Nathan Swain
* Created On: July 8, 2014
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
"""

import os

import time
from gsshapy.orm import WMSDatasetFile, ProjectFile, ChannelInputFile, LinkNodeDatasetFile
from gsshapy.lib import db_tools as dbt
from sqlalchemy import MetaData, create_engine
from mapkit.RasterConverter import RasterConverter

# Database Setup ------------------------------------------------------------------------------------------------------#

# # Drop all tables except the spatial reference table that PostGIS uses
# db_url = 'postgresql://swainn:(|water@localhost/gsshapy_postgis_2'
# engine = create_engine(db_url)
# meta = MetaData()
# meta.reflect(bind=engine)
#
# for table in reversed(meta.sorted_tables):
#     if table.name != 'spatial_ref_sys':
#         table.drop(engine)

# Create new tables
sqlalchemy_url = dbt.init_postgresql_db(username='swainn',
                                        password='(|w@ter',
                                        host='localhost',
                                        database='gsshapy_postgis_2')

# Global Parameters ---------------------------------------------------------------------------------------------------#
#'''
read_directory = '/Users/swainn/testing/timeseries_maps/Park_City_Chan_Depth'
write_directory = '/Users/swainn/testing/timeseries_maps/Park_City_Chan_Depth/write'
'''
read_directory = '/Users/swainn/testing/timeseries_maps/Park_City_5_Min_Frequency'
write_directory = '/Users/swainn/testing/timeseries_maps/Park_City_5_Min_Frequency/write'
#'''
new_name = 'out'
spatial = True
srid = 26912
raster2pgsql_path = '/Applications/Postgres93.app/Contents/MacOS/bin/raster2pgsql'
read_session = dbt.create_session(sqlalchemy_url)
write_session = dbt.create_session(sqlalchemy_url)
   

# Read Project --------------------------------------------------------------------------------------------------------#

# project_file = ProjectFile()
#
# START = time.time()
# project_file.readProject(read_directory, 'parkcity.prj', read_session, spatial=spatial, spatialReferenceID=srid, raster2pgsqlPath=raster2pgsql_path)
# print 'READ: ', time.time() - START

# project_file = write_session.query(ProjectFile).first()
# START = time.time()
# project_file.writeProject(write_session, write_directory, 'parkcity')
# print 'WRITE: ', time.time() - START

# Test Time Series KML ------------------------------------------------------------------------------------------------#
project_file = write_session.query(ProjectFile).first()
wms_dataset = write_session.query(WMSDatasetFile).first()

START = time.time()
'''
out_path = os.path.join(write_directory, 'out.kml')
kml_animation_string = wms_dataset.getAsKmlGridAnimation(write_session, project_file, path=out_path, colorRamp=RasterConverter.COLOR_RAMP_AQUA)
'''

'''
out_path = os.path.join(write_directory, 'out.kmz')
kml_animation_string = wms_dataset.getAsKmlPngAnimation(write_session, project_file, path=out_path, colorRamp=RasterConverter.COLOR_RAMP_AQUA, alpha=0.8, cellSize=30)
#'''

'''
channel_input_file = write_session.query(ChannelInputFile).first()
stream_links = channel_input_file.streamLinks

out_path = os.path.join(write_directory, 'channel.kml')
styles = {'lineColor': (0, 255, 128, 255)}

channel_input_file.getStreamNetworkAsKml(write_session, out_path)
'''

'''
out_path = os.path.join(write_directory, 'model.kml')
project_file.getKmlRepresentationOfModel(write_session, out_path, withStreamNetwork=True)
'''

channel_input_file = write_session.query(ChannelInputFile).first()
link_node_dataset_file = write_session.query(LinkNodeDatasetFile).first()

# link_node_dataset_file.linkToChannelInputFile(write_session, channel_input_file)
out_path = os.path.join(write_directory, 'channel_depth.kml')
link_node_dataset_file.getAsKmlAnimation(write_session, channel_input_file, path=out_path, zScale=100)

print 'KML OUT: ', time.time() - START