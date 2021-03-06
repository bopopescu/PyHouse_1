"""
-*- test-case-name: PyHouse.src.Modules.Scheduling.test.test_schedule -*-

@name:      PyHouse/src/Modules/Scheduling/schedule.py
@author:    D. Brian Kimmel
@contact:   D.BrianKimmel@gmail.com
@copyright: (c) 2013-2016 by D. Brian Kimmel
@license:   MIT License
@note:      Created on Apr 8, 2013
@summary:   Schedule events


Handle the home automation system schedule for a house.

The schedule is at the Core of PyHouse.
Lighting events, entertainment events, etc. for one house are triggered by the schedule and are run by twisted.

Read/reread the schedule file at:
    1. Start up
    2. Midnight
    3. After each set of scheduled events.


Controls:
    Communication
    Entertainment
    HVAC
    Irrigation
    Lighting
    Pool
    Remote
    Security
    UPNP

Operation:

  Iterate thru the schedule tree and create a list of schedule events.
  Select the next event(s) from now, there may be more than one event scheduled for the same time.

  Create a twisted timer that goes off when the scheduled time arrives.
  We only create one timer (ATM) so that we do not have to cancel timers when the schedule is edited.
"""

#  Import system type stuff
import datetime
import dateutil.parser as dparser
import twisted

#  Import PyMh files
from Modules.Hvac.hvac_actions import API as hvacActionsAPI
from Modules.Irrigation.irrigation_action import API as irrigationActionsAPI
from Modules.Lighting.lighting_actions import API as lightActionsAPI
from Modules.Scheduling.schedule_xml import Xml as scheduleXml
from Modules.Computer import logging_pyh as Logger
from Modules.Scheduling import sunrisesunset
#  from Modules.Utilities.debug_tools import PrettyFormatAny

LOG = Logger.getLogger('PyHouse.Schedule       ')
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60  # 3600
SECONDS_IN_DAY = SECONDS_IN_HOUR * 24  # 86400
SECONDS_IN_WEEK = SECONDS_IN_DAY * 7  # 604800
INITIAL_DELAY = 5  # Must be from 5 to 30 seconds.
PAUSE_DELAY = 5


# twisted.internet.base.DelayedCall.debug = True


class RiseSet(object):
    def __init__(self):
        self.SunRise = None
        self.SunSet = None


class SchedTime(object):
    """
    Get the when scheduled time.  It may be from about a minute to about 1 week.
    If the schedule is not active return a None
    This class deals with extracting information from the time and DOW fields of a schedule.

    DOW        mon=1, tue=2, wed=4, thu=8, fri=16, sat=32, sun=64
    weekday    mon=0, tue=1, wed=2, thu=3, fri=4,  sat=5,  sun=6

    The time field may be:
        HH:MM or HH:MM:SS
        sunrise/sunset/dawn/dusk  +/-  offset HH:MM:SS or HH:MM
    """

    @staticmethod
    def _extract_days(p_schedule_obj, p_now):
        """ Get the number of days until the next DOW in the schedule.

        DOW        mon=1, tue=2, wed=4, thu=8, fri=16, sat=32, sun=64
        weekday()  mon=0, tue=1, wed=2, thu=3, fri=4,  sat=5,  sun=6

        @param p_schedule_obj: is the schedule object we are working on
        @param p_now: is a datetime.datetime.now()
        @return: the number of days till the next DOW - 0..6, 10 if never
        """
        l_dow = p_schedule_obj.DOW
        l_now_day = p_now.weekday()
        l_day = 2 ** l_now_day
        l_is_in_dow = (l_dow & l_day) != 0
        #  print("A ", l_dow, l_now_day, l_day, l_is_in_dow)
        if l_is_in_dow:
            return 0
        l_days = 1
        for _l_ix in range(0, 7):
            l_now_day = (l_now_day + 1) % 7
            l_day = 2 ** l_now_day
            l_is_in_dow = (l_dow & l_day) != 0
            #  print("B ", l_dow, l_now_day, l_day, l_is_in_dow)
            if l_is_in_dow:
                return l_days
            l_days += 1
        return 10

    @staticmethod
    def _extract_schedule_time(p_schedule_obj, p_rise_set):
        """Find the number of minutes from midnight until the schedule time for action.
        @return: the number of minutes
        """
        l_timefield = p_schedule_obj.Time.lower()
        l_time = dparser.parse(l_timefield, fuzzy = True)
        l_offset = l_time.hour * 60 + l_time.minute
        #
        if 'dawn' in l_timefield:
            l_base = Utility.to_mins(p_rise_set.Dawn)
        if 'sunrise' in l_timefield or 'dawn' in l_timefield:
            l_base = Utility.to_mins(p_rise_set.SunRise)
        elif 'sunset' in l_timefield or 'dusk' in l_timefield:
            l_base = Utility.to_mins(p_rise_set.SunSet)
        elif 'dusk' in l_timefield:
            l_base = Utility.to_mins(p_rise_set.Dusk)
        else:
            l_base = l_offset
        #
        if '-' in l_timefield:
            l_minutes = l_base - l_offset
        elif '+' in l_timefield:
            l_minutes = l_base + l_offset
        else:
            l_minutes = l_base
        #
        return l_minutes

    @staticmethod
    def extract_time_to_go(_p_pyhouse_obj, p_schedule_obj, p_now, p_rise_set):
        """Compute the seconds to go from now to the next scheduled time.
        @param p_pyhouse_obj: Not used yet
        @param p_schedule_obj: is the schedule object we are working on.
        @param p_now: is the datetime for now
        @param p_rise_set: is the sunrise/sunset structure
        """
        l_dow_mins = SchedTime._extract_days(p_schedule_obj, p_now) * 24 * 60
        l_sched_mins = SchedTime._extract_schedule_time(p_schedule_obj, p_rise_set)
        l_sched_secs = 60 * (l_dow_mins + l_sched_mins)
        #  print(l_dow, l_minutes, l_seconds)
        l_now_secs = Utility.to_mins(p_now) * 60
        l_seconds = l_sched_secs - l_now_secs
        if l_seconds < 0:
            l_seconds += SECONDS_IN_DAY
        return l_seconds


class ScheduleExecution(object):

    @staticmethod
    def dispatch_one_schedule(p_pyhouse_obj, p_schedule_obj):
        """
        Send information to one device to execute a schedule.
        """
        if p_schedule_obj.ScheduleType == 'Lighting':
            LOG.info('Execute_one_schedule type = Lighting')
            lightActionsAPI.DoSchedule(p_pyhouse_obj, p_schedule_obj)
        #
        elif p_schedule_obj.ScheduleType == 'Hvac':
            LOG.info('Execute_one_schedule type = Hvac')
            hvacActionsAPI.DoSchedule(p_pyhouse_obj, p_schedule_obj)
        #
        elif p_schedule_obj.ScheduleType == 'Irrigation':
            LOG.info('Execute_one_schedule type = Hvac')
            irrigationActionsAPI.DoSchedule(p_pyhouse_obj, p_schedule_obj)
        #
        elif p_schedule_obj.ScheduleType == 'TeStInG14159':  # To allow a path for unit tests
            LOG.info('Execute_one_schedule type = Testing')
            #  irrigationActionsAPI.DoSchedule(p_pyhouse_obj, p_schedule_obj)
        #
        else:
            LOG.error('Unknown schedule type: {}'.format(p_schedule_obj.ScheduleType))
            irrigationActionsAPI.DoSchedule(p_pyhouse_obj, p_schedule_obj)

    @staticmethod
    def execute_schedules_list(p_pyhouse_obj, p_key_list = []):
        """ The timer calls this when a list of schedules is due to be executed.
        For each Schedule in the list, call the dispatcher for that type of schedule.

        Delay before generating the next schedule to avoid a race condition
         that duplicates an event if it completes before the clock goes to the next second.

        @param p_key_list: a list of schedule keys in the next time schedule to be executed.
        """
        LOG.info("About to execute - Schedules:{}".format(p_key_list))
        for l_slot in range(len(p_key_list)):
            l_schedule_obj = p_pyhouse_obj.House.Schedules[p_key_list[l_slot]]
            ScheduleExecution.dispatch_one_schedule(p_pyhouse_obj, l_schedule_obj)
        Utility.schedule_next_event(p_pyhouse_obj)


class Utility(object):
    """
    """

    @staticmethod
    def _setup_components(p_pyhouse_obj):
        p_pyhouse_obj.House.Schedules = {}

    @staticmethod
    def to_mins(p_datetime):
        """ Convert a datetime to minutes since midnight.
        """
        l_mins = p_datetime.hour * 60 + p_datetime.minute
        return l_mins

    @staticmethod
    def fetch_sunrise_set(p_pyhouse_obj):
        l_sunrise = p_pyhouse_obj.House.Location.RiseSet.SunRise
        l_sunset = p_pyhouse_obj.House.Location.RiseSet.SunSet
        LOG.info('Got Sunrise: {};   Sunset: {}'.format(l_sunrise, l_sunset))
        l_riseset = RiseSet()
        l_riseset.SunRise = l_sunrise
        l_riseset.SunSet = l_sunset
        #  node_mqtt.API().doPublishMessage(p_pyhouse_obj.Computer.Mqtt, "pyhouse/schedule/sunrise", l_sunrise)
        return l_riseset

    @staticmethod
    def find_next_scheduled_events(p_pyhouse_obj, p_now):
        """ Go thru all the schedules and find the next schedule list to run.
        Note that there may be several scheduled events for that time

        @param p_now: is a datetime of now()
        """
        l_schedule_key_list = []
        l_min_seconds = SECONDS_IN_WEEK
        l_riseset = Utility.fetch_sunrise_set(p_pyhouse_obj)
        for l_key, l_schedule_obj in p_pyhouse_obj.House.Schedules.iteritems():
            if not l_schedule_obj.Active:
                continue
            l_seconds = SchedTime.extract_time_to_go(p_pyhouse_obj, l_schedule_obj, p_now, l_riseset)
            if l_seconds < 30:
                continue
            if l_min_seconds == l_seconds:  # Add to lists for the given time.
                l_schedule_key_list.append(l_key)
            elif l_seconds < l_min_seconds:  # earlier schedule - start new list
                l_min_seconds = l_seconds
                l_schedule_key_list = []
                l_schedule_key_list.append(l_key)
        l_debug_msg = "Delaying {} for list {}".format(l_min_seconds, l_schedule_key_list)
        LOG.info("find_next_scheduled_events complete. {}".format(l_debug_msg))
        return l_min_seconds, l_schedule_key_list

    @staticmethod
    def run_after_delay(p_pyhouse_obj, p_delay, p_list):
        l_runID = p_pyhouse_obj.Twisted.Reactor.callLater(p_delay, ScheduleExecution.execute_schedules_list, p_pyhouse_obj, p_list)
        l_datetime = datetime.datetime.fromtimestamp(l_runID.getTime())
        LOG.info('Scheduled {} after delay of {} - Time: {}'.format(p_list, p_delay, l_datetime))
        return l_runID

    @staticmethod
    def schedule_next_event(p_pyhouse_obj, p_delay = 0):
        """ Find the list of schedules to run, call the timer to run at the time in the schedules.
        @param p_pyhouse_obj: is the grand repository of information
        @param p_delay: is the (forced) delay time for the timer.
        """
        l_delay, l_list = Utility.find_next_scheduled_events(p_pyhouse_obj, datetime.datetime.now())
        if p_delay != 0:
            l_delay = p_delay
        Utility.run_after_delay(p_pyhouse_obj, l_delay, l_list)


class Timers(object):
    """
    """

    def __init__(self, p_pyhouse_obj):
        self.m_pyhouse_obj = p_pyhouse_obj
        self.m_timers = {}
        self.m_count = 0

    def set_one(self, p_pyhouse_obj, p_delay, p_list):
        l_callback = ScheduleExecution.execute_schedules_list
        l_runID = p_pyhouse_obj.Twisted.Reactor.callLater(p_delay, l_callback, p_pyhouse_obj, p_list)
        l_datetime = datetime.datetime.fromtimestamp(l_runID.getTime())
        LOG.info('Scheduled {} after delay of {} - Time: {}'.format(p_list, p_delay, l_datetime))
        return l_runID


class API(object):

    m_pyhouse_obj = None

    def __init__(self, p_pyhouse_obj):
        self.m_pyhouse_obj = p_pyhouse_obj
        Utility._setup_components(p_pyhouse_obj)
        LOG.info("Initialized.")

    def LoadXml(self, p_pyhouse_obj):
        """ Load the Schedule xml info.
        """
        l_schedules = scheduleXml.read_schedules_xml(p_pyhouse_obj)
        p_pyhouse_obj.House.Schedules = l_schedules
        LOG.info('Loaded {} Schedules XML'.format(len(l_schedules)))
        return l_schedules  # for testing

    def Start(self):
        """
        Extracts all from XML so an update will write correct info back out to the XML file.
        """
        sunrisesunset.API(self.m_pyhouse_obj).Start()
        self.RestartSchedule()
        LOG.info("Started.")

    def Stop(self):
        """Stop everything.
        """
        LOG.info("Stopped.")

    def SaveXml(self, p_xml):
        l_xml, l_count = scheduleXml.write_schedules_xml(self.m_pyhouse_obj.House.Schedules)
        p_xml.append(l_xml)
        LOG.info('Saved {} Schedules XML.'.format(l_count))
        return l_xml  # for testing

    def RestartSchedule(self):
        """ Anything that alters the schedules should call this to cause the new schedules to take effect.
        """
        self.m_pyhouse_obj.Twisted.Reactor.callLater(INITIAL_DELAY, Utility.schedule_next_event, self.m_pyhouse_obj)

# ## END DBK
