"""
Generación optimizada de códigos QR para TitanSend
- Compresión de datos antes de generar QR
- Fragmentación automática para archivos grandes
- Parámetros optimizados para máxima capacidad
"""
import os
import zlib
import json
import qrcode
from qrcode.constants import ERROR_CORRECT_L
from colorama import Fore, Style

# Configuración optimizada para máxima capacidad
QR_CONFIG = {
    'version': 40,  # Máximo tamaño (177x177 módulos)
    'error_correction': ERROR_CORRECT_L,  # 7% de corrección de errores (máxima capacidad)
    'box_size': 2,  # Tamaño de cada módulo
    'border': 1,  # Borde mínimo
    'max_data_bytes': 2956  # Capacidad máxima en bytes para QR v40 con L
}

def comprimir_datos(datos):
    """Comprime datos usando zlib para reducir tamaño"""
    return zlib.compress(datos, level=9)  # Máxima compresión

def descomprimir_datos(datos_comprimidos):
    """Descomprime datos usando zlib"""
    return zlib.decompress(datos_comprimidos)

def calcular_fragmentos(datos, max_bytes=QR_CONFIG['max_data_bytes']):
    """Calcula cuántos fragmentos QR se necesitan"""
    datos_comprimidos = comprimir_datos(datos)
    return (len(datos_comprimidos) + max_bytes - 1) // max_bytes

def generar_qr_optimizado(datos, ruta_salida, fragmento_num=1, total_fragmentos=1):
    """Genera un código QR optimizado con metadatos de fragmentación"""
    datos_comprimidos = comprimir_datos(datos)
    
    # Si es un solo fragmento
    if total_fragmentos == 1:
        qr_data = datos_comprimidos
    else:
        # Dividir en fragmentos y añadir metadatos
        max_bytes = QR_CONFIG['max_data_bytes'] - 50  # Reservar espacio para metadatos
        start_idx = (fragmento_num - 1) * max_bytes
        end_idx = min(start_idx + max_bytes, len(datos_comprimidos))
        fragmento_data = datos_comprimidos[start_idx:end_idx]
        
        # Metadatos del fragmento
        metadata = {
            'fragmento': fragmento_num,
            'total': total_fragmentos,
            'tamaño_original': len(datos),
            'tamaño_comprimido': len(datos_comprimidos),
            'checksum': zlib.crc32(datos_comprimidos) & 0xffffffff
        }
        
        # Codificar metadatos + datos
        qr_data = json.dumps(metadata).encode() + b'|' + fragmento_data
    
    # Generar QR optimizado
    qr = qrcode.QRCode(
        version=QR_CONFIG['version'],
        error_correction=QR_CONFIG['error_correction'],
        box_size=QR_CONFIG['box_size'],
        border=QR_CONFIG['border']
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Crear imagen
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar con nombre descriptivo
    if total_fragmentos == 1:
        filename = ruta_salida
    else:
        base, ext = os.path.splitext(ruta_salida)
        filename = f"{base}_parte_{fragmento_num:02d}_de_{total_fragmentos:02d}{ext}"
    
    img.save(filename)
    return filename

def generar_qr_multiple(datos, ruta_base):
    """Genera múltiples códigos QR para archivos grandes"""
    total_fragmentos = calcular_fragmentos(datos)
    
    if total_fragmentos == 1:
        # Archivo pequeño, un solo QR
        filename = generar_qr_optimizado(datos, ruta_base, 1, 1)
        print(f"✅ Código QR generado: {filename}")
        print(f"📊 Tamaño original: {len(datos)} bytes")
        print(f"📊 Tamaño comprimido: {len(comprimir_datos(datos))} bytes")
        return [filename]
    else:
        # Archivo grande, múltiples QR
        print(f"📦 Archivo grande detectado. Generando {total_fragmentos} códigos QR...")
        archivos_generados = []
        
        for i in range(1, total_fragmentos + 1):
            filename = generar_qr_optimizado(datos, ruta_base, i, total_fragmentos)
            archivos_generados.append(filename)
            print(f"✅ QR {i}/{total_fragmentos}: {filename}")
        
        print(f"📊 Tamaño original: {len(datos)} bytes")
        print(f"📊 Tamaño comprimido: {len(comprimir_datos(datos))} bytes")
        print(f"📊 Fragmentos generados: {total_fragmentos}")
        return archivos_generados

def leer_qr_optimizado(ruta_qr):
    """Lee un código QR optimizado"""
    try:
        # Leer imagen QR
        img = qrcode.make(ruta_qr)
        qr = qrcode.QRCode()
        qr.add_data(img)
        qr.make()
        
        # Extraer datos
        qr_data = qr.get_data()
        if not qr_data:
            raise ValueError("No se pudieron extraer datos del QR")
        
        # Verificar si es un fragmento
        if b'|' in qr_data:
            # Es un fragmento con metadatos
            metadata_str, fragmento_data = qr_data.split(b'|', 1)
            metadata = json.loads(metadata_str.decode())
            return {
                'tipo': 'fragmento',
                'metadata': metadata,
                'datos': fragmento_data
            }
        else:
            # Es un QR completo
            return {
                'tipo': 'completo',
                'datos': qr_data
            }
    except Exception as e:
        raise ValueError(f"Error leyendo QR: {e}")

def reconstruir_archivo_multiple_qr(rutas_qr, ruta_salida):
    """Reconstruye un archivo desde múltiples códigos QR"""
    fragmentos = {}
    metadata = None
    
    print(f"🔍 Leyendo {len(rutas_qr)} códigos QR...")
    
    for ruta in rutas_qr:
        try:
            resultado = leer_qr_optimizado(ruta)
            if resultado['tipo'] == 'fragmento':
                fragmentos[resultado['metadata']['fragmento']] = resultado['datos']
                metadata = resultado['metadata']
            else:
                # Es un QR completo
                datos_comprimidos = resultado['datos']
                datos_originales = descomprimir_datos(datos_comprimidos)
                with open(ruta_salida, 'wb') as f:
                    f.write(datos_originales)
                print(f"✅ Archivo reconstruido: {ruta_salida}")
                return True
        except Exception as e:
            print(f"❌ Error leyendo {ruta}: {e}")
            return False
    
    # Reconstruir desde fragmentos
    if not fragmentos or not metadata:
        print("❌ No se pudieron leer los fragmentos correctamente")
        return False
    
    # Verificar que tengamos todos los fragmentos
    fragmentos_esperados = set(range(1, metadata['total'] + 1))
    fragmentos_obtenidos = set(fragmentos.keys())
    
    if fragmentos_esperados != fragmentos_obtenidos:
        print(f"❌ Fragmentos faltantes: {fragmentos_esperados - fragmentos_obtenidos}")
        return False
    
    # Reconstruir datos comprimidos
    datos_comprimidos = b''
    for i in range(1, metadata['total'] + 1):
        datos_comprimidos += fragmentos[i]
    
    # Verificar checksum
    checksum_calculado = zlib.crc32(datos_comprimidos) & 0xffffffff
    if checksum_calculado != metadata['checksum']:
        print("❌ Error de integridad: checksum no coincide")
        return False
    
    # Descomprimir y guardar
    try:
        datos_originales = descomprimir_datos(datos_comprimidos)
        with open(ruta_salida, 'wb') as f:
            f.write(datos_originales)
        print(f"✅ Archivo reconstruido: {ruta_salida}")
        print(f"📊 Tamaño original: {metadata['tamaño_original']} bytes")
        print(f"📊 Fragmentos utilizados: {metadata['total']}")
        return True
    except Exception as e:
        print(f"❌ Error descomprimiendo: {e}")
        return False

def generar_qr_simple(datos, ruta_salida):
    """Función simple para compatibilidad con el código existente"""
    return generar_qr_multiple(datos, ruta_salida)

def leer_qr_simple(ruta_qr):
    """Función simple para compatibilidad con el código existente"""
    resultado = leer_qr_optimizado(ruta_qr)
    if resultado['tipo'] == 'completo':
        return descomprimir_datos(resultado['datos'])
    else:
        raise ValueError("Este QR es un fragmento. Usa reconstruir_archivo_multiple_qr()")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="QR optimizado para TitanSend")
    subparsers = parser.add_subparsers(dest='cmd')
    
    gen = subparsers.add_parser('generate', help='Generar QR optimizado')
    gen.add_argument('file', help='Archivo a convertir en QR')
    gen.add_argument('output', help='Ruta base para los QR generados')
    
    read = subparsers.add_parser('read', help='Leer QR y reconstruir archivo')
    read.add_argument('qr_files', nargs='+', help='Archivos QR a leer')
    read.add_argument('output', help='Archivo de salida')
    
    args = parser.parse_args()
    
    if args.cmd == 'generate':
        with open(args.file, 'rb') as f:
            datos = f.read()
        generar_qr_multiple(datos, args.output)
    elif args.cmd == 'read':
        reconstruir_archivo_multiple_qr(args.qr_files, args.output)
    else:
        parser.print_help() 