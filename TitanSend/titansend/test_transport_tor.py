import argparse
import sys
import hashlib
import time
from urllib.parse import urlparse
from transport_tor import send_data_tor, receive_data_tor

def hash_datos(datos):
    return hashlib.sha256(datos).hexdigest()

def validar_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https')

def main():
    parser = argparse.ArgumentParser(
        description='Prueba de transporte Tor para TitanSend',
        epilog="""
Ejemplos:
  python test_transport_tor.py --mode send --url http://127.0.0.1:5000/upload --data "Hola Tor"
  python test_transport_tor.py --mode send --url http://127.0.0.1:5000/upload --file archivo.bin
  python test_transport_tor.py --mode receive --url http://127.0.0.1:5000/download --output recibido.bin
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--mode', choices=['send', 'receive'], required=True, help='Modo: send o receive')
    parser.add_argument('--url', required=True, help='URL del endpoint Tor')
    parser.add_argument('--data', help='Datos a enviar (modo send)')
    parser.add_argument('--file', help='Archivo a enviar (modo send)')
    parser.add_argument('--output', help='Archivo de salida (modo receive)')
    parser.add_argument('--show-hash', action='store_true', help='Mostrar SHA256 de los datos enviados/recibidos')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout en segundos para la operación')
    parser.add_argument('--header', action='append', help='Cabecera HTTP personalizada, formato: Nombre:Valor')
    parser.add_argument('--verbose', action='store_true', help='Mostrar logs detallados')
    args = parser.parse_args()

    if not validar_url(args.url):
        print('URL inválida. Debe comenzar con http:// o https://')
        sys.exit(1)

    headers = {}
    if args.header:
        for h in args.header:
            if ':' in h:
                k, v = h.split(':', 1)
                headers[k.strip()] = v.strip()
            else:
                print(f'Cabecera inválida: {h} (debe ser Nombre:Valor)')
                sys.exit(1)

    if args.mode == 'send':
        if not args.data and not args.file:
            print('Debes especificar --data o --file en modo send')
            sys.exit(1)
        if args.file:
            try:
                with open(args.file, 'rb') as f:
                    datos = f.read()
            except Exception as e:
                print(f'Error leyendo archivo: {e}')
                sys.exit(1)
        else:
            datos = args.data.encode()
        try:
            if args.verbose:
                print(f"[{time.strftime('%H:%M:%S')}] Enviando datos a {args.url} (timeout={args.timeout}s)...")
            start = time.time()
            respuesta = send_data_tor(args.url, datos, timeout=args.timeout, headers=headers if headers else None)
            elapsed = time.time() - start
            print('Respuesta del servidor (POST):', respuesta)
            if args.show_hash:
                print('SHA256 de datos enviados:', hash_datos(datos))
            print('Tamaño enviado:', len(datos), 'bytes')
            print(f"Tiempo de envío: {elapsed:.2f} s")
        except Exception as e:
            print('Error al enviar datos por Tor:', e)
    elif args.mode == 'receive':
        try:
            if args.verbose:
                print(f"[{time.strftime('%H:%M:%S')}] Recibiendo datos de {args.url} (timeout={args.timeout}s)...")
            start = time.time()
            contenido, resp_info = receive_data_tor(args.url, timeout=args.timeout, headers=headers if headers else None, return_response_info=True)
            elapsed = time.time() - start
            if args.output:
                try:
                    with open(args.output, 'wb') as f:
                        f.write(contenido)
                    print(f'Contenido recibido guardado en {args.output}')
                except Exception as e:
                    print(f'Error guardando archivo: {e}')
            else:
                print('Contenido recibido (GET):', contenido)
            if args.show_hash:
                print('SHA256 de datos recibidos:', hash_datos(contenido))
            print('Tamaño recibido:', len(contenido), 'bytes')
            print(f"Código HTTP: {resp_info.get('status_code', 'N/A')}, Content-Type: {resp_info.get('content_type', 'N/A')}")
            print(f"Tiempo de recepción: {elapsed:.2f} s")
            if resp_info.get('error_content'):
                print("Contenido de error del servidor:", resp_info['error_content'])
        except Exception as e:
            print('Error al recibir datos por Tor:', e)

if __name__ == '__main__':
    main()