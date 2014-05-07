"""
Simple logging handler for sending gelf messages via TCP or UDP
Author: Stewart Rutledge <stew.rutledge AT gmail.com>
License: BSD I guess
"""
import logging
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, getfqdn
from json import dumps
from zlib import compress


class handler(logging.Handler):

    def __init__(self, **kw):
        self.proto = kw.get('proto', 'UDP')
        self.host = kw.get('host', 'localhost')
        self.port = kw.get('port', None)
        self.fullInfo = kw.get('fullInfo', False)
        if self.proto == 'UDP' and self.port is None:
            self.port = 12202
        if self.proto == 'TCP' and self.port is None:
            self.port = 12201
        self.facility = kw.get('facility', None)
        self.fromHost = kw.get('fromHost', getfqdn())
        logging.Handler.__init__(self)

    def getLevelNo(self, level):
        levelsDict = {
            'WARNING': 4,
            'INFO': 6,
            'DEBUG': 7,
            'ERROR': 3,
            }
        try:
            return(levelsDict[level])
        except:
            raise('Could not determine level number')

    def emit(self, record, **kwargs):
        if self.proto == 'UDP':
            self.sock = socket(AF_INET, SOCK_DGRAM)
        if self.proto == 'TCP':
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.host, int(self.port)))
        recordDict = record.__dict__
        msgDict = {}
        msgDict['version'] = '1.1'
        msgDict['timestamp'] = recordDict['created']
        msgDict['level'] = self.getLevelNo(recordDict['levelname'])
        msgDict['long_message'] = recordDict['msg']
        msgDict['short_message'] = recordDict['msg']
        msgDict['host'] = self.fromHost
        if self.fullInfo is True:
            msgDict['pid'] = recordDict['process']
            msgDict['processName'] = recordDict['processName']
            msgDict['funcName'] = recordDict['funcName']
        if self.facility is not None:
            msgDict['facility'] = self.facility
        elif self.facility is None:
            msgDict['facility'] = recordDict['name']
        extra_props = recordDict.get('gelfProps', None)
        if isinstance(extra_props, dict):
            for k, v in extra_props.iteritems():
                msgDict[k] = v
        if self.proto == 'UDP':
            zpdMsg = compress(dumps(msgDict))
            self.sock.sendto(zpdMsg, (self.host, self.port))
        if self.proto == 'TCP':
            msg = compress(dumps(msgDict)) + '\0'
            try:
                self.sock.sendall(msg)
                self.sock.close()
            except Exception as e:
                raise('Could not send message via TCP: %s' % e)
