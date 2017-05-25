"""
********************************************************************************
* Name: Mask Tests
* Author: Alan D. Snow
* Created On: February 6, 2016
* License: BSD 3-Clause
********************************************************************************
"""
from glob import glob
from os import path
import unittest
from shutil import copy

from .template import TestGridTemplate

from gsshapy.orm import ProjectFile, WatershedMaskFile
from gsshapy.lib import db_tools as dbt

from os import path, chdir


class TestMask(TestGridTemplate):
    def setUp(self):
        self.gssha_project_directory = self.writeDirectory

        self.shapefile_path = path.join(self.writeDirectory,
                                        'phillipines_5070115700.shp')

        self.compare_path = path.join(self.readDirectory,
                                      'phillipines',
                                      'compare_data')
        # copy shapefile
        shapefile_basename = path.join(self.readDirectory,
                                       'phillipines',
                                       'phillipines_5070115700.*')

        for shapefile_part in glob(shapefile_basename):
            try:
                copy(shapefile_part,
                     path.join(self.writeDirectory, path.basename(shapefile_part)))
            except OSError:
                pass

        # Create Test DB
        sqlalchemy_url, sql_engine = dbt.init_sqlite_memory()

        # Create DB Sessions
        self.db_session = dbt.create_session(sqlalchemy_url, sql_engine)

        # Instantiate GSSHAPY object for reading to database
        self.project_manager = ProjectFile(name="grid_standard_msk", map_type=1)
        self.db_session.add(self.project_manager)
        self.db_session.commit()

        self.msk_file = WatershedMaskFile(project_file=self.project_manager,
                                          session=self.db_session)
        chdir(self.gssha_project_directory)

    def _compare_output(self, project_name):
        """
        compare mask files
        """
        # compare mask files
        mask_file_name = '{0}.msk'.format(project_name)
        new_mask_grid = path.join(self.writeDirectory, mask_file_name)
        compare_msk_file = path.join(self.compare_path, mask_file_name)
        self._compare_files(compare_msk_file, new_mask_grid, raster=True)
        # compare project files
        prj_file_name = '{0}.prj'.format(project_name)
        generated_prj_file = path.join(self.gssha_project_directory, prj_file_name)
        compare_prj_file = path.join(self.compare_path, prj_file_name)
        self._compare_files(generated_prj_file, compare_prj_file)
        # check to see if projection file generated
        proj_file_name = '{0}_prj.pro'.format(project_name)
        generated_proj_file = path.join(self.gssha_project_directory, proj_file_name)
        compare_proj_file = path.join(self.compare_path, proj_file_name)
        self._compare_files(generated_proj_file, compare_proj_file)

    def _before_teardown(self):
        """
        Method to execute at beginning of tearDown
        """
        self.db_session.close()

    def test_rasterize_cell_size_ascii_utm(self):
        """
        Tests rasterize_shapefile using cell size to ascii in utm
        """
        project_name = 'grid_standard_msk'
        mask_name = '{0}.msk'.format(project_name)
        self.msk_file.generateFromWatershedShapefile(self.shapefile_path,
                                                     cell_size=1000,
                                                     out_raster_path=mask_name,
                                                     )
        self.project_manager.writeInput(session=self.db_session,
                                        directory=self.gssha_project_directory,
                                        name=project_name)
        # compare results
        self._compare_output(project_name)

    def test_rasterize_cell_size_ascii_utm_outlet(self):
        """
        Tests rasterize_shapefile using cell size to ascii in utm
        Then add outlet information
        """
        project_name = 'grid_standard_msk_outlet'
        mask_name = '{0}.msk'.format(project_name)
        self.msk_file.generateFromWatershedShapefile(self.shapefile_path,
                                                     cell_size=1000,
                                                     out_raster_path=mask_name,
                                                     )
        self.project_manager.setOutlet(col=0, row=9)
        self.project_manager.writeInput(session=self.db_session,
                                        directory=self.gssha_project_directory,
                                        name=project_name)
        # compare results
        self._compare_output(project_name)

if __name__ == '__main__':
    unittest.main()
