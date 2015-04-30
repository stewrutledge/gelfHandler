"""
Simple logging handler for sending gelf messages via TCP or UDP
Author: Stewart Rutledge <stew.rutledge AT gmail.com>
License: BSD I guess
"""
import logging
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, getfqdn
from ssl import *
from json import dumps
from zlib import compress


class handler(logging.Handler):

    def __init__(self, **kw):
        self.proto = kw.get('proto', 'UDP')
        self.host = kw.get('host', 'localhost')
        self.port = kw.get('port', None)
        self.fullInfo = kw.get('fullInfo', False)
        self.facility = kw.get('facility', None)
        self.fromHost = kw.get('fromHost', getfqdn())
        self.tls = kw.get('tls', False)
        if self.proto == 'UDP':
            self.connectUDPSocket()
        if self.proto == 'TCP':
            self.connectTCPSocket()
        logging.Handler.__init__(self)

    def connectUDPSocket(self):
        if self.port is None:
            self.port = 12202
        self.sock = socket(AF_INET, SOCK_DGRAM)

    def connectTCPSocket(self):
        if self.port is None:
            self.port = 12201
        self.sock = socket(AF_INET, SOCK_STREAM)
        if self.tls:
            self.sock = wrap_socket(self.sock, ssl_version=PROTOCOL_TLSv1, cert_reqs=CERT_NONE)
        try:
            self.sock.connect((self.host, int(self.port)))
        except IOError, e:
            raise RuntimeError('Could not connect via TCP: %s' % e)

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

    def buildMessage(self, record, **kwargs):
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
        return msgDict

    def formatMessage(self, msgDict):
        if self.proto == 'UDP':
            msg = compress(dumps(msgDict))
        if self.proto == 'TCP':
            msg = dumps(msgDict) + '\0'
        return msg

    def sendOverTCP(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise IOError("socket connection broken")
            totalsent = totalsent + sent

    def emit(self, record, **kwargs):
        try:
            msgDict = self.buildMessage(record, **kwargs)
            msg = self.formatMessage(msgDict)
        except UnicodeEncodeError, e:
            print "%s in %s" % (e, msgDict)

        if self.proto == 'UDP':
            self.sock.sendto(msg, (self.host, self.port))

        if self.proto == 'TCP':
            try:
                self.sendOverTCP(msg)
            except IOError:
                try:
                    self.sock.close()
                    self.connectTCPSocket()
                    self.sendOverTCP(msg)
                except IOError:
                    raise RuntimeError('Could not connect via TCP: %s' % e)

    def close(self):
        if self.proto == 'TCP':
            self.sock.close()
