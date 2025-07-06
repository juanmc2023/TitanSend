"""
Soporte real de Bluetooth clásico (RFCOMM) para TitanSend.
Requiere: pybluez (pip install pybluez)
Advertencia: En Windows, solo funciona con Python <=3.9
"""
import os
import sys
import time

# Detectar compatibilidad de Python y sistema operativo
PYTHON_VERSION = sys.version_info
IS_WINDOWS = os.name == 'nt'
IS_COMPATIBLE = not (IS_WINDOWS and PYTHON_VERSION >= (3, 10))

try:
    import bluetooth  # type: ignore
    BLUETOOTH_AVAILABLE = True
except ImportError:
    bluetooth = None
    BLUETOOTH_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

CHUNK_SIZE = 4096

def check_titansend_file(file_path):
    """
    Verifica que el archivo sea un archivo cifrado válido de TitanSend.
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        if len(data) < 16 + 256 + 32:
            return False, "Archivo demasiado pequeño para ser un archivo cifrado de TitanSend"
        salt = data[:16]
        if all(b == 0 for b in salt):
            return False, "Salt inválido - posible archivo no cifrado"
        return True, "Archivo válido de TitanSend"
    except Exception as e:
        return False, f"Error verificando archivo: {e}"

def check_compatibility():
    """
    Verifica la compatibilidad del sistema para Bluetooth real.
    """
    if not BLUETOOTH_AVAILABLE:
        return False, "pybluez no está instalado. Instala con: pip install pybluez"
    if not IS_COMPATIBLE:
        return False, f"Python {PYTHON_VERSION.major}.{PYTHON_VERSION.minor} no es compatible con pybluez en Windows. Usa Python <=3.9"
    return True, "Sistema compatible"

def recibir_bluetooth_real(ruta_salida, port=3, timeout=60):
    """
    Servidor: recibe archivo cifrado y lo guarda.
    Soporta timeout y barra de progreso si tqdm está disponible.
    """
    compatible, msg = check_compatibility()
    if not compatible:
        print(f"❌ {msg}")
        return False

    try:
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", port))
        server_sock.listen(1)
        server_sock.settimeout(timeout)
        print(f"📡 Esperando conexión Bluetooth en canal RFCOMM {port} (timeout {timeout}s)...")
        print("💡 Asegúrate de que el dispositivo emisor esté emparejado")
        try:
            client_sock, address = server_sock.accept()
        except bluetooth.BluetoothError as e:
            print(f"❌ Timeout esperando conexión: {e}")
            server_sock.close()
            return False
        print(f"✅ Conexión aceptada de {address}")

        with open(ruta_salida, 'wb') as f:
            total_received = 0
            start = time.time()
            pbar = None
            while True:
                data = client_sock.recv(CHUNK_SIZE)
                if not data:
                    break
                f.write(data)
                total_received += len(data)
                if TQDM_AVAILABLE:
                    if pbar is None:
                        pbar = tqdm(total=0, unit='B', unit_scale=True, desc="Recibiendo")
                    pbar.total = max(pbar.total, total_received)
                    pbar.n = total_received
                    pbar.refresh()
                else:
                    print(f"📥 Recibidos {total_received} bytes...")
            if pbar:
                pbar.close()
            elapsed = time.time() - start

        print(f"✅ Archivo recibido y guardado en {ruta_salida} ({total_received} bytes, {elapsed:.2f}s)")

        # Verificar que sea un archivo válido de TitanSend
        is_valid, msg = check_titansend_file(ruta_salida)
        if is_valid:
            print("🔒 Archivo verificado como archivo cifrado válido de TitanSend")
        else:
            print(f"⚠️  Advertencia: {msg}")

        client_sock.close()
        server_sock.close()
        return True

    except bluetooth.BluetoothError as e:
        print(f"❌ Error de Bluetooth: {e}")
        print("💡 Verifica que Bluetooth esté habilitado y el dispositivo emparejado")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def enviar_bluetooth_real(ruta_archivo, direccion_destino, port=3, retries=3, timeout=60):
    """
    Cliente: envía archivo cifrado a un dispositivo Bluetooth.
    Soporta reintentos, barra de progreso y timeout.
    """
    compatible, msg = check_compatibility()
    if not compatible:
        print(f"❌ {msg}")
        return False

    if not os.path.isfile(ruta_archivo):
        print(f"❌ Archivo '{ruta_archivo}' no encontrado")
        return False

    is_valid, msg = check_titansend_file(ruta_archivo)
    if not is_valid:
        print(f"❌ {msg}")
        print("💡 Solo puedes enviar archivos cifrados generados por TitanSend")
        return False

    file_size = os.path.getsize(ruta_archivo)
    attempt = 0
    while attempt < retries:
        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.settimeout(timeout)
            print(f"🔗 Conectando a {direccion_destino} en canal RFCOMM {port} (intento {attempt+1}/{retries})...")
            sock.connect((direccion_destino, port))
            print("✅ Conexión establecida")

            print(f"📤 Enviando archivo de {file_size} bytes...")
            with open(ruta_archivo, 'rb') as f:
                total_sent = 0
                start = time.time()
                pbar = tqdm(total=file_size, unit='B', unit_scale=True, desc="Enviando") if TQDM_AVAILABLE else None
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    sock.send(chunk)
                    total_sent += len(chunk)
                    if pbar:
                        pbar.update(len(chunk))
                    else:
                        print(f"📤 Enviados {total_sent}/{file_size} bytes...")
                if pbar:
                    pbar.close()
                elapsed = time.time() - start

            print(f"✅ Archivo '{ruta_archivo}' enviado correctamente a {direccion_destino} ({elapsed:.2f}s)")
            sock.close()
            return True

        except bluetooth.BluetoothError as e:
            print(f"❌ Error de Bluetooth: {e}")
            print("💡 Verifica que el dispositivo esté encendido, emparejado y en modo visible")
            attempt += 1
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            attempt += 1
            time.sleep(2)
    print("❌ No se pudo enviar el archivo tras varios intentos.")
    return False

def buscar_dispositivos(timeout=10):
    """
    Busca dispositivos Bluetooth cercanos.
    """
    compatible, msg = check_compatibility()
    if not compatible:
        print(f"❌ {msg}")
        return []

    try:
        print("🔍 Buscando dispositivos Bluetooth cercanos...")
        print(f"⏳ Esto puede tomar hasta {timeout} segundos...")
        dispositivos = bluetooth.discover_devices(duration=timeout, lookup_names=True)

        if not dispositivos:
            print("❌ No se encontraron dispositivos Bluetooth")
            print("💡 Verifica que Bluetooth esté habilitado y hay dispositivos cercanos")
            return []

        print(f"✅ Encontrados {len(dispositivos)} dispositivos:")
        for i, (addr, name) in enumerate(dispositivos, 1):
            print(f"  {i}. {addr} - {name}")

        return dispositivos

    except bluetooth.BluetoothError as e:
        print(f"❌ Error buscando dispositivos: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return []

def log_transfer(event, info):
    """
    Guarda un log simple de transferencias (opcional, solo si se desea).
    """
    try:
        with open("bluetooth_transfer.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [{event}] {info}\n")
    except Exception:
        pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bluetooth real para TitanSend (pybluez)")
    subparsers = parser.add_subparsers(dest='cmd')

    srv = subparsers.add_parser('server', help='Esperar y recibir archivo')
    srv.add_argument('--output', required=True, help='Ruta de salida para guardar el archivo recibido')
    srv.add_argument('--port', type=int, default=3, help='Canal RFCOMM (default 3)')
    srv.add_argument('--timeout', type=int, default=60, help='Timeout en segundos para esperar conexión')

    cli = subparsers.add_parser('client', help='Enviar archivo a un dispositivo')
    cli.add_argument('--file', required=True, help='Archivo a enviar')
    cli.add_argument('--address', required=True, help='Dirección MAC del receptor')
    cli.add_argument('--port', type=int, default=3, help='Canal RFCOMM (default 3)')
    cli.add_argument('--retries', type=int, default=3, help='Reintentos de conexión')
    cli.add_argument('--timeout', type=int, default=60, help='Timeout en segundos para conectar y enviar')

    scan = subparsers.add_parser('scan', help='Buscar dispositivos Bluetooth cercanos')
    scan.add_argument('--timeout', type=int, default=10, help='Tiempo de búsqueda en segundos')

    args = parser.parse_args()
    if args.cmd == 'server':
        ok = recibir_bluetooth_real(args.output, args.port, args.timeout)
        log_transfer("RECEIVE", f"output={args.output} port={args.port} ok={ok}")
    elif args.cmd == 'client':
        ok = enviar_bluetooth_real(args.file, args.address, args.port, args.retries, args.timeout)
        log_transfer("SEND", f"file={args.file} address={args.address} port={args.port} ok={ok}")
    elif args.cmd == 'scan':
        buscar_dispositivos(args.timeout)
        log_transfer("SCAN", f"timeout={args.timeout}")
    else:
        parser.print_help()