import os
import struct
import time
import json
from cryptography.hazmat.primitives.ciphers import aead

# =========================
# Guardar registro cifrado con longitud, autenticidad y timestamp (AES-GCM)
# =========================

def guardar_log(mensaje: str, clave: bytes, ruta: str, usuario: str = None):
    """
    Guarda un mensaje en el log cifrado usando AES-GCM.
    El formato es: [nonce (12)] + [longitud (4)] + [cifrado+tag (longitud)]
    El mensaje se almacena como JSON con timestamp y usuario.
    """
    nonce = os.urandom(12)
    aesgcm = aead.AESGCM(clave)
    timestamp = int(time.time())
    log_entry = {
        "timestamp": timestamp,
        "mensaje": mensaje,
    }
    if usuario:
        log_entry["usuario"] = usuario
    cifrado = aesgcm.encrypt(nonce, json.dumps(log_entry).encode(), None)
    longitud = struct.pack('>I', len(cifrado))
    with open(ruta, 'ab') as f:
        f.write(nonce + longitud + cifrado)

def leer_logs(clave: bytes, ruta: str, mostrar_json: bool = False, usuario: str = None, desde: int = None, hasta: int = None):
    """
    Lee todos los mensajes del log cifrado usando AES-GCM.
    Devuelve una lista de mensajes descifrados (como string o dict si mostrar_json=True).
    Permite filtrar por usuario y por rango de fechas (timestamp UNIX).
    Si la clave es incorrecta, muestra advertencia si todos los mensajes fallan.
    """
    logs = []
    if not os.path.isfile(ruta):
        return logs
    with open(ruta, 'rb') as f:
        data = f.read()
    i = 0
    errores = 0
    while i + 16 <= len(data):  # 12 bytes nonce + 4 bytes longitud
        nonce = data[i:i+12]
        i += 12
        longitud = struct.unpack('>I', data[i:i+4])[0]
        i += 4
        cifrado = data[i:i+longitud]
        i += longitud
        aesgcm = aead.AESGCM(clave)
        try:
            mensaje = aesgcm.decrypt(nonce, cifrado, None)
            try:
                log_entry = json.loads(mensaje.decode(errors='ignore'))
                # Filtros por usuario y fecha
                if usuario and log_entry.get("usuario") != usuario:
                    continue
                ts = log_entry.get("timestamp", 0)
                if (desde is not None and ts < desde) or (hasta is not None and ts > hasta):
                    continue
                if mostrar_json:
                    logs.append(log_entry)
                else:
                    ts_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
                    usuario_str = f"[{log_entry['usuario']}]" if "usuario" in log_entry else ""
                    logs.append(f"{ts_str} {usuario_str} {log_entry.get('mensaje', '')}".strip())
            except Exception:
                logs.append(mensaje.decode(errors='ignore'))
        except Exception:
            logs.append("[ERROR DE DESCIFRADO O INTEGRIDAD]")
            errores += 1
    if errores == len(logs) and len(logs) > 0:
        logs.append("[ADVERTENCIA] Todos los mensajes fallaron al descifrar. ¿Clave incorrecta?")
    return logs

def leer_logs_por_fecha(clave: bytes, ruta: str, desde: int = None, hasta: int = None):
    """
    Lee los logs filtrando por rango de fechas (timestamp UNIX).
    Devuelve una lista de dicts.
    """
    return leer_logs(clave, ruta, mostrar_json=True, desde=desde, hasta=hasta)

def leer_log(clave: bytes, ruta: str):
    """
    Lee y concatena todos los mensajes del log cifrado como un solo string.
    """
    logs = leer_logs(clave, ruta)
    return '\n'.join(logs)

def leer_ultimo_log(clave: bytes, ruta: str):
    """
    Lee solo la última entrada del log cifrado.
    """
    logs = leer_logs(clave, ruta)
    return logs[-1] if logs else None

def rotar_log(ruta: str, max_bytes: int = 5 * 1024 * 1024):
    """
    Rota el archivo de log si supera max_bytes (por defecto 5MB).
    Renombra el archivo actual y crea uno nuevo.
    Devuelve el nombre del archivo rotado o None si no se rotó.
    """
    if os.path.isfile(ruta) and os.path.getsize(ruta) > max_bytes:
        base, ext = os.path.splitext(ruta)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        nuevo_nombre = f"{base}_{timestamp}{ext}"
        os.rename(ruta, nuevo_nombre)
        return nuevo_nombre
    return None

def borrar_log_seguro(ruta: str):
    """
    Borra el archivo de log de forma segura (sobrescribe antes de eliminar).
    """
    if os.path.isfile(ruta):
        tam = os.path.getsize(ruta)
        with open(ruta, 'ba+', buffering=0) as f:
            f.seek(0)
            f.write(os.urandom(tam))
        os.remove(ruta)