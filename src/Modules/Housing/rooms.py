"""
-*- test-case-name: PyHouse.src.Modules.Housing.test.test_rooms -*-

@name:      PyHouse/src/Modules/Housing/rooms.py
@author:    D. Brian Kimmel
@contact:   D.BrianKimmel@gmail.com
@copyright: (c) 2013-2016 by D. Brian Kimmel
@license:   MIT License
@note:      Created on Apr 10, 2013
@summary:   Handle the rooms information for a house.

"""

#  Import system type stuff
import xml.etree.ElementTree as ET
import datetime

#  Import PyMh files
from Modules.Core.data_objects import RoomData
from Modules.Utilities.coordinate_tools import Coords
from Modules.Utilities.json_tools import encode_json
from Modules.Utilities.xml_tools import PutGetXML, XmlConfigTools
from Modules.Computer import logging_pyh as Logger
from Modules.Utilities.debug_tools import PrettyFormatAny

LOG = Logger.getLogger('PyHouse.Rooms          ')
TOPIC_DELETE = 'room/delete'


class Xml(object):
    """ Class to read and write the XML config file for PyHouse.
    """

    @staticmethod
    def read_one_room(p_room_element):
        l_room_obj = RoomData()
        try:
            XmlConfigTools.read_base_object_xml(l_room_obj, p_room_element)
            l_room_obj.Comment = PutGetXML.get_text_from_xml(p_room_element, 'Comment')
            l_room_obj.Corner = PutGetXML.get_coords_from_xml(p_room_element, 'Corner')
            l_room_obj.Floor = PutGetXML.get_text_from_xml(p_room_element, 'Floor', '1')
            l_room_obj.LastUpdate = PutGetXML.get_date_time_from_xml(p_room_element, 'LastUpdate')
            l_room_obj.Size = PutGetXML.get_coords_from_xml(p_room_element, 'Size')
            l_room_obj.RoomType = PutGetXML.get_text_from_xml(p_room_element, 'RoomType')
        except:
            LOG.warn('Incomplete data for room {}'.format(l_room_obj.Name))
        return l_room_obj

    @staticmethod
    def write_one_room(p_room_object):
        l_entry = XmlConfigTools.write_base_object_xml('Room', p_room_object)
        PutGetXML.put_text_element(l_entry, 'Comment', p_room_object.Comment)
        PutGetXML.put_coords_element(l_entry, 'Corner', p_room_object.Corner)
        PutGetXML.put_text_element(l_entry, 'Floor', p_room_object.Floor)
        PutGetXML.put_date_time_element(l_entry, 'LastUpdate', p_room_object.LastUpdate)
        PutGetXML.put_coords_element(l_entry, 'Size', p_room_object.Size)
        PutGetXML.put_text_element(l_entry, 'RoomType', p_room_object.RoomType)
        return l_entry

    @staticmethod
    def read_rooms_xml(p_pyhouse_obj):
        """
        @param p_house_obj: is
        @param p_house_xml: is
        """
        l_ret = {}
        l_count = 0
        l_xml = p_pyhouse_obj.Xml.XmlRoot
        l_xml = l_xml.find('HouseDivision')
        if l_xml is None:
            return l_ret
        l_xml = l_xml.find('RoomSection')
        if l_xml is None:
            return l_ret
        try:
            for l_room_xml in l_xml.iterfind('Room'):
                # print(PrettyFormatAny.form(l_room_xml, 'room xml'))
                l_room_obj = Xml.read_one_room(l_room_xml)
                l_room_obj.Key = l_count
                l_ret[l_count] = l_room_obj
                LOG.info('Loaded room {}'.format(l_room_obj.Name))
                l_count += 1
        except AttributeError as e_err:
            LOG.error('ERROR if getting rooms Data - {}'.format(e_err))
        LOG.info('Loaded {} rooms.'.format(l_count))
        return l_ret

    @staticmethod
    def write_rooms_xml(p_rooms_obj):
        l_rooms_xml = ET.Element('RoomSection')
        l_count = 0
        for l_room_object in p_rooms_obj.itervalues():
            l_room_object.Key = l_count
            l_entry = Xml.write_one_room(l_room_object)
            l_rooms_xml.append(l_entry)
            l_count += 1
        LOG.info('Saved {} Rooms XML'.format(l_count))
        return l_rooms_xml


class Maint(object):
    """ Maintain the room internal database.
    """

    @staticmethod
    def _json_2_obj(p_json):
        l_obj = RoomData()
        l_obj.Name = p_json['Name']
        l_obj.Active = p_json['Active']
        l_obj.Key = 0
        l_obj.UUID = p_json['UUID']
        l_obj.Comment = p_json['Comment']
        l_obj.Corner = Coords._get_coords(p_json['Corner'])
        l_obj.Floor = p_json['Floor']
        l_obj.Size = Coords._get_coords(p_json['Size'])
        l_obj.RoomType = p_json['RoomType']
        l_obj._AddFlag = p_json['Add']
        l_obj._DeleteFlag = p_json['Delete']
        return l_obj

    def from_web(self, p_pyhouse_obj, p_json):
        """ The web browser has sent back an add/change/delete request.
        """
        LOG.warn('Room debug {}'.format(p_json))
        l_obj = Maint._json_2_obj(p_json)
        if l_obj._DeleteFlag:
            l_room = Sync.find_room_uuid(p_pyhouse_obj, l_obj.UUID)
            if l_room is None:
                LOG.error("Trying to delete non existent room {}".format(l_obj.Name))
            else:
                LOG.info('Deleting Room {}'.format(l_obj.Name))
                Maint._delete_room(p_pyhouse_obj, l_obj)
        else:  # Add/Change
            l_rooms = self._add_change_room(p_pyhouse_obj, l_obj)
            p_pyhouse_obj.House.Rooms = l_rooms

    def _add_change_room(self, p_pyhouse_obj, p_room_obj):
        """
        Update a room or add a new room if the UUID does not exist
        """
        l_rooms = p_pyhouse_obj.House.Rooms
        l_len = len(l_rooms)
        for l_key, l_val in l_rooms.iteritems():
            if l_val.UUID == p_room_obj.UUID:
                LOG.info('Updating room {}'.format(p_room_obj.Name))
                l_rooms[l_key] = l_val
                l_rooms[l_key].LastUpda = datetime.datetime.now()
                return

        if Rooms(p_pyhouse_obj).find_room_uuid(p_pyhouse_obj, p_room_obj.UUID) is None and p_room_obj._DeleteFlag:
            pass
        l_msg = 'Adding room {} {}'.format(p_room_obj.Name, p_room_obj.Key)
        p_room_obj.Key = l_len
        p_room_obj.LastUpdate = datetime.datetime.now()
        l_rooms[len(l_rooms)] = p_room_obj
        print l_msg
        LOG.info(l_msg)
        p_pyhouse_obj.House.Rooms = l_rooms
        # p_pyhouse_obj.APIs.Computer.MqttAPI.MqttPublish("room/add", l_obj)
        return l_rooms

    @staticmethod
    def _delete_room(p_pyhouse_obj, p_room_obj):
        l_room_ix = int(p_room_obj.Key)
        try:
            del p_pyhouse_obj.House.Rooms[l_room_ix]
        except AttributeError:
            LOG.error("web_rooms - Failed to delete - JSON: {}".format(p_room_obj.Name))
        # p_pyhouse_obj.APIs.Computer.MqttAPI.MqttPublish("room/delete", p_json)
        return

    def sync_room(self, p_pyhouse_obj, p_room_obj):
        """ This can get to be a problem.
        A node uses its own UUID for a room created on that node.
        Room names might be slightly different on different nodes (Living Room vs Livingroom)
        We need to get to a single UUID to identify a room somehow.
        """
        pass


class Mqtt(object):
    """
    """

    def _decode_room(self, p_logmsg, p_topic, p_message):
        p_logmsg += '\tRooms:\n'
        if p_topic[1] == 'add':
            p_logmsg += '\tName: {}\n'.format(self._get_field(p_message, 'Name'))
        elif p_topic[1] == 'delete':
            p_logmsg += '\tName: {}\n'.format(self._get_field(p_message, 'Name'))
        elif p_topic[1] == 'sync':
            p_logmsg += '\tName: {}\n'.format(self._get_field(p_message, 'Name'))
        elif p_topic[1] == 'update':
            p_logmsg += '\tName: {}\n'.format(self._get_field(p_message, 'Name'))
        else:
            p_logmsg += '\tUnknown sub-topic {}'.format(PrettyFormatAny.form(p_message, 'Rooms msg', 160))
        return p_logmsg

    def dispatch(self, p_topic, p_message):
        pass

    def send_message(self, p_pyhouse_obj, p_topic, p_room_obj):
        """ Messages are:
                room/add - to add a new room to the database.
                room/delete - to delete a room from all nodes
                room/sync - to keep all nodes in sync periodically.
                room/update - to add or modify a room
        """
        l_json = encode_json(p_room_obj)
        p_pyhouse_obj.APIs.Computer.MqttAPI.MqttPublish(p_topic, l_json)


class Sync(object):
    """ Used to sync the rooms between all the nodes.
    """

    def find_room_name(self, p_pyhouse_obj, p_name):
        l_rooms = p_pyhouse_obj.House.Rooms
        for l_room in l_rooms.itervalues():
            if l_room.Name == p_name:
                return l_room
        return None

    def find_room_uuid(self, p_pyhouse_obj, p_uuid):
        l_rooms = p_pyhouse_obj.House.Rooms
        for l_room in l_rooms.itervalues():
            if l_room.UUID == p_uuid:
                return l_room
        return None


class Rooms(Sync, Xml, Maint):
    """
    """

    def __init__(self, p_pyHouse_obj):
        self.m_pyhouse_obj = p_pyHouse_obj

#  ## END DBK
