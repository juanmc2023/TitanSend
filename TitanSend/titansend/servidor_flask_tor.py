from flask import Flask, request, send_file, jsonify
import os
from datetime import datetime
import uuid
import threading

app = Flask(__name__)

# Configuración por variables de entorno
ARCHIVO = os.environ.get('TSEND_FILE', 'archivo_tor.bin')
MAX_SIZE = int(os.environ.get('TSEND_MAX_SIZE', 100 * 1024 * 1024))  # 100 MB por defecto
SOLO_LECTURA = os.environ.get('TSEND_SOLO_LECTURA', '0') == '1'
MULTIARCHIVO = os.environ.get('TSEND_MULTIARCHIVO', '0') == '1'
TOKEN = os.environ.get('TSEND_TOKEN', None)  # Token opcional para autenticación

# Lock para acceso concurrente seguro a archivos
file_lock = threading.Lock()

def borrar_seguro(path):
    """Borra un archivo sobrescribiéndolo con datos aleatorios antes de eliminarlo."""
    if os.path.isfile(path):
        tam = os.path.getsize(path)
        try:
            with open(path, 'ba+', buffering=0) as f:
                f.seek(0)
                f.write(os.urandom(tam))
            os.remove(path)
            return True
        except Exception as e:
            print(f"[{datetime.now()}] [ERROR] Borrado seguro falló: {e}")
    return False

def validar_nombre_archivo(nombre):
    """Evita rutas relativas y caracteres peligrosos en nombres de archivo."""
    if not nombre or '..' in nombre or '/' in nombre or '\\' in nombre:
        return False
    if not nombre.endswith('.bin'):
        return False
    return True

@app.after_request
def set_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Content-Security-Policy'] = "default-src 'none';"
    return response

def require_token():
    if TOKEN and request.headers.get('Authorization') != f"Bearer {TOKEN}":
        return jsonify({"error": "No autorizado"}), 401

@app.route('/upload', methods=['POST'])
def upload():
    if TOKEN:
        auth = require_token()
        if auth: return auth
    if SOLO_LECTURA:
        return jsonify({"error": "Servidor en modo solo lectura"}), 403
    tam = len(request.data)
    if tam > MAX_SIZE:
        return jsonify({"error": "Archivo demasiado grande"}), 413
    if MULTIARCHIVO:
        file_id = str(uuid.uuid4())
        fname = f"{file_id}.bin"
        if not validar_nombre_archivo(fname):
            return jsonify({"error": "Nombre de archivo inválido"}), 400
        with file_lock:
            with open(fname, 'wb') as f:
                f.write(request.data)
        print(f"[{datetime.now()}] [UPLOAD] Archivo recibido - {tam} bytes guardados como '{fname}'")
        return jsonify({"msg": f"Archivo recibido ({tam} bytes)", "id": file_id}), 200
    else:
        if os.path.exists(ARCHIVO):
            return jsonify({"error": "Ya existe un archivo pendiente de descarga. Borra antes de subir uno nuevo."}), 409
        with file_lock:
            with open(ARCHIVO, 'wb') as f:
                f.write(request.data)
        print(f"[{datetime.now()}] [UPLOAD] Archivo recibido - {tam} bytes guardados en '{ARCHIVO}'")
        return jsonify({"msg": f"Archivo recibido ({tam} bytes)"}), 200

@app.route('/download', methods=['GET'])
def download():
    if TOKEN:
        auth = require_token()
        if auth: return auth
    if MULTIARCHIVO:
        file_id = request.args.get('id')
        fname = f"{file_id}.bin" if file_id else None
        if not file_id or not validar_nombre_archivo(fname):
            return jsonify({"error": "Falta o nombre de archivo inválido en parámetro id"}), 400
        if os.path.exists(fname):
            tam = os.path.getsize(fname)
            print(f"[{datetime.now()}] [DOWNLOAD] Archivo '{fname}' de {tam} bytes enviado")
            response = send_file(fname, as_attachment=True)
            # Descarga de un solo uso: borrar tras enviar
            if os.environ.get('TSEND_UNICO', '0') == '1':
                threading.Thread(target=borrar_seguro, args=(fname,)).start()
            return response
        else:
            print(f"[{datetime.now()}] [DOWNLOAD] Solicitud de descarga pero archivo '{fname}' no encontrado")
            return jsonify({"error": "Archivo no encontrado"}), 404
    else:
        if os.path.exists(ARCHIVO):
            tam = os.path.getsize(ARCHIVO)
            print(f"[{datetime.now()}] [DOWNLOAD] Archivo '{ARCHIVO}' de {tam} bytes enviado")
            response = send_file(ARCHIVO, as_attachment=True)
            # Descarga de un solo uso: borrar tras enviar
            if os.environ.get('TSEND_UNICO', '0') == '1':
                threading.Thread(target=borrar_seguro, args=(ARCHIVO,)).start()
            return response
        else:
            print(f"[{datetime.now()}] [DOWNLOAD] Solicitud de descarga pero archivo no encontrado")
            return jsonify({"error": "Archivo no encontrado"}), 404

@app.route('/delete', methods=['POST'])
def delete():
    if TOKEN:
        auth = require_token()
        if auth: return auth
    if SOLO_LECTURA:
        return jsonify({"error": "Servidor en modo solo lectura"}), 403
    if MULTIARCHIVO:
        file_id = request.args.get('id')
        fname = f"{file_id}.bin" if file_id else None
        if not file_id or not validar_nombre_archivo(fname):
            return jsonify({"error": "Falta o nombre de archivo inválido en parámetro id"}), 400
        if os.path.exists(fname):
            ok = borrar_seguro(fname)
            print(f"[{datetime.now()}] [DELETE] Archivo '{fname}' borrado seguro: {ok}")
            return jsonify({"msg": "Archivo borrado" if ok else "Archivo eliminado sin sobrescribir"}), 200
        return jsonify({"error": "Archivo no encontrado"}), 404
    else:
        if os.path.exists(ARCHIVO):
            ok = borrar_seguro(ARCHIVO)
            print(f"[{datetime.now()}] [DELETE] Archivo '{ARCHIVO}' borrado seguro: {ok}")
            return jsonify({"msg": "Archivo borrado" if ok else "Archivo eliminado sin sobrescribir"}), 200
        return jsonify({"error": "Archivo no encontrado"}), 404

@app.route('/status', methods=['GET'])
def status():
    """
    Endpoint simple para saber si el servidor está listo y si hay archivo disponible.
    Incluye espacio libre en disco.
    """
    statvfs = os.statvfs('.')
    espacio_libre = statvfs.f_frsize * statvfs.f_bavail
    if MULTIARCHIVO:
        archivos = [f for f in os.listdir('.') if f.endswith('.bin')]
        return jsonify({
            "status": "ok",
            "archivos": archivos,
            "multiarchivo": True,
            "espacio_libre_MB": espacio_libre // (1024 * 1024)
        })
    else:
        existe = os.path.exists(ARCHIVO)
        tam = os.path.getsize(ARCHIVO) if existe else 0
        return jsonify({
            "status": "ok",
            "archivo_disponible": existe,
            "tamano": tam,
            "multiarchivo": False,
            "espacio_libre_MB": espacio_libre // (1024 * 1024)
        })

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud para monitoreo."""
    return jsonify({"status": "ok", "hora": datetime.now().isoformat()})

if __name__ == '__main__':
    print(f"[{datetime.now()}] Servidor Flask iniciado en http://0.0.0.0:5000")
    print(f"Archivo: {ARCHIVO} | Tamaño máximo: {MAX_SIZE // (1024*1024)} MB | Solo lectura: {SOLO_LECTURA} | Multiarchivo: {MULTIARCHIVO}")
    if TOKEN:
        print("¡Autenticación por token habilitada!")
    app.run(host='0.0.0.0', port=5000)