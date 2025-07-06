"""
Transporte P2P y Onion (Tor) para TitanSend
Mantiene cifrado extremo a extremo, solo usa la red como canal
"""
import os
import socket
import threading
import time
import json
from colorama import Fore, Style

# Intentar importar Tor (opcional)
try:
    from stem import Signal
    from stem.control import Controller
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False

# Intentar importar socks para conexiones Tor
try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False

DEFAULT_PORT = 8080
CHUNK_SIZE = 4096

class P2PServer:
    """Servidor P2P para recibir archivos cifrados"""
    
    def __init__(self, port=DEFAULT_PORT, use_tor=False):
        self.port = port
        self.use_tor = use_tor and TOR_AVAILABLE
        self.server_socket = None
        self.running = False
        
    def start(self, output_file):
        """Inicia el servidor P2P"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('', self.port))
            self.server_socket.listen(1)
            self.running = True
            
            if self.use_tor:
                print(f"🌐 Servidor P2P iniciado en puerto {self.port} (con Tor)")
                print("🔗 Dirección Onion disponible (si Tor está configurado)")
            else:
                print(f"🌐 Servidor P2P iniciado en puerto {self.port}")
                print(f"📡 Esperando conexiones en 0.0.0.0:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"✅ Conexión aceptada de {address}")
                    
                    # Recibir archivo cifrado
                    with open(output_file, 'wb') as f:
                        total_received = 0
                        while True:
                            data = client_socket.recv(CHUNK_SIZE)
                            if not data:
                                break
                            f.write(data)
                            total_received += len(data)
                            print(f"📥 Recibidos {total_received} bytes...")
                    
                    print(f"✅ Archivo recibido y guardado en {output_file}")
                    print(f"📊 Tamaño total: {total_received} bytes")
                    client_socket.close()
                    break
                    
                except Exception as e:
                    print(f"❌ Error en conexión: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Error iniciando servidor P2P: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Detiene el servidor"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

class P2PClient:
    """Cliente P2P para enviar archivos cifrados"""
    
    def __init__(self, use_tor=False):
        self.use_tor = use_tor and SOCKS_AVAILABLE
        
    def send_file(self, file_path, target_host, target_port=DEFAULT_PORT):
        """Envía archivo cifrado por P2P"""
        if not os.path.isfile(file_path):
            print(f"❌ Archivo '{file_path}' no encontrado")
            return False
            
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            if self.use_tor:
                # Configurar proxy SOCKS para Tor
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
                print(f"🌐 Conectando a {target_host}:{target_port} a través de Tor...")
            else:
                print(f"🌐 Conectando a {target_host}:{target_port}...")
            
            sock.connect((target_host, target_port))
            print("✅ Conexión establecida")
            
            file_size = os.path.getsize(file_path)
            print(f"📤 Enviando archivo de {file_size} bytes...")
            
            with open(file_path, 'rb') as f:
                total_sent = 0
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    sock.send(chunk)
                    total_sent += len(chunk)
                    print(f"📤 Enviados {total_sent}/{file_size} bytes...")
            
            print(f"✅ Archivo enviado correctamente a {target_host}:{target_port}")
            sock.close()
            return True
            
        except Exception as e:
            print(f"❌ Error enviando archivo: {e}")
            return False

def obtener_direccion_onion():
    """Obtiene la dirección Onion actual (si Tor está disponible)"""
    if not TOR_AVAILABLE:
        return None
    
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            return controller.get_info("onion")
    except Exception as e:
        print(f"⚠️  No se pudo obtener dirección Onion: {e}")
        return None

def generar_direccion_onion(port=DEFAULT_PORT):
    """Genera una nueva dirección Onion (requiere Tor configurado)"""
    if not TOR_AVAILABLE:
        print("❌ Tor no está disponible. Instala: pip install stem")
        return None
    
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            
            # Crear servicio Onion
            service = controller.create_onion_service(
                ports=[(port, port)],
                detached=True
            )
            
            print(f"🌐 Nueva dirección Onion generada: {service.service_id}.onion")
            return service.service_id
    except Exception as e:
        print(f"❌ Error generando dirección Onion: {e}")
        return None

def verificar_tor():
    """Verifica si Tor está disponible y funcionando"""
    if not TOR_AVAILABLE:
        return False, "Tor no está disponible. Instala: pip install stem"
    
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            version = controller.get_version()
            return True, f"Tor disponible: {version}"
    except Exception as e:
        return False, f"Tor no está funcionando: {e}"

def verificar_socks():
    """Verifica si SOCKS está disponible para conexiones Tor"""
    if not SOCKS_AVAILABLE:
        return False, "SOCKS no está disponible. Instala: pip install PySocks"
    return True, "SOCKS disponible"

def send_data_p2p(ip, port, data):
    """
    Envía datos a un peer usando sockets TCP.
    """
    s = socket.socket()
    s.connect((ip, port))
    s.sendall(data)
    s.close()

def receive_data_p2p(port, buffer_size=4096):
    """
    Recibe datos de un peer escuchando en un puerto TCP.
    Devuelve los datos recibidos.
    """
    s = socket.socket()
    s.bind(("0.0.0.0", port))
    s.listen(1)
    conn, addr = s.accept()
    data = b""
    while True:
        chunk = conn.recv(buffer_size)
        if not chunk:
            break
        data += chunk
    conn.close()
    s.close()
    return data

if __name__ == "__main__":
    from titansend.cli import main
    main() 