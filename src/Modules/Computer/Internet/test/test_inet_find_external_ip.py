"""
@name:      PyHouse/src/Modules/Computer/Internet/test/test_inet_find_external_ip.py
@author:    D. Brian Kimmel
@contact:   D.BrianKimmel@gmail.com>
@copyright: (c) 2014-2015 by D. Brian Kimmel
@license:   MIT License
@note:      Created on Jun 27, 2014
@Summary:   Test finding an external IP address.

Passed all 3 tests - DBK - 2015-09-12

"""

# Import system type stuff
import xml.etree.ElementTree as ET
from twisted.trial import unittest

# Import PyMh files and modules.
from Modules.Computer.Internet import inet_find_external_ip
from test.xml_data import XML_LONG
from test.testing_mixin import SetupPyHouseObj


class SetupMixin(object):
    """
    Set up pyhouse_obj and xml element pointers
    """

    def setUp(self, p_root):
        self.m_pyhouse_obj = SetupPyHouseObj().BuildPyHouseObj(p_root)
        self.m_xml = SetupPyHouseObj().BuildXml(p_root)


class C1_Util(SetupMixin, unittest.TestCase):

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(XML_LONG))
        self.m_reactor = self.m_pyhouse_obj.Twisted.Reactor
        self.m_api = inet_find_external_ip.API()

    def test_01_IPv4_addr(self):
        pass

    def test_02_scrape(self):
        l_body = 'Current IP Address: 216.16.166.42'
        l_ip = self.m_api._scrape_body(l_body)
        self.assertEqual(l_ip, '216.16.166.42')
        l_body = '50.16.166.2'
        l_ip = self.m_api._scrape_body(l_body)
        self.assertEqual(l_ip, '50.16.166.2')

    def test_06_snar3(self):
        l_defer = self.m_api.get_public_ip(self.m_pyhouse_obj, 0)
        return l_defer

# ## END DBK
