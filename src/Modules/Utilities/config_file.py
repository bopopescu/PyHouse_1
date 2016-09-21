"""
-*- test-case-name: PyHouse.src.Modules.Utilities.test.test_config_file -*-

@name:      PyHouse/src/Modules/Utilities/config_file.py
@author:    D. Brian Kimmel
@contact:   D.BrianKimmel@gmail.com>
@copyright: (c) 2014-2016 by D. Brian Kimmel
@license:   MIT License
@note:      Created on Jul 15, 2014
@Summary:   This handles creation, read and write of the XML Config file.

"""


#  Import system type stuff
import datetime
#  from distutils.version import Version
import os
from xml.etree import ElementTree as ET

#  Import PyMh files
from Modules.Computer import logging_pyh as Logger
from Modules.Utilities.xml_tools import PutGetXML

LOG = Logger.getLogger('PyHouse.ConfigFile     ')
XML_FILE_NAME = '/etc/pyhouse/master.xml'


class Util(object):
    """
    Private utilities for this module.
    """

    @staticmethod
    def _create_empty_config_file(p_pyhouse_obj):
        """
        Internal - Create an empty skeleton XML config file.
        """
        l_top = Util()._create_empty_xml_skeleton(p_pyhouse_obj)
        l_comment = ET.Comment('Generated by PyHouse {0:}'.format(datetime.datetime.now()))
        l_top.append(l_comment)
        open(os.path.expanduser(p_pyhouse_obj.Xml.XmlFileName), 'w')
        ET.ElementTree(l_top).write(p_pyhouse_obj.Xml.XmlFileName)

    @staticmethod
    def _open_config_file(p_pyhouse_obj):
        """
        This is not really needed, it is here so we can test the file in unit testing (if needed).
        """
        if p_pyhouse_obj.Xml.XmlFileName is None:
            p_pyhouse_obj.Xml.XmlFileName = XML_FILE_NAME
        try:
            l_file = open(p_pyhouse_obj.Xml.XmlFileName, mode = 'r')
        except IOError as e_err:
            LOG.error(" -- Error in open_config_file {}".format(e_err))
            l_file = None
        return l_file

    @staticmethod
    def _create_empty_xml_skeleton(p_pyhouse_obj):
        l_xml = ET.Element("PyHouse")
        PutGetXML.put_text_attribute(l_xml, 'Version', p_pyhouse_obj.Xml.XmlVersion)
        PutGetXML.put_text_attribute(l_xml, 'xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        PutGetXML.put_text_attribute(l_xml, 'xsi:schemaLocation', 'http://PyHouse.org schemas/PyHouse.xsd')
        PutGetXML.put_text_attribute(l_xml, 'xmlns:comp', 'http://PyHouse.Org/ComputerDiv')
        l_xml.append(ET.Comment(' Updated by PyHouse {} '.format(datetime.datetime.now())))
        return l_xml


class API(object):

    g_pyhouse_obj = None

    def __init__(self, p_pyhouse_obj):
        self.m_pyhouse_obj = p_pyhouse_obj

    @staticmethod
    def get_xml_config_file_version(p_pyhouse_obj):
        """Get the value of the Version attribute of ???
        """
        l_root = p_pyhouse_obj.Xml.XmlRoot.find('.')
        l_ret = PutGetXML.get_text_from_xml(l_root, 'Version')
        return l_ret

    @staticmethod
    def read_xml_config_file(p_pyhouse_obj):
        """
        This will open and parse the XML config file.
        This puts the XML tree and file name in the pyhouse object for use by various modules.

        This does not load the information contained in the config file.
        """
        global g_pyhouse_obj
        g_pyhouse_obj = p_pyhouse_obj
        if p_pyhouse_obj.Xml.XmlFileName is None:
            p_pyhouse_obj.Xml.XmlFileName = XML_FILE_NAME
        try:
            l_xmltree = ET.parse(p_pyhouse_obj.Xml.XmlFileName)
        except (SyntaxError, IOError) as e_error:
            Util()._create_empty_config_file(p_pyhouse_obj)
            l_xmltree = ET.parse(p_pyhouse_obj.Xml.XmlFileName)
            LOG.warning("No config file found - Error:{}\n   Empty config file created.".format(e_error))

        p_pyhouse_obj.Xml.XmlRoot = l_xmltree.getroot()
        l_version = p_pyhouse_obj.Xml.XmlRoot.attrib['Version']
        if l_version == 'None':
            l_version = '1.0'
        p_pyhouse_obj.Xml.XmlOldVersion = l_version
        LOG.info('Using Config File: {} - Version: {}'.format(p_pyhouse_obj.Xml.XmlFileName, l_version))
        return p_pyhouse_obj  # For testing

    @staticmethod
    def create_xml_config_foundation(p_pyhouse_obj):
        """
        Create the "PyHouse" top element of the XML config file.
        The other divisions are appended to this foundation.
        """
        l_xml = ET.Element("PyHouse")
        PutGetXML.put_text_attribute(l_xml, 'Version', p_pyhouse_obj.Xml.XmlVersion)
        PutGetXML.put_text_attribute(l_xml, 'xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        PutGetXML.put_text_attribute(l_xml, 'xsi:schemaLocation', 'http://PyHouse.org schemas/PyHouse.xsd')
        PutGetXML.put_text_attribute(l_xml, 'xmlns:comp', 'http://PyHouse.Org/ComputerDiv')
        l_xml.append(ET.Comment(' Updated by PyHouse {} '.format(datetime.datetime.now())))
        return l_xml

    @staticmethod
    def write_xml_config_file(p_pyhouse_obj, p_xmltree):
        """
        Note!
        @param p_xml_tree: is the tree body part to write
        """
        try:
            l_tree = ET.ElementTree()
            l_tree._setroot(p_xmltree)
            l_tree.write(p_pyhouse_obj.Xml.XmlFileName, xml_declaration = True)
        except AttributeError as e_err:
            LOG.error('Err:{}\n\t{}'.format(e_err, repr(p_xmltree)))

#  ## END DBK