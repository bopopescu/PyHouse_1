"""
@name:      PyHouse/src/Modules/housing/test/test_house.py
@author:    D. Brian Kimmel
@contact:   D.BrianKimmel@gmail.com
@copyright: (c) 2013-2016 by D. Brian Kimmel
@license:   MIT License
@note:      Created on Apr 8, 2013
@summary:   Test handling the information for a house.


Passed all 7 tests - DBK - 2016-07-02
"""

# Import system type stuff
import xml.etree.ElementTree as ET
from twisted.trial import unittest

# Import PyMh files and modules.
from Modules.Housing.house import \
    API as houseAPI, \
    Xml as houseXml, \
    Utility as houseUtil
from Modules.Housing.test.xml_location import TESTING_LOCATION_STREET, TESTING_LOCATION_LATITUDE
from Modules.Housing.test.xml_rooms import TESTING_ROOM_NAME_0
from Modules.Housing.test.xml_housing import \
    TESTING_HOUSE_NAME, \
    TESTING_HOUSE_KEY, \
    TESTING_HOUSE_ACTIVE, \
    TESTING_HOUSE_UUID
from Modules.Utilities import json_tools
from test import xml_data
from test.testing_mixin import SetupPyHouseObj
from Modules.Utilities.debug_tools import PrettyFormatAny


class SetupMixin(object):

    def setUp(self, p_root):
        self.m_pyhouse_obj = SetupPyHouseObj().BuildPyHouseObj(p_root)
        self.m_xml = SetupPyHouseObj().BuildXml(p_root)
        self.m_api = houseAPI(self.m_pyhouse_obj)


class A1_Setup(SetupMixin, unittest.TestCase):
    """
    This section will verify the XML in the 'Modules.text.xml_data' file is correct and what the node_local
        module can read/write.
    """

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(xml_data.XML_LONG))

    def test_01_read_xml(self):
        self.assertEqual(self.m_xml.root.tag, 'PyHouse')
        self.assertEqual(self.m_xml.house_div.tag, 'HouseDivision')


class A2_Xml(SetupMixin, unittest.TestCase):
    """
    This section will verify the XML in the 'Modules.text.xml_data' file is correct and what the node_local
        module can read/write.
    """

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(xml_data.XML_LONG))

    def test_1_read_xml(self):
        l_pyhouse = self.m_xml.root
        self.assertEqual(l_pyhouse.tag, 'PyHouse')

    def test_2_buildObjects(self):
        """ Test to be sure the compound object was built correctly - Rooms is an empty dict.
        """
        print(PrettyFormatAny.form(self.m_pyhouse_obj.House, 'A2-2-A - House'))
        self.assertEqual(self.m_pyhouse_obj.House.Rooms, None)


class B1_Read(SetupMixin, unittest.TestCase):
    """
    This section tests the reading and writing of XML used by house.
    """

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(xml_data.XML_LONG))

    def test_1_API(self):
        houseUtil._init_component_apis(self.m_pyhouse_obj, self)
        # print(PrettyFormatAny.form(self.m_pyhouse_obj, 'B1-1-A - XML'))
        self.assertEqual(self.m_pyhouse_obj.Uuids, {})

    def test_2_Base(self):
        l_obj = houseXml._read_house_base(self.m_pyhouse_obj)
        # print(PrettyFormatAny.form(l_obj, 'B1-2-A - XML'))
        self.assertEqual(l_obj.Name, TESTING_HOUSE_NAME)
        self.assertEqual(str(l_obj.Key), TESTING_HOUSE_KEY)
        self.assertEqual(str(l_obj.Active), TESTING_HOUSE_ACTIVE)
        self.assertEqual(l_obj.UUID, TESTING_HOUSE_UUID)

    def test_3_House(self):
        l_obj = houseXml.read_house_xml(self.m_pyhouse_obj)
        print(PrettyFormatAny.form(l_obj, 'B1-3-A - XML'))
        self.assertEqual(l_obj.Name, TESTING_HOUSE_NAME)
        self.assertEqual(str(l_obj.Key), TESTING_HOUSE_KEY)
        self.assertEqual(str(l_obj.Active), TESTING_HOUSE_ACTIVE)
        self.assertEqual(l_obj.UUID, TESTING_HOUSE_UUID)
        self.assertEqual(str(l_obj.Location.Latitude), TESTING_LOCATION_LATITUDE)
        self.assertEqual(l_obj.Rooms[0].Name, TESTING_ROOM_NAME_0)


    def test_4_House(self):
        l_obj = houseXml.read_house_xml(self.m_pyhouse_obj)
        print(PrettyFormatAny.form(l_obj, 'B1-4-A - XML'))
        self.assertEqual(l_obj.Name, TESTING_HOUSE_NAME)
        self.assertEqual(str(l_obj.Key), TESTING_HOUSE_KEY)
        self.assertEqual(str(l_obj.Active), TESTING_HOUSE_ACTIVE)
        self.assertEqual(l_obj.UUID, TESTING_HOUSE_UUID)

class C03_Write(SetupMixin, unittest.TestCase):
    """
    This section tests the reading and writing of XML used by house.
    """

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(xml_data.XML_LONG))

    def test_01_House(self):
        l_house_obj = houseXml.read_house_xml(self.m_pyhouse_obj)
        self.m_pyhouse_obj.House = l_house_obj
        l_xml = houseXml.write_house_xml(self.m_pyhouse_obj)
        print(PrettyFormatAny.form(l_xml, 'XML'))
        self.assertEqual(l_xml.tag, 'HouseDivision')
        self.assertEqual(l_xml.attrib['Name'], TESTING_HOUSE_NAME)


class Z1_JSON(SetupMixin, unittest.TestCase):
    """
    This section tests the reading and writing of XML used by house.
    """

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(xml_data.XML_LONG))

    def test_01_Create(self):
        """ Create a JSON object for Location.5
        """
        l_house = houseXml.read_house_xml(self.m_pyhouse_obj)
        print('House: {0:}'.format(l_house))
        l_json = json_tools.encode_json(l_house)
        print('JSON: {0:}'.format(l_json))

# ## END DBK
