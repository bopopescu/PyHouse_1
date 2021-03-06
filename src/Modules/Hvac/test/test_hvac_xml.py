"""
@name:      PyHouse/src/Modules/Hvac/test/test_hvac_xml.py
@author:    D. Brian Kimmel
@contact:   D.BrianKimmel@gmail.com
@copyright: (c) 2015-2016 by D. Brian Kimmel
@license:   MIT License
@note:      Created on Jul 12, 2015
@Summary:

Passed all 16 tests - DBK - 2016-01-29

"""

#  Import system type stuff
from twisted.trial import unittest
import xml.etree.ElementTree as ET

#  Import PyMh files
from Modules.Core import conversions
from Modules.Core.test.xml_device import \
            TESTING_DEVICE_COMMENT, TESTING_DEVICE_ROOM_NAME, \
            TESTING_DEVICE_FAMILY_INSTEON
from Modules.Families.Insteon.test.xml_insteon import \
            TESTING_INSTEON_ADDRESS_0, TESTING_INSTEON_DEVCAT_0, \
            TESTING_INSTEON_GROUP_LIST_0, TESTING_INSTEON_GROUP_NUM_0, \
            TESTING_INSTEON_PRODUCT_KEY_0
from Modules.Hvac.hvac_xml import Utility, XML as hvacXML
from Modules.Hvac.test.xml_hvac import \
            TESTING_THERMOSTAT_NAME_0, TESTING_THERMOSTAT_ACTIVE_0, \
            TESTING_THERMOSTAT_KEY_0, TESTING_THERMOSTAT_COOL_SETPOINT_0, \
            TESTING_THERMOSTAT_DEVICE_FAMILY_0, \
            TESTING_THERMOSTAT_HEAT_SETPOINT_0, \
            TESTING_THERMOSTAT_MODE_0, \
            TESTING_THERMOSTAT_SCALE_0
from Modules.Utilities.debug_tools import PrettyFormatAny
from test.testing_mixin import SetupPyHouseObj
from test.xml_data import XML_LONG, XML_EMPTY


class SetupMixin(object):

    def setUp(self, p_root):
        self.m_pyhouse_obj = SetupPyHouseObj().BuildPyHouseObj(p_root)
        self.m_xml = SetupPyHouseObj().BuildXml(p_root)


class A1_XML(SetupMixin, unittest.TestCase):

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(XML_LONG))

    def test_01_BuildObjects(self):
        """ Test to be sure the compound object was built correctly.
        """
        self.assertEqual(self.m_pyhouse_obj.House.Hvac, None)


class A2_EmptyXML(SetupMixin, unittest.TestCase):

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(XML_EMPTY))

    def test_01_BuildObjects(self):
        """ Test to be sure the compound object was built correctly.
        """
        self.assertEqual(self.m_pyhouse_obj.House.Hvac, None)


class B1_PyHouse(SetupMixin, unittest.TestCase):

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(XML_LONG))

    def test_01_PyHouse(self):
        """Read the base device XML
        """
        self.m_pyhouse_obj.House.Hvac = hvacXML.read_hvac_xml(self.m_pyhouse_obj)
        self.assertNotEqual(self.m_pyhouse_obj.House.Hvac, None)


class C1_Read(SetupMixin, unittest.TestCase):

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(XML_LONG))

    def test_01_Base(self):
        """Read the base device XML
        """
        l_xml = self.m_xml.thermostat
        l_obj = Utility._read_base(l_xml)
        self.assertEqual(l_obj.Name, TESTING_THERMOSTAT_NAME_0)
        self.assertEqual(l_obj.Active, TESTING_THERMOSTAT_ACTIVE_0 == 'True')
        self.assertEqual(l_obj.Key, int(TESTING_THERMOSTAT_KEY_0))

    def test_02_BaseDevice(self):
        """Read the base device XML
        """
        l_xml = self.m_xml.thermostat
        l_obj = Utility._read_thermostat_base(l_xml)
        self.assertEqual(l_obj.Name, TESTING_THERMOSTAT_NAME_0)
        self.assertEqual(l_obj.Active, TESTING_THERMOSTAT_ACTIVE_0 == 'True')
        self.assertEqual(l_obj.Key, int(TESTING_THERMOSTAT_KEY_0))
        self.assertEqual(l_obj.Comment, TESTING_DEVICE_COMMENT)
        self.assertEqual(l_obj.DeviceFamily, TESTING_THERMOSTAT_DEVICE_FAMILY_0)
        self.assertEqual(l_obj.RoomName, TESTING_DEVICE_ROOM_NAME)

    def test_03_Thermostat(self):
        """Read the thermostat specific data.
        """
        l_xml = self.m_xml.thermostat
        l_obj = Utility._read_thermostat_base(l_xml)
        Utility._read_thermostat_data(l_obj, l_xml)
        self.assertEqual(l_obj.Name, TESTING_THERMOSTAT_NAME_0)
        self.assertEqual(l_obj.CoolSetPoint, float(TESTING_THERMOSTAT_COOL_SETPOINT_0))
        self.assertEqual(l_obj.HeatSetPoint, float(TESTING_THERMOSTAT_HEAT_SETPOINT_0))
        self.assertEqual(l_obj.ThermostatMode, TESTING_THERMOSTAT_MODE_0)
        self.assertEqual(l_obj.ThermostatScale, TESTING_THERMOSTAT_SCALE_0)

    def test_04_Family(self):
        """Read and add the family specific parts.
        """
        l_xml = self.m_xml.thermostat
        l_obj = Utility._read_thermostat_base(l_xml)
        Utility._read_thermostat_data(l_obj, l_xml)
        Utility._read_family_data(self.m_pyhouse_obj, l_obj, l_xml)
        self.assertEqual(conversions.int2dotted_hex(l_obj.InsteonAddress, 3), TESTING_INSTEON_ADDRESS_0)
        self.assertEqual(conversions.int2dotted_hex(l_obj.DevCat, 2), TESTING_INSTEON_DEVCAT_0)
        self.assertEqual(l_obj.GroupList, TESTING_INSTEON_GROUP_LIST_0)
        self.assertEqual(l_obj.GroupNumber, int(TESTING_INSTEON_GROUP_NUM_0))
        self.assertEqual(conversions.int2dotted_hex(l_obj.ProductKey, 3), TESTING_INSTEON_PRODUCT_KEY_0)

    def test_05_OneThermostat(self):
        """Read one thermostat entirely.
        """
        l_obj = Utility._read_one_thermostat_xml(self.m_pyhouse_obj, self.m_xml.thermostat)
        self.assertEqual(l_obj.Name, TESTING_THERMOSTAT_NAME_0)
        self.assertEqual(l_obj.CoolSetPoint, float(TESTING_THERMOSTAT_COOL_SETPOINT_0))
        self.assertEqual(conversions.int2dotted_hex(l_obj.InsteonAddress, 3), TESTING_INSTEON_ADDRESS_0)

    def test_06_AllThermostats(self):
        """Read all the thermostats on file.
        """
        l_obj = hvacXML.read_hvac_xml(self.m_pyhouse_obj)
        self.assertEqual(len(l_obj.Thermostats), 2)
        self.assertEqual(l_obj.Thermostats[0].Name, TESTING_THERMOSTAT_NAME_0)
        self.assertEqual(l_obj.Thermostats[0].CoolSetPoint, float(TESTING_THERMOSTAT_COOL_SETPOINT_0))


class C2_EmptyRead(SetupMixin, unittest.TestCase):

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(XML_EMPTY))

    def test_01_AllThermostats(self):
        """Read all the thermostats on file.
        """
        l_obj = hvacXML.read_hvac_xml(self.m_pyhouse_obj)
        self.assertEqual(len(l_obj.Thermostats), 0)


class D1_Write(SetupMixin, unittest.TestCase):

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(XML_LONG))

    def test_01_Base(self):
        """Write the base device.
        """
        l_obj = Utility._read_one_thermostat_xml(self.m_pyhouse_obj, self.m_xml.thermostat)
        l_xml = Utility._write_thermostat_base('Thermostat', l_obj)
        self.assertEqual(self.m_pyhouse_obj.House.Hvac, None)
        self.assertEqual(l_xml.attrib['Name'], TESTING_THERMOSTAT_NAME_0)
        self.assertEqual(l_xml.attrib['Key'], TESTING_THERMOSTAT_KEY_0)
        self.assertEqual(l_xml.attrib['Active'], TESTING_THERMOSTAT_ACTIVE_0)
        self.assertEqual(l_xml.find('Comment').text, TESTING_DEVICE_COMMENT)
        self.assertEqual(l_xml.find('DeviceFamily').text, TESTING_DEVICE_FAMILY_INSTEON)
        self.assertEqual(l_xml.find('RoomName').text, TESTING_DEVICE_ROOM_NAME)

    def test_02_BaseDevice(self):
        """Write the base device.
        """
        l_obj = Utility._read_one_thermostat_xml(self.m_pyhouse_obj, self.m_xml.thermostat)
        l_xml = Utility._write_thermostat_base('Thermostat', l_obj)
        self.assertEqual(self.m_pyhouse_obj.House.Hvac, None)
        self.assertEqual(l_xml.attrib['Name'], TESTING_THERMOSTAT_NAME_0)
        self.assertEqual(l_xml.attrib['Key'], TESTING_THERMOSTAT_KEY_0)
        self.assertEqual(l_xml.attrib['Active'], TESTING_THERMOSTAT_ACTIVE_0)
        self.assertEqual(l_xml.find('Comment').text, TESTING_DEVICE_COMMENT)
        self.assertEqual(l_xml.find('DeviceFamily').text, TESTING_DEVICE_FAMILY_INSTEON)
        self.assertEqual(l_xml.find('RoomName').text, TESTING_DEVICE_ROOM_NAME)

    def test_03_Thermostat(self):
        """ Write the thermostat specific data to XML
        """
        l_obj = Utility._read_one_thermostat_xml(self.m_pyhouse_obj, self.m_xml.thermostat)
        l_xml = Utility._write_thermostat_base('Thermostat', l_obj)
        Utility._write_thermostat_data(l_xml, l_obj)
        self.assertEqual(self.m_pyhouse_obj.House.Hvac, None)
        self.assertEqual(l_xml.attrib['Name'], TESTING_THERMOSTAT_NAME_0)
        self.assertEqual(l_xml.attrib['Key'], TESTING_THERMOSTAT_KEY_0)
        self.assertEqual(l_xml.attrib['Active'], TESTING_THERMOSTAT_ACTIVE_0)
        self.assertEqual(l_xml.find('Comment').text, TESTING_DEVICE_COMMENT)
        self.assertEqual(l_xml.find('CoolSetPoint').text, TESTING_THERMOSTAT_COOL_SETPOINT_0)

    def test_04_Family(self):
        """Write family data to XML
        """
        l_obj = Utility._read_one_thermostat_xml(self.m_pyhouse_obj, self.m_xml.thermostat)
        l_xml = Utility._write_thermostat_base('Thermostat', l_obj)
        Utility._write_thermostat_data(l_xml, l_obj)
        Utility._write_family_data(self.m_pyhouse_obj, l_obj, l_xml)
        self.assertEqual(l_xml.attrib['Name'], TESTING_THERMOSTAT_NAME_0)
        self.assertEqual(l_xml.find('InsteonAddress').text, TESTING_INSTEON_ADDRESS_0)
        self.assertEqual(l_xml.find('DevCat').text, TESTING_INSTEON_DEVCAT_0)
        self.assertEqual(l_xml.find('GroupList').text, TESTING_INSTEON_GROUP_LIST_0)
        self.assertEqual(l_xml.find('GroupNumber').text, TESTING_INSTEON_GROUP_NUM_0)
        self.assertEqual(l_xml.find('ProductKey').text, TESTING_INSTEON_PRODUCT_KEY_0)

    def test_05_OneThermostat(self):
        """Write one complete thermostat
        """
        l_obj = Utility._read_one_thermostat_xml(self.m_pyhouse_obj, self.m_xml.thermostat)
        l_xml = Utility._write_one_thermostat_xml(self.m_pyhouse_obj, l_obj)
        self.assertEqual(self.m_pyhouse_obj.House.Hvac, None)
        self.assertEqual(l_xml.attrib['Name'], TESTING_THERMOSTAT_NAME_0)
        self.assertEqual(l_xml.attrib['Key'], TESTING_THERMOSTAT_KEY_0)
        self.assertEqual(l_xml.attrib['Active'], TESTING_THERMOSTAT_ACTIVE_0)
        self.assertEqual(l_xml.find('Comment').text, TESTING_DEVICE_COMMENT)
        self.assertEqual(l_xml.find('CoolSetPoint').text, TESTING_THERMOSTAT_COOL_SETPOINT_0)
        self.assertEqual(l_xml.find('InsteonAddress').text, TESTING_INSTEON_ADDRESS_0)
        self.assertEqual(l_xml.find('DevCat').text, TESTING_INSTEON_DEVCAT_0)
        self.assertEqual(l_xml.find('GroupList').text, TESTING_INSTEON_GROUP_LIST_0)
        self.assertEqual(l_xml.find('GroupNumber').text, TESTING_INSTEON_GROUP_NUM_0)
        self.assertEqual(l_xml.find('ProductKey').text, TESTING_INSTEON_PRODUCT_KEY_0)

    def test_06_All(self):
        """ Write all thermostats
        """
        l_objs = hvacXML.read_hvac_xml(self.m_pyhouse_obj)
        self.m_pyhouse_obj.House.Hvac = l_objs
        l_xml = ET.Element('HvacSection')
        l_xml = hvacXML.write_hvac_xml(self.m_pyhouse_obj, l_xml)
        self.assertEqual(l_xml.find('ThermostatSection/Thermostat/Comment').text, TESTING_DEVICE_COMMENT)

#  ## END DBK
