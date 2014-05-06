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

    def emit(self, record):
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
        if self.facility is not None:
            msgDict['facility'] = self.facility
        elif self.facility is None:
            msgDict['facility'] = recordDict['name']
        if isinstance(recordDict['args'], dict):
            for k, v in recordDict['args'].iteritems():
                msgDict[k] = v
        if self.proto == 'UDP':
            zpdMsg = compress(dumps(msgDict))
            self.sock.sendto(zpdMsg, (self.host, self.port))
        if self.proto == 'TCP':
            msg = dumps(msgDict) + '\0'
            self.sock.sendall(msg)
            self.sock.close()
