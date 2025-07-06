import unittest
import threading
import time
from transport_p2p import send_data_p2p, receive_data_p2p

PORT = 5051
DATA = b'Prueba automatica P2P'
DATA_GRANDE = b'A' * 1024 * 1024  # 1 MB
TIMEOUT = 2

class TestTransportP2P(unittest.TestCase):
    def setUp(self):
        self.result = None
        self.exception = None

    def receptor(self, puerto, timeout=None):
        try:
            self.result = receive_data_p2p(puerto, timeout=timeout)
        except Exception as e:
            self.exception = e

    def test_send_and_receive(self):
        t = threading.Thread(target=self.receptor, args=(PORT, TIMEOUT), daemon=True)
        t.start()
        time.sleep(0.3)
        send_data_p2p('127.0.0.1', PORT, DATA)
        t.join(timeout=TIMEOUT + 1)
        self.assertIsNone(self.exception)
        self.assertEqual(self.result, DATA)

    def test_send_and_receive_grande(self):
        t = threading.Thread(target=self.receptor, args=(PORT + 1, TIMEOUT), daemon=True)
        t.start()
        time.sleep(0.3)
        send_data_p2p('127.0.0.1', PORT + 1, DATA_GRANDE)
        t.join(timeout=TIMEOUT + 2)
        self.assertIsNone(self.exception)
        self.assertEqual(self.result, DATA_GRANDE)

    def test_timeout(self):
        # No enviamos nada, receptor debe hacer timeout
        t = threading.Thread(target=self.receptor, args=(PORT + 2, 1), daemon=True)
        t.start()
        t.join(timeout=2)
        self.assertIsNotNone(self.exception)

if __name__ == '__main__':
    unittest.main()