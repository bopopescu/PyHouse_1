"""
-*- test-case-name: PyHouse.src.Modules.Web.test.test_web_house -*-

@name:      PyHouse/src/Modules/Web/web_house.py
@author:    D. Brian Kimmel
@contact:   D.BrianKimmel@gmail.com
@copyright: (c) 2013-2015 by D. Brian Kimmel
@license:   MIT License
@note:      Created on Jun 3, 2013
@summary:   Web interface to house info for the selected house.

"""

# Import system type stuff
import os
from nevow import athena
from nevow import loaders

# Import PyMh files and modules.
from Modules.Web.web_utils import JsonUnicode, GetJSONHouseInfo
from Modules.Computer import logging_pyh as Logger

LOG = Logger.getLogger('PyHouse.webHouse    ')

# Handy helper for finding external resources nearby.
webpath = os.path.join(os.path.split(__file__)[0])
templatepath = os.path.join(webpath, 'template')


class HouseElement(athena.LiveElement):
    """ a 'live' house element.
    """
    docFactory = loaders.xmlfile(os.path.join(templatepath, 'houseElement.html'))
    jsClass = u'house.HouseWidget'

    def __init__(self, p_workspace_obj):
        self.m_workspace_obj = p_workspace_obj
        self.m_pyhouse_obj = p_workspace_obj.m_pyhouse_obj

    @athena.expose
    def getHouseData(self):
        l_house = GetJSONHouseInfo(self.m_pyhouse_obj)
        return l_house

    @athena.expose
    def saveHouseData(self, p_json):
        """House data has been returned, so update the house info.
        """
        l_json = JsonUnicode().decode_json(p_json)
        LOG.info('Update House info - {}'.format(l_json))
        l_delete = l_json['Delete']
        if l_delete:
            try:
                del self.m_pyhouse_obj.House
            except AttributeError:
                LOG.error("Failed to delete - JSON: {}".format(l_json))
            return
        self.m_pyhouse_obj.House.Name = l_json['Name']
        self.m_pyhouse_obj.House.Key = int(l_json['Key'])
        self.m_pyhouse_obj.House.Active = True
        self.m_pyhouse_obj.House.UUID
        l_obj = self.m_pyhouse_obj.House.Location
        l_obj.Street = l_json['Location']['Street']
        l_obj.City = l_json['Location']['City']
        l_obj.State = l_json['Location']['State']
        l_obj.ZipCode = l_json['Location']['ZipCode']
        l_obj.Region = l_json['Location']['Region']
        l_obj.Phone = l_json['Location']['Phone']
        l_obj.Latitude = l_json['Location']['Latitude']
        l_obj.Longitude = l_json['Location']['Longitude']
        l_obj.Elevation = l_json['Location']['Elevation']
        l_obj.TimeZoneName = l_json['Location']['TimeZoneName']
        self.m_pyhouse_obj.House.Location = l_obj

# ## END DBK
