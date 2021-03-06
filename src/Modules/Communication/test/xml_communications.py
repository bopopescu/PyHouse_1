"""
@name:      PyHouse/src/Modules/Communication/test/xml_communications.py
@author:    D. Brian Kimmel
@contact:   D.BrianKimmel@gmail.com
@copyright: (c) 2014-2016 by D. Brian Kimmel
@license:   MIT License
@note:      Created on Nov 17, 2014
@Summary:

"""


L_EMAIL_START = '<EmailSection>'
L_EMAIL_END = '</EmailSection>'

TESTING_EMAIL_FROM_ADDRESS = 'mail.sender@Gmail.Com'
TESTING_EMAIL_TO_ADDRESS = 'mail.receiver@Gmail.Com'
TESTING_GMAIL_LOGIN = 'TestAccount@Gmail.Com'
TESTING_GMAIL_PASSWORD = 'Test=!=Password'

L_EMAIL_FROM_ADDRESS = '<EmailFromAddress>' + TESTING_EMAIL_FROM_ADDRESS + '</EmailFromAddress>'
L_EMAIL_TO_ADDRESS = '<EmailToAddress>' + TESTING_EMAIL_TO_ADDRESS + '</EmailToAddress>'
L_GMAIL_LOGIN = '<GmailLogin>' + TESTING_GMAIL_LOGIN + '</GmailLogin>'
L_GMAIL_PASSWORD = '<GmailPassword>' + TESTING_GMAIL_PASSWORD + '</GmailPassword>'

XML_EMAIL = '\n'.join([
    L_EMAIL_START,
    L_EMAIL_FROM_ADDRESS,
    L_EMAIL_TO_ADDRESS,
    L_GMAIL_LOGIN,
    L_GMAIL_PASSWORD,
    L_EMAIL_END
])

L_TWITTER_START = '<TwitterSection>'
L_TWITTER_END = '</TwitterSection>'

TESTING_CONSUMER_KEY = 'ABCDEFGHIJKLKMNOPQRSTUVWXYZ'
TESTING_CONSUMER_SECRET = '1234567890ABCDEFGHIJKLKMNOPQRSTUVWXYZ'
TESTING_ACCESS_KEY = 'ZYXWVUTSRQPONMLKJIHFEDCBA'
TESTING_ACCESS_SECRET = '0987654321ZYXWVUTSRQPONMLKJIHFEDCBA'

L_CONSUMER_KEY = '    <ConsumerKey>' + TESTING_CONSUMER_KEY + '</ConsumerKey>'
L_CONSUMER_SECRET = '    <ConsumerSecret>' + TESTING_CONSUMER_SECRET + '</ConsumerSecret>'
L_ACCESS_KEY = '    <AccessKey>' + TESTING_ACCESS_KEY + '</AccessKey>'
L_ACCESS_SECRET = '    <AccessSecret>' + TESTING_ACCESS_SECRET + '</AccessSecret>'


XML_TWITTER = '\n'.join([
    L_TWITTER_START,
    L_CONSUMER_KEY,
    L_CONSUMER_SECRET,
    L_ACCESS_KEY,
    L_ACCESS_SECRET,
    L_TWITTER_END
])

L_COMMUNICATION_START = '<CommunicationSection>'
L_COMMUNICATION_END = '</CommunicationSection>'

XML_COMMUNICATION = '\n'.join([
    L_COMMUNICATION_START,
    XML_EMAIL,
    XML_TWITTER,
    L_COMMUNICATION_END
])

# ## END DBK
