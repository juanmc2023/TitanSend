import qrcode
import os

# Importar pyudev de forma opcional
try:
    import pyudev # type: ignore
    PYUDEV_AVAILABLE = True
except ImportError:
    PYUDEV_AVAILABLE = False

# Bluetooth (interfaz simulada)
def enviar_bluetooth(datos: bytes, direccion: str):
    """
    Simula el envío de datos por Bluetooth.
    """
    print(f"[Bluetooth] Enviando datos a {direccion} (simulado)")

def recibir_bluetooth(direccion: str) -> bytes:
    """
    Simula la recepción de datos por Bluetooth.
    """
    print(f"[Bluetooth] Recibiendo datos de {direccion} (simulado)")
    return b""

# QR
def generar_qr(datos: bytes, ruta: str):
    """
    Genera un código QR a partir de los datos y lo guarda en la ruta indicada.
    """
    try:
        img = qrcode.make(datos)
        img.save(ruta)
        print(f"[QR] Código QR guardado en {ruta}")
    except Exception as e:
        print(f"[QR] Error generando QR: {e}")

def leer_qr(ruta: str) -> bytes:
    """
    Lee los datos de un archivo QR (binario).
    """
    try:
        with open(ruta, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"[QR] Error leyendo QR: {e}")
        return b""

# USB
def enviar_usb(datos: bytes, ruta_usb: str):
    """
    Guarda los datos en la ruta indicada (simula transferencia por USB).
    """
    try:
        with open(ruta_usb, 'wb') as f:
            f.write(datos)
        print(f"[USB] Datos guardados en {ruta_usb}")
    except Exception as e:
        print(f"[USB] Error guardando datos en USB: {e}")

def recibir_usb(ruta_usb: str) -> bytes:
    """
    Lee los datos de la ruta indicada (simula recepción por USB).
    """
    try:
        with open(ruta_usb, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"[USB] Error leyendo datos de USB: {e}")
        return b""

def detectar_usb(callback):
    if not PYUDEV_AVAILABLE:
        print("pyudev no disponible. La detección automática de USB no funcionará.")
        return
    
    try:
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by('block')
        for device in iter(monitor.poll, None):
            if device.action == 'add' and device.get('ID_BUS') == 'usb':
                mount_point = buscar_punto_montaje(device)
                if mount_point:
                    callback(mount_point)
    except Exception as e:
        print(f"Error detectando USB: {e}")

def buscar_punto_montaje(device):
    # Implementa lógica para buscar el punto de montaje del dispositivo
    # Ejemplo: leer /proc/mounts o usar psutil.disk_partitions()
    return "/media/usuario/pendrive"

def copiar_a_usb(origen, destino_usb):
    import shutil
    shutil.copy(origen, destino_usb)

# Variables de compatibilidad
BLUETOOTH_AVAILABLE = False
IS_COMPATIBLE = False

try:
    import pybluez
    BLUETOOTH_AVAILABLE = True
    IS_COMPATIBLE = True
except ImportError:
    pass

if not BLUETOOTH_AVAILABLE:
    print("Bluetooth no disponible. Instala pybluez o revisa compatibilidad de tu sistema.")
elif not IS_COMPATIBLE:
    print("Bluetooth solo soportado en Windows con Python <= 3.9. Usa Linux o baja la versión de Python.")