"""
@name:      PyHouse/src/Modules/web/test/test_web_clock.py
@author:    D. Brian Kimmel
@contact:   D.BrianKimmel@gmail.com>
@copyright: (c) 2014-2015 by briank
@license:   MIT License
@note:      Created on Jun 21, 2014
@Summary:

"""

# Import system type stuff
from twisted.trial import unittest
import xml.etree.ElementTree as ET

# Import PyMh files and modules.
from test import xml_data
from test.testing_mixin import SetupPyHouseObj


class SetupMixin(object):
    """
    """

    def setUp(self, p_root):
        self.m_pyhouse_obj = SetupPyHouseObj().BuildPyHouseObj(p_root)
        self.m_xml = SetupPyHouseObj().BuildXml(p_root)


class Test(SetupMixin, unittest.TestCase):

    def setUp(self):
        SetupMixin.setUp(self, ET.fromstring(xml_data.XML_LONG))

    def testName(self):
        pass

# ## END DBK
