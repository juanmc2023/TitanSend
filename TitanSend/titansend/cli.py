import os
import json
import argparse
import time
import getpass
from . import crypto, shamir, transport
from cryptography.hazmat.primitives import serialization
from colorama import Fore, Style

# Importar Bluetooth real
try:
    from . import transport_bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False

# Importar QR optimizado
try:
    from . import transport_qr
    QR_OPTIMIZED_AVAILABLE = True
except ImportError:
    QR_OPTIMIZED_AVAILABLE = False

# Importar P2P y Onion
try:
    from . import transport_p2p
    P2P_AVAILABLE = True
except ImportError:
    P2P_AVAILABLE = False

# Importar Tor
try:
    from . import transport_tor
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False

VERSION = '1.0.0'

# Mensaje de bienvenida
WELCOME = f"""
{Fore.CYAN}TitanSend v{VERSION} - Tu Búnker Digital Portátil{Style.RESET_ALL}
Proyecto: https://github.com/tu-repo/titansend
"""

def confirmar_sobrescritura(path):
    if os.path.exists(path):
        resp = input(Fore.YELLOW + f"⚠️  El archivo '{path}' ya existe. ¿Deseas sobrescribirlo? (s/N): " + Style.RESET_ALL).strip().lower()
        if resp != 's':
            print(Fore.RED + "Operación cancelada por el usuario." + Style.RESET_ALL)
            return False
    return True

def serialize_public_key_from_file(path):
    with open(path, 'rb') as f:
        pub = crypto.deserializar_clave_publica(f.read())
    return pub

def lock(args):
    try:
        file_path = args.file_path
        pubkey_path = args.public_key
        password = args.password or getpass.getpass("Contraseña para generar la clave AES: ")
        out_path = args.output
        if not os.path.isfile(file_path):
            print(Fore.RED + f"❌ Archivo '{file_path}' no encontrado. Verifica la ruta, el nombre y que estés en la carpeta correcta." + Style.RESET_ALL)
            print(Fore.YELLOW + "¿Olvidaste crear el archivo? Usa: echo hola > archivo.txt" + Style.RESET_ALL)
            return
        if not os.path.isfile(pubkey_path):
            print(Fore.RED + f"❌ Clave pública '{pubkey_path}' no encontrada. Verifica la ruta." + Style.RESET_ALL)
            print(Fore.YELLOW + "¿Olvidaste generar la clave pública? Usa: openssl genrsa -out privada.pem 2048 && openssl rsa -in privada.pem -pubout -out publica.pem" + Style.RESET_ALL)
            return
        if not confirmar_sobrescritura(out_path):
            return
        with open(file_path, 'rb') as f:
            file_data = f.read()
        pubkey = serialize_public_key_from_file(pubkey_path)
        salt = os.urandom(16)
        aes_key = crypto.generar_clave_aes(password, salt)
        timestamp = int(time.time()).to_bytes(8, 'big')
        nonce = os.urandom(8)
        metadata = json.dumps({"filename": os.path.basename(file_path), "size": len(file_data)}).encode()
        metadata_length = len(metadata).to_bytes(4, 'big')
        data_to_encrypt = timestamp + nonce + metadata_length + metadata + file_data
        cifrado = crypto.cifrar_aes(data_to_encrypt, aes_key)
        firma = crypto.firmar_hmac(aes_key, cifrado)
        aes_key_cifrada = crypto.cifrar_con_publica(pubkey, aes_key)
        resultado = salt + aes_key_cifrada + firma + cifrado
        with open(out_path, 'wb') as f:
            f.write(resultado)
        print(Fore.GREEN + f"Archivo cifrado y guardado en {out_path}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ Error inesperado: {e}" + Style.RESET_ALL)
        print(Fore.YELLOW + "Si el problema persiste, reporta el error en https://github.com/tu-repo/titansend/issues" + Style.RESET_ALL)

def unlock(args):
    try:
        file_path = args.file_path
        privkey_path = args.key
        password = args.password or getpass.getpass("Contraseña para la clave AES: ")
        out_path = args.output
        if not os.path.isfile(file_path):
            print(Fore.RED + f"❌ Archivo cifrado '{file_path}' no encontrado. Verifica la ruta, el nombre y que estés en la carpeta correcta." + Style.RESET_ALL)
            return
        if not os.path.isfile(privkey_path):
            print(Fore.RED + f"❌ Clave privada '{privkey_path}' no encontrada. Verifica la ruta." + Style.RESET_ALL)
            print(Fore.YELLOW + "¿Olvidaste generar la clave privada? Usa: openssl genrsa -out privada.pem 2048" + Style.RESET_ALL)
            return
        with open(file_path, 'rb') as f:
            datos = f.read()
        with open(privkey_path, 'rb') as f:
            privkey = serialization.load_pem_private_key(f.read(), password=None)
        salt = datos[:16]
        aes_key_cifrada = datos[16:16+256]
        firma = datos[16+256:16+256+32]
        cifrado = datos[16+256+32:]
        aes_key = crypto.descifrar_con_privada(privkey, aes_key_cifrada)
        if not crypto.verificar_hmac(aes_key, cifrado, firma):
            print(Fore.RED + "Firma HMAC inválida. El archivo puede haber sido manipulado." + Style.RESET_ALL)
            return
        descifrado = crypto.descifrar_aes(cifrado, aes_key)
        timestamp = int.from_bytes(descifrado[:8], 'big')
        nonce = descifrado[8:16]
        metadata_length = int.from_bytes(descifrado[16:20], 'big')
        metadata = descifrado[20:20+metadata_length]
        file_data = descifrado[20+metadata_length:]
        meta = json.loads(metadata.decode())
        out_file = out_path or meta['filename']
        if out_path and not confirmar_sobrescritura(out_file):
            return
        with open(out_file, 'wb') as f:
            f.write(file_data)
        print(Fore.GREEN + f"Archivo descifrado y guardado como {out_file}" + Style.RESET_ALL)
        print(Fore.BLUE + f"Metadatos: {meta}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ Error inesperado: {e}" + Style.RESET_ALL)
        print(Fore.YELLOW + "Si el problema persiste, reporta el error en https://github.com/tu-repo/titansend/issues" + Style.RESET_ALL)

def split(args):
    try:
        privkey_path = args.private_key_path
        shares = args.shares
        threshold = args.threshold
        if not os.path.isfile(privkey_path):
            print(Fore.RED + f"❌ Clave privada '{privkey_path}' no encontrada. Verifica la ruta." + Style.RESET_ALL)
            print(Fore.YELLOW + "¿Olvidaste generar la clave privada? Usa: openssl genrsa -out privada.pem 2048" + Style.RESET_ALL)
            return
        with open(privkey_path, 'r', encoding='utf-8', errors='ignore') as f:
            privkey = f.read()
        partes = shamir.fragmentar_clave(privkey, shares, threshold)
        for i, parte in enumerate(partes):
            fname = f'share_{i+1}.txt'
            with open(fname, 'w') as f:
                f.write(parte)
            print(Fore.GREEN + f"Fragmento guardado: {fname}" + Style.RESET_ALL)
        print(Fore.BLUE + f"Clave fragmentada en {shares} partes (umbral: {threshold})" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ Error inesperado: {e}" + Style.RESET_ALL)
        print(Fore.YELLOW + "Si el problema persiste, reporta el error en https://github.com/tu-repo/titansend/issues" + Style.RESET_ALL)

def reconstruct(args):
    try:
        share_paths = args.shares
        partes = []
        for path in share_paths:
            if not os.path.isfile(path):
                print(Fore.RED + f"❌ Fragmento '{path}' no encontrado. Verifica la ruta." + Style.RESET_ALL)
                return
            with open(path, 'r') as f:
                partes.append(f.read().strip())
        clave = shamir.reconstruir_clave(partes)
        with open('reconstructed_key.pem', 'w') as f:
            f.write(clave)
        print(Fore.GREEN + "Clave reconstruida y guardada como 'reconstructed_key.pem'" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ Error inesperado: {e}" + Style.RESET_ALL)
        print(Fore.YELLOW + "Si el problema persiste, reporta el error en https://github.com/tu-repo/titansend/issues" + Style.RESET_ALL)

def send(args):
    try:
        file_path = args.file_path
        method = args.method
        if not os.path.isfile(file_path):
            print(Fore.RED + f"❌ Archivo '{file_path}' no encontrado. Verifica la ruta." + Style.RESET_ALL)
            return
        with open(file_path, 'rb') as f:
            datos = f.read()
        if method == 'usb':
            out_path = args.output or input("Ruta de salida en USB: ").strip()
            if not confirmar_sobrescritura(out_path):
                return
            with open(out_path, 'wb') as f:
                f.write(datos)
            print(Fore.GREEN + f"Archivo guardado en {out_path}" + Style.RESET_ALL)
        elif method == 'qr':
            if QR_OPTIMIZED_AVAILABLE:
                print(Fore.YELLOW + "Usando QR optimizado con compresión y fragmentación automática..." + Style.RESET_ALL)
                qr_path = args.output or input("Ruta base para los códigos QR: ").strip()
                if os.path.exists(qr_path):
                    print(Fore.YELLOW + f"⚠️  El archivo base '{qr_path}' ya existe. Se generarán archivos adicionales." + Style.RESET_ALL)
                archivos_generados = transport_qr.generar_qr_multiple(datos, qr_path)
                if len(archivos_generados) == 1:
                    print(Fore.GREEN + f"✅ QR único generado: {archivos_generados[0]}" + Style.RESET_ALL)
                else:
                    print(Fore.GREEN + f"✅ {len(archivos_generados)} códigos QR generados para archivo grande" + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + "QR optimizado no disponible. Usando QR simple..." + Style.RESET_ALL)
                qr_path = args.output or input("Ruta para guardar el código QR: ").strip()
                transport.generar_qr(datos, qr_path)
        elif method == 'bluetooth':
            if not BLUETOOTH_AVAILABLE:
                print(Fore.RED + "Bluetooth real no disponible. Usando simulación." + Style.RESET_ALL)
                address = args.address or input("Dirección Bluetooth del receptor: ").strip()
                transport.enviar_bluetooth(datos, address)
            else:
                print(Fore.YELLOW + "Usando Bluetooth real (RFCOMM)..." + Style.RESET_ALL)
                address = args.address or input("Dirección MAC del receptor (ej: 00:11:22:33:44:55): ").strip()
                port = args.port or 3
                transport_bluetooth.enviar_bluetooth_real(file_path, address, port)
        elif method == 'p2p':
            if not P2P_AVAILABLE:
                print(Fore.RED + "Transporte P2P no disponible." + Style.RESET_ALL)
                return
            host = args.host or input("Host del receptor: ").strip()
            port = args.port or 8080
            use_tor = args.tor
            client = transport_p2p.P2PClient(use_tor)
            if client.send_file(file_path, host, port):
                print(Fore.GREEN + f"✅ Archivo enviado por P2P a {host}:{port}" + Style.RESET_ALL)
            else:
                print(Fore.RED + "❌ Error enviando archivo por P2P" + Style.RESET_ALL)
        elif method == 'onion':
            if not P2P_AVAILABLE:
                print(Fore.RED + "Transporte Onion no disponible." + Style.RESET_ALL)
                return
            onion_address = args.onion or input("Dirección Onion del receptor (.onion): ").strip()
            port = args.port or 8080
            client = transport_p2p.P2PClient(use_tor=True)
            if client.send_file(file_path, onion_address, port):
                print(Fore.GREEN + f"✅ Archivo enviado por Onion a {onion_address}:{port}" + Style.RESET_ALL)
            else:
                print(Fore.RED + "❌ Error enviando archivo por Onion" + Style.RESET_ALL)
        elif method == 'tor':
            if not TOR_AVAILABLE:
                print(Fore.RED + "Transporte Tor no disponible." + Style.RESET_ALL)
                return
            url = args.url or input("URL del endpoint Tor (ej: http://127.0.0.1:5000/upload): ").strip()
            if not url.startswith('http'):
                print(Fore.RED + "❌ La URL debe comenzar con http o https." + Style.RESET_ALL)
                return
            respuesta = transport_tor.send_data_tor(url, datos)
            print(Fore.GREEN + f"Archivo enviado por Tor. Respuesta: {respuesta}" + Style.RESET_ALL)
        else:
            print(Fore.RED + "Método de envío no soportado." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ Error inesperado: {e}" + Style.RESET_ALL)
        print(Fore.YELLOW + "Si el problema persiste, reporta el error en https://github.com/tu-repo/titansend/issues" + Style.RESET_ALL)

def receive(args):
    try:
        method = args.method
        out_path = args.output or input("Ruta de salida para guardar el archivo recibido: ").strip()
        if out_path and os.path.exists(out_path):
            if not confirmar_sobrescritura(out_path):
                return
        if method == 'usb':
            usb_path = args.input or input("Ruta del archivo en USB: ").strip()
            with open(usb_path, 'rb') as f:
                datos = f.read()
            with open(out_path, 'wb') as f:
                f.write(datos)
            print(Fore.GREEN + f"Archivo recibido y guardado en {out_path}" + Style.RESET_ALL)
        elif method == 'qr':
            if QR_OPTIMIZED_AVAILABLE:
                print(Fore.YELLOW + "Usando QR optimizado..." + Style.RESET_ALL)
                qr_files = args.input or input("Rutas de los códigos QR (separadas por espacios): ").strip()
                qr_file_list = qr_files.split()
                if transport_qr.reconstruir_archivo_multiple_qr(qr_file_list, out_path):
                    print(Fore.GREEN + f"✅ Archivo reconstruido exitosamente" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "❌ Error reconstruyendo archivo desde QR" + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + "QR optimizado no disponible. Usando QR simple..." + Style.RESET_ALL)
                qr_path = args.input or input("Ruta del código QR: ").strip()
                datos = transport.leer_qr(qr_path)
                with open(out_path, 'wb') as f:
                    f.write(datos)
                print(Fore.GREEN + f"Archivo recibido y guardado en {out_path}" + Style.RESET_ALL)
        elif method == 'bluetooth':
            if not BLUETOOTH_AVAILABLE:
                print(Fore.RED + "Bluetooth real no disponible. Usando simulación." + Style.RESET_ALL)
                address = args.address or input("Dirección Bluetooth del emisor: ").strip()
                datos = transport.recibir_bluetooth(address)
                with open(out_path, 'wb') as f:
                    f.write(datos)
                print(Fore.GREEN + f"Archivo recibido y guardado en {out_path}" + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + "Esperando archivo por Bluetooth real (RFCOMM)..." + Style.RESET_ALL)
                port = args.port or 3
                transport_bluetooth.recibir_bluetooth_real(out_path, port)
        elif method == 'p2p':
            if not P2P_AVAILABLE:
                print(Fore.RED + "Transporte P2P no disponible." + Style.RESET_ALL)
                return
            port = args.port or 8080
            use_tor = args.tor
            print(Fore.YELLOW + f"🌐 Iniciando servidor P2P en puerto {port}..." + Style.RESET_ALL)
            if use_tor:
                print(Fore.CYAN + "🔗 Usando Tor para anonimato" + Style.RESET_ALL)
            server = transport_p2p.P2PServer(port, use_tor)
            server.start(out_path)
        elif method == 'onion':
            if not P2P_AVAILABLE:
                print(Fore.RED + "Transporte Onion no disponible." + Style.RESET_ALL)
                return
            port = args.port or 8080
            print(Fore.YELLOW + f"🌐 Iniciando servidor Onion en puerto {port}..." + Style.RESET_ALL)
            print(Fore.CYAN + "🔗 Configurando servicio Onion..." + Style.RESET_ALL)
            server = transport_p2p.P2PServer(port, use_tor=True)
            server.start(out_path)
        elif method == 'tor':
            if not TOR_AVAILABLE:
                print(Fore.RED + "Transporte Tor no disponible." + Style.RESET_ALL)
                return
            url = args.url or input("URL del endpoint Tor (ej: http://127.0.0.1:5000/download): ").strip()
            if not url.startswith('http'):
                print(Fore.RED + "❌ La URL debe comenzar con http o https." + Style.RESET_ALL)
                return
            datos = transport_tor.receive_data_tor(url)
            with open(out_path, 'wb') as f:
                f.write(datos)
            print(Fore.GREEN + f"Archivo recibido por Tor y guardado en {out_path}" + Style.RESET_ALL)
        else:
            print(Fore.RED + "Método de recepción no soportado." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ Error inesperado: {e}" + Style.RESET_ALL)
        print(Fore.YELLOW + "Si el problema persiste, reporta el error en https://github.com/tu-repo/titansend/issues" + Style.RESET_ALL)

def scan_bluetooth(args):
    if not BLUETOOTH_AVAILABLE:
        print(Fore.RED + "Bluetooth real no disponible. Instala pybluez: pip install pybluez" + Style.RESET_ALL)
        return
    print(Fore.CYAN + "Buscando dispositivos Bluetooth cercanos..." + Style.RESET_ALL)
    transport_bluetooth.buscar_dispositivos()

def check_tor(args):
    if not P2P_AVAILABLE:
        print(Fore.RED + "Transporte P2P/Onion no disponible." + Style.RESET_ALL)
        return
    print(Fore.CYAN + "🔍 Verificando disponibilidad de Tor y SOCKS..." + Style.RESET_ALL)
    tor_ok, tor_msg = transport_p2p.verificar_tor()
    socks_ok, socks_msg = transport_p2p.verificar_socks()
    if tor_ok:
        print(Fore.GREEN + f"✅ {tor_msg}" + Style.RESET_ALL)
    else:
        print(Fore.RED + f"❌ {tor_msg}" + Style.RESET_ALL)
    if socks_ok:
        print(Fore.GREEN + f"✅ {socks_msg}" + Style.RESET_ALL)
    else:
        print(Fore.RED + f"❌ {socks_msg}" + Style.RESET_ALL)
    if tor_ok and socks_ok:
        print(Fore.GREEN + "🎉 Tor y SOCKS están listos para uso anónimo" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "⚠️  Para usar Onion, instala: pip install stem PySocks" + Style.RESET_ALL)

def generate_onion(args):
    if not P2P_AVAILABLE:
        print(Fore.RED + "Transporte P2P/Onion no disponible." + Style.RESET_ALL)
        return
    port = args.port or 8080
    print(Fore.CYAN + f"🔗 Generando nueva dirección Onion para puerto {port}..." + Style.RESET_ALL)
    service_id = transport_p2p.generar_direccion_onion(port)
    if service_id:
        print(Fore.GREEN + f"✅ Nueva dirección Onion: {service_id}.onion" + Style.RESET_ALL)
        print(Fore.BLUE + f"📡 Usa: titansend receive --method onion --port {port}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "❌ Error generando dirección Onion" + Style.RESET_ALL)
        print(Fore.YELLOW + "💡 Asegúrate de que Tor esté ejecutándose y configurado" + Style.RESET_ALL)

def get_onion_address(args):
    if not P2P_AVAILABLE:
        print(Fore.RED + "Transporte P2P/Onion no disponible." + Style.RESET_ALL)
        return
    print(Fore.CYAN + "🔍 Obteniendo dirección Onion actual..." + Style.RESET_ALL)
    onion_address = transport_p2p.obtener_direccion_onion()
    if onion_address:
        print(Fore.GREEN + f"✅ Dirección Onion actual: {onion_address}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "❌ No se pudo obtener dirección Onion" + Style.RESET_ALL)
        print(Fore.YELLOW + "💡 Asegúrate de que Tor esté ejecutándose y configurado" + Style.RESET_ALL)

def genkey(args):
    priv_path = args.private
    pub_path = args.public
    if os.path.exists(priv_path) or os.path.exists(pub_path):
        if not confirmar_sobrescritura(priv_path) or not confirmar_sobrescritura(pub_path):
            return
    priv, pub = crypto.generar_par_claves()
    with open(priv_path, 'wb') as f:
        f.write(priv)
    with open(pub_path, 'wb') as f:
        f.write(pub)
    print(Fore.GREEN + f"Claves generadas: {priv_path}, {pub_path}" + Style.RESET_ALL)

def check_integrity(args):
    file_path = args.file_path
    privkey_path = args.key
    if not os.path.isfile(file_path) or not os.path.isfile(privkey_path):
        print(Fore.RED + "Archivo o clave no encontrados." + Style.RESET_ALL)
        return
    with open(file_path, 'rb') as f:
        datos = f.read()
    with open(privkey_path, 'rb') as f:
        privkey = serialization.load_pem_private_key(f.read(), password=None)
    salt = datos[:16]
    aes_key_cifrada = datos[16:16+256]
    firma = datos[16+256:16+256+32]
    cifrado = datos[16+256+32:]
    aes_key = crypto.descifrar_con_privada(privkey, aes_key_cifrada)
    if crypto.verificar_hmac(aes_key, cifrado, firma):
        print(Fore.GREEN + "Integridad verificada correctamente." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Integridad NO verificada. El archivo puede estar dañado o manipulado." + Style.RESET_ALL)

def diagnose(args):
    print(Fore.CYAN + "Diagnóstico del entorno TitanSend:" + Style.RESET_ALL)
    print("Bluetooth:", "OK" if BLUETOOTH_AVAILABLE else "NO DISPONIBLE")
    print("QR optimizado:", "OK" if QR_OPTIMIZED_AVAILABLE else "NO DISPONIBLE")
    print("P2P/Onion:", "OK" if P2P_AVAILABLE else "NO DISPONIBLE")
    print("Tor:", "OK" if TOR_AVAILABLE else "NO DISPONIBLE")

# En main():
integrity_parser = argparse._SubParsersAction.add_parser('check_integrity', help='Validar integridad de archivo cifrado')
integrity_parser.add_argument('file_path', help='Ruta del archivo cifrado')
integrity_parser.add_argument('--key', required=True, help='Clave privada para descifrar (PEM)')
integrity_parser.set_defaults(func=check_integrity)

def main():
    print(WELCOME)
    parser = argparse.ArgumentParser(description='TitanSend: Tu Búnker Digital Portátil',
        epilog='Ejemplo: python -m titansend.cli send archivo_cifrado.bin --method tor --url http://127.0.0.1:5000/upload')
    parser.add_argument('--version', action='version', version=f'TitanSend {VERSION}')
    subparsers = parser.add_subparsers(dest='command')

    lock_parser = subparsers.add_parser('lock', help='Cifrar y empaquetar un archivo',
        epilog='Ejemplo: python -m titansend.cli lock archivo.txt --public-key publica.pem --password tuclave --output archivo_cifrado.bin')
    lock_parser.add_argument('file_path', help='Ruta del archivo a cifrar')
    lock_parser.add_argument('--public-key', required=True, help='Clave pública del receptor (PEM)')
    lock_parser.add_argument('--password', help='Contraseña para generar la clave AES')
    lock_parser.add_argument('--output', required=True, help='Archivo de salida cifrado')
    lock_parser.set_defaults(func=lock)

    unlock_parser = subparsers.add_parser('unlock', help='Descifrar un archivo',
        epilog='Ejemplo: python -m titansend.cli unlock archivo_cifrado.bin --key privada.pem --password tuclave --output archivo_descifrado.txt')
    unlock_parser.add_argument('file_path', help='Ruta del archivo cifrado')
    unlock_parser.add_argument('--key', required=True, help='Clave privada para descifrar (PEM)')
    unlock_parser.add_argument('--password', help='Contraseña para la clave AES')
    unlock_parser.add_argument('--output', help='Archivo de salida descifrado (opcional)')
    unlock_parser.set_defaults(func=unlock)

    split_parser = subparsers.add_parser('split', help='Dividir la clave en fragmentos')
    split_parser.add_argument('private_key_path', help='Ruta de la clave privada a dividir')
    split_parser.add_argument('--shares', type=int, required=True, help='Número de fragmentos')
    split_parser.add_argument('--threshold', type=int, required=True, help='Número mínimo de fragmentos necesarios para reconstruir la clave')
    split_parser.set_defaults(func=split)

    reconstruct_parser = subparsers.add_parser('reconstruct', help='Reconstruir la clave a partir de fragmentos')
    reconstruct_parser.add_argument('shares', nargs='+', help='Rutas de los fragmentos')
    reconstruct_parser.set_defaults(func=reconstruct)

    send_parser = subparsers.add_parser('send', help='Enviar un archivo cifrado',
        epilog='Ejemplo: python -m titansend.cli send archivo_cifrado.bin --method tor --url http://127.0.0.1:5000/upload')
    send_parser.add_argument('file_path', help='Ruta del archivo cifrado a enviar')
    send_parser.add_argument('--method', choices=['bluetooth', 'qr', 'usb', 'p2p', 'onion', 'tor'], required=True, help='Método de transporte')
    send_parser.add_argument('--output', help='Ruta de salida para USB/QR (opcional)')
    send_parser.add_argument('--address', help='Dirección Bluetooth (opcional)')
    send_parser.add_argument('--port', type=int, default=3, help='Puerto RFCOMM para Bluetooth (default 3)')
    send_parser.add_argument('--host', help='Host del receptor para P2P')
    send_parser.add_argument('--tor', action='store_true', help='Usar TOR para P2P')
    send_parser.add_argument('--onion', help='Dirección Onion del receptor')
    send_parser.add_argument('--url', help='URL del endpoint Tor (para método tor)')
    send_parser.set_defaults(func=send)

    receive_parser = subparsers.add_parser('receive', help='Recibir un archivo cifrado',
        epilog='Ejemplo: python -m titansend.cli receive --method tor --url http://127.0.0.1:5000/download --output archivo_recibido.bin')
    receive_parser.add_argument('--method', choices=['bluetooth', 'qr', 'usb', 'p2p', 'onion', 'tor'], required=True, help='Método de recepción')
    receive_parser.add_argument('--input', help='Ruta del archivo de entrada (para USB/QR)')
    receive_parser.add_argument('--output', help='Ruta de salida para guardar el archivo recibido')
    receive_parser.add_argument('--address', help='Dirección Bluetooth (opcional)')
    receive_parser.add_argument('--port', type=int, default=3, help='Puerto RFCOMM para Bluetooth (default 3)')
    receive_parser.add_argument('--url', help='URL del endpoint Tor (para método tor)')
    receive_parser.set_defaults(func=receive)

    scan_parser = subparsers.add_parser('scan', help='Buscar dispositivos Bluetooth cercanos')
    scan_parser.set_defaults(func=scan_bluetooth)

    check_tor_parser = subparsers.add_parser('check_tor', help='Verificar disponibilidad de Tor y SOCKS')
    check_tor_parser.set_defaults(func=check_tor)

    generate_onion_parser = subparsers.add_parser('generate_onion', help='Generar nueva dirección Onion')
    generate_onion_parser.add_argument('--port', type=int, default=8080, help='Puerto para la nueva dirección Onion')
    generate_onion_parser.set_defaults(func=generate_onion)

    get_onion_address_parser = subparsers.add_parser('get_onion_address', help='Obtener dirección Onion actual')
    get_onion_address_parser.set_defaults(func=get_onion_address)

    genkey_parser = subparsers.add_parser('genkey', help='Generar par de claves RSA')
    genkey_parser.add_argument('--private', required=True, help='Ruta para la clave privada')
    genkey_parser.add_argument('--public', required=True, help='Ruta para la clave pública')
    genkey_parser.set_defaults(func=genkey)

    integrity_parser = subparsers.add_parser('check_integrity', help='Validar integridad de archivo cifrado')
    integrity_parser.add_argument('file_path', help='Ruta del archivo cifrado')
    integrity_parser.add_argument('--key', required=True, help='Clave privada para descifrar (PEM)')
    integrity_parser.set_defaults(func=check_integrity)

    diagnose_parser = subparsers.add_parser('diagnose', help='Diagnóstico rápido del entorno')
    diagnose_parser.set_defaults(func=diagnose)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()