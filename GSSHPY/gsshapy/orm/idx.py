'''
********************************************************************************
* Name: IndexMapModel
* Author: Nathan Swain
* Created On: Mar 18, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''

__all__ = ['IndexMap']

from sqlalchemy import Column
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relationship

from model.gsshapy import DeclarativeBase


class IndexMap(DeclarativeBase):
    """
    classdocs

    """
    __tablename__ = 'idx_index_maps'
    
    # Primary and Foreign Keys
    id = Column(Integer, autoincrement=True, primary_key=True)
    
    # Value Columns
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    rasterMap = Column(String) # Custom column to store rasters
    
    # Relationship Properties
    mapTables = relationship('MapTable', back_populates='indexMap')
    
    def __init__(self, name, filename, rasterMap):
        '''
        Constructor
        '''
        self.name = name
        self.filename = filename
        self.rasterMap = rasterMap
        
    def __repr__(self):
        return '<IndexMap: Name=%s, Path=%s>' % (self.name, self.filename)