import argparse
import sys
import hashlib
from transport_p2p import send_data_p2p, receive_data_p2p

def hash_datos(datos):
    return hashlib.sha256(datos).hexdigest()

def main():
    parser = argparse.ArgumentParser(
        description='Prueba de transporte P2P',
        epilog="""
Ejemplos:
  python test_transport_p2p.py --mode receive --port 9000
  python test_transport_p2p.py --mode send --ip 127.0.0.1 --port 9000 --data "Hola mundo"
  python test_transport_p2p.py --mode send --auto --port 9000 --data "Test"
  python test_transport_p2p.py --mode send --ip 127.0.0.1 --port 9000 --file archivo.bin
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--mode', choices=['send', 'receive'], required=True, help='Modo: send o receive')
    parser.add_argument('--ip', help='IP del peer receptor (modo send)')
    parser.add_argument('--port', type=int, required=True, help='Puerto TCP')
    parser.add_argument('--data', help='Datos a enviar (modo send)')
    parser.add_argument('--file', help='Archivo a enviar (modo send)')
    parser.add_argument('--repeat', type=int, default=1, help='Repetir la prueba N veces')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout en segundos para recibir datos')
    parser.add_argument('--auto', action='store_true', help='Automatizar prueba: enviar y recibir en el mismo script (requiere threading)')
    args = parser.parse_args()

    def get_data():
        if args.file:
            try:
                with open(args.file, 'rb') as f:
                    return f.read()
            except Exception as e:
                print(f'Error leyendo archivo: {e}')
                sys.exit(1)
        elif args.data:
            return args.data.encode()
        else:
            print('Debes especificar --data o --file en modo send')
            sys.exit(1)

    if args.auto and args.mode == 'send':
        import threading
        import time

        def receiver():
            print(f'[AUTO] Esperando datos en el puerto {args.port}...')
            try:
                datos = receive_data_p2p(args.port, timeout=args.timeout)
                print('[AUTO] Datos recibidos:', datos)
                print('[AUTO] Tamaño:', len(datos), 'bytes')
                print('[AUTO] SHA256:', hash_datos(datos))
            except Exception as e:
                print(f'[AUTO] Error al recibir datos: {e}')

        t = threading.Thread(target=receiver, daemon=True)
        t.start()
        time.sleep(1)  # Espera a que el receptor esté listo

        for i in range(args.repeat):
            print(f'[AUTO] Enviando datos (iteración {i+1})...')
            datos_envio = get_data()
            try:
                send_data_p2p('127.0.0.1', args.port, datos_envio)
                print('[AUTO] Datos enviados. Tamaño:', len(datos_envio), 'SHA256:', hash_datos(datos_envio))
            except Exception as e:
                print(f'[AUTO] Error al enviar datos: {e}')
            time.sleep(0.5)
        t.join(timeout=args.timeout)
        return

    for i in range(args.repeat):
        if args.mode == 'receive':
            print(f'Esperando datos en el puerto {args.port}... (iteración {i+1})')
            try:
                datos = receive_data_p2p(args.port, timeout=args.timeout)
                print('Datos recibidos:', datos)
                print('Tamaño:', len(datos), 'bytes')
                print('SHA256:', hash_datos(datos))
            except Exception as e:
                print(f'Error al recibir datos: {e}')
        elif args.mode == 'send':
            if not args.ip or (not args.data and not args.file):
                print('Debes especificar --ip y --data o --file en modo send')
                sys.exit(1)
            datos_envio = get_data()
            print(f'Enviando datos a {args.ip}:{args.port}... (iteración {i+1})')
            try:
                send_data_p2p(args.ip, args.port, datos_envio)
                print('Datos enviados. Tamaño:', len(datos_envio), 'SHA256:', hash_datos(datos_envio))
            except Exception as e:
                print(f'Error al enviar datos: {e}')

if __name__ == '__main__':
    main()