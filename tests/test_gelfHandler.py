import unittest
try:
    from unittest import mock
except ImportError:
    import mock
from gelfHandler import GelfHandler
import logging
import json
from uuid import uuid4

class GelfHandlerTests(unittest.TestCase):

    @mock.patch('gelfHandler.gelf.GelfHandler.close', side_effect=ValueError)
    @mock.patch('gelfHandler.gelf.GelfHandler._connect_tcp_socket')
    def test_facility_is_set(self, *args):
        logger = logging.getLogger(uuid4().hex)
        gelfHandler = GelfHandler(host='localhost', protocol='TCP', facility='UnitTest')
        gelfHandler.close = mock.MagicMock(None)
        logger.addHandler(gelfHandler)
        with mock.patch('gelfHandler.gelf.GelfHandler._emit_tcp') as mocked:
            logger.warning('Test Message')
            self.assertEqual(json.loads(mocked.call_args[0][0][:-1])['facility'], 'UnitTest')

    @mock.patch('gelfHandler.gelf.GelfHandler.close', side_effect=ValueError)
    @mock.patch('gelfHandler.gelf.GelfHandler._connect_tcp_socket')
    def test_facility_should_be_logger_name_when_not_set(self, *args):
        logger_name = uuid4().hex
        logger = logging.getLogger(logger_name)
        gelfHandler = GelfHandler(host='localhost', protocol='TCP')
        gelfHandler.close = mock.MagicMock(None)
        logger.addHandler(gelfHandler)
        with mock.patch('gelfHandler.gelf.GelfHandler._emit_tcp') as mocked:
            logger.warning('Test Message')
            self.assertEqual(json.loads(mocked.call_args[0][0][:-1])['facility'], logger_name)

    @mock.patch('gelfHandler.gelf.GelfHandler.close', side_effect=ValueError)
    @mock.patch('gelfHandler.gelf.GelfHandler._connect_tcp_socket')
    def test_extra_props_should_be_set_when_provided(self, *args):
        logger_name = uuid4().hex
        logger = logging.getLogger(logger_name)
        gelfHandler = GelfHandler(host='localhost', protocol='TCP')
        gelfHandler.close = mock.MagicMock(None)
        logger.addHandler(gelfHandler)
        with mock.patch('gelfHandler.gelf.GelfHandler._emit_tcp') as mocked:
            logger.warning('Test Message', extra={'gelf_props': {'my_test': 'testing'}})
            self.assertEqual(json.loads(mocked.call_args[0][0][:-1])['my_test'], 'testing')


    @mock.patch('gelfHandler.gelf.GelfHandler.close', side_effect=ValueError)
    @mock.patch('gelfHandler.gelf.GelfHandler._connect_tcp_socket')
    def test_should_add_full_info_when_set_true(self, *args):
        logger = logging.getLogger(uuid4().hex)
        gelfHandler = GelfHandler(host='localhost', protocol='TCP', full_info=True, facility='UnitTest')
        gelfHandler.close = mock.MagicMock(None)
        logger.addHandler(gelfHandler)
        with mock.patch('gelfHandler.gelf.GelfHandler._emit_tcp') as mocked:
            logger.warning('Test Message')
            self.assertIsNotNone(json.loads(mocked.call_args[0][0][:-1]).get('pid'))
            self.assertIsNotNone(json.loads(mocked.call_args[0][0][:-1]).get('processName'))
            self.assertIsNotNone(json.loads(mocked.call_args[0][0][:-1]).get('funcName'))


    @mock.patch('gelfHandler.gelf.GelfHandler.close', side_effect=ValueError)
    @mock.patch('gelfHandler.gelf.GelfHandler._connect_tcp_socket')
    def test_tcp_is_sent_with_zero_byte(self, *args):
        logger = logging.getLogger(uuid4().hex)
        gelfHandler = GelfHandler(host='localhost', protocol='TCP', facility='UnitTest')
        gelfHandler.close = mock.MagicMock(None)
        logger.addHandler(gelfHandler)
        with mock.patch('gelfHandler.gelf.GelfHandler._emit_tcp') as mocked:
            logger.warning('Test Message')
            self.assertEqual(mocked.call_args[0][0][-1:], '\0')

    @mock.patch('gelfHandler.gelf.GelfHandler.close', side_effect=ValueError)
    def test_should_raise_value_error_when_not_tcp_or_udp(self, *args):
        logger = logging.getLogger(uuid4().hex)
        with self.assertRaises(ValueError):
            gelfHandler = GelfHandler(host='localhost', protocol='WRONG', facility='UnitTest')

    @mock.patch('gelfHandler.gelf.GelfHandler.close', side_effect=ValueError)
    def test_udp_is_sent_as_bytes(self, *args):
        logger = logging.getLogger(uuid4().hex)
        gelfHandler = GelfHandler(host='localhost', protocol='udp', facility='UDPTest')
        gelfHandler.close = mock.MagicMock(None)
        logger.addHandler(gelfHandler)
        with mock.patch('gelfHandler.gelf.GelfHandler._emit_udp') as mocked:
            logger.warning('Test Message')
            self.assertIsInstance(mocked.call_args[1]['compressed_msg'], bytes)