import logging
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, getfqdn
import ssl
from json import dumps
from zlib import compress


class GelfHandler(logging.Handler):
    """
    Simple logging handler for sending gelf messages via TCP or UDP
    Author: Stewart Rutledge <stew.rutledge AT gmail.com>
    License: BSD
    """
    def __init__(self, protocol='UDP', host='localhost', port=None, **kw):
        """
        Simple
        :param protocol: Which protocol to use (TCP or UDP) [Default: UDP]
        :param host: Host to send logs to [Default: localhost]
        :param port: Port [Default: 12201 UDP/12202 TCP
        :param full_info: Include function name, pid and process [Default: False]
        :param facility: Logging facility [Default: None]
        :param from_host: Host name in the log message [Default: FQDN]
        :param tls: Use a tls connection [Default: False]
        :type protocol str
        :type host: str
        :type port: int
        :type full_info: bool
        :type facility: str
        :type from_host: str
        :type tl: bool
        """
        if not protocol.lower() in ['tcp', 'udp']:
            raise ValueError('Protocol must be either TCP or UDP')
        self.protocol = protocol
        self.host = host
        self.port = port
        self.full_info = kw.get('full_info', False)
        self.facility = kw.get('facility', None)
        self.from_host = kw.get('from_host', getfqdn())
        self.tls = kw.get('tls', False)
        self.application = kw.get('application', None)
        if self.protocol.lower() == 'udp':
            self._connect_udp_socket()
        if self.protocol.lower() == 'tcp':
            self._connect_tcp_socket()
        logging.Handler.__init__(self)

    def _connect_udp_socket(self):
        if self.port is None:
            self.port = 12202
        self.sock = socket(AF_INET, SOCK_DGRAM)

    def _connect_tcp_socket(self):
        if self.port is None:
            self.port = 12201
        self.sock = socket(AF_INET, SOCK_STREAM)
        if self.tls:
            self.sock = ssl.wrap_socket(self.sock, ssl_version=ssl.PROTOCOL_TLSv1, cert_reqs=ssl.CERT_NONE)
        try:
            self.sock.connect((self.host, int(self.port)))
        except IOError as e:
            raise RuntimeError('Could not connect via TCP: %s' % e)

    def getLevelNo(self, level):
        levelsDict = {
            'WARNING': 4,
            'INFO': 6,
            'DEBUG': 7,
            'ERROR': 3,
            'CRITICAL': 9
        }
        try:
            return(levelsDict[level])
        except:
            raise('Could not determine level number')

    def _build_message(self, record, **kwargs):
        record_dict = record.__dict__
        msg_dict = {}
        msg_dict['version'] = '1.1'
        msg_dict['timestamp'] = record_dict['created']
        msg_dict['level'] = self.getLevelNo(record_dict['levelname'])
        msg_dict['long_message'] = record_dict['msg']
        msg_dict['short_message'] = record_dict['msg']
        msg_dict['host'] = self.from_host
        if self.application:
            msgDict['application'] = recordDict['application']
        if self.full_info is True:
            msg_dict['pid'] = record_dict['process']
            msg_dict['processName'] = record_dict['processName']
            msg_dict['funcName'] = record_dict['funcName']
        if self.facility is not None:
            msg_dict['facility'] = self.facility
        elif self.facility is None:
            msg_dict['facility'] = record_dict['name']
        extra_props = record_dict.get('gelf_props', None)
        if isinstance(extra_props, dict):
            for k, v in extra_props.items():
                msg_dict[k] = v
        return msg_dict

    def formatMessage(self, msgDict):
        if self.proto == 'UDP':
            msg = compress(dumps(msgDict))
        if self.proto == 'TCP':
            msg = dumps(msgDict) + '\0'
        return msg

    def _emit_tcp(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:].encode())
            if sent == 0:
                raise IOError("socket connection broken")
            totalsent = totalsent + sent

    def _emit_udp(self, compressed_msg):
        self.sock.sendto(compressed_msg, (self.host, self.port))

    def emit(self, record, **kwargs):
        msg_dict = self._build_message(record, **kwargs)
        if self.protocol.lower() == 'udp':
            compressed_msg = compress(dumps(msg_dict).encode())
            self._emit_udp(compressed_msg=compressed_msg)
        if self.protocol.lower() == 'tcp':
            msg = dumps(msg_dict) + '\0'
            try:
                self._emit_tcp(msg)
            except IOError:
                try:
                    self.sock.close()
                    self._connect_tcp_socket()
                    self._emit_tcp(msg)
                except IOError as e:
                    raise RuntimeError('Could not connect via TCP: %s' % e)

    def close(self):
        if self.protocol == 'TCP':
            self.sock.close()
