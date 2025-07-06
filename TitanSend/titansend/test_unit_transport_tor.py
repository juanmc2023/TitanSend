import unittest
import threading
import time
from flask import Flask, request
from transport_tor import send_data_tor, receive_data_tor

PORT = 5050
URL_POST = f'http://127.0.0.1:{PORT}/upload'
URL_GET = f'http://127.0.0.1:{PORT}/download'
ARCHIVO = 'test_tor.bin'

# Servidor Flask de prueba
app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    with open(ARCHIVO, 'wb') as f:
        f.write(request.data)
    return 'OK', 200

@app.route('/download', methods=['GET'])
def download():
    with open(ARCHIVO, 'rb') as f:
        return f.read(), 200

def run_flask():
    app.run(port=PORT)

class TestTransportTor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.flask_thread = threading.Thread(target=run_flask, daemon=True)
        cls.flask_thread.start()
        time.sleep(1)  # Esperar a que el servidor arranque

    def test_send_and_receive(self):
        data = b'Prueba automatica Tor'
        resp = send_data_tor(URL_POST, data)
        self.assertIn(b'OK', resp)
        recibido = receive_data_tor(URL_GET)
        self.assertEqual(data, recibido)

if __name__ == '__main__':
    unittest.main() 