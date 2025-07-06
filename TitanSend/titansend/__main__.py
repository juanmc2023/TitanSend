import sys
from colorama import Fore, Style
import os
from . import crypto, shamir, transport, log
from cryptography.hazmat.primitives import serialization

def confirmar_sobrescritura(ruta):
    if os.path.exists(ruta):
        resp = input(Fore.RED + f"El archivo '{ruta}' ya existe. ¿Desea sobrescribirlo? (s/n): " + Style.RESET_ALL).strip().lower()
        if resp != 's':
            print(Fore.YELLOW + "Operación cancelada por el usuario." + Style.RESET_ALL)
            return False
    return True

def leer_archivo_binario(ruta):
    try:
        with open(ruta, 'rb') as f:
            return f.read()
    except Exception as e:
        print(Fore.RED + f"Error al leer '{ruta}': {e}" + Style.RESET_ALL)
        return None

def escribir_archivo_binario(ruta, datos):
    try:
        with open(ruta, 'wb') as f:
            f.write(datos)
        return True
    except Exception as e:
        print(Fore.RED + f"Error al escribir '{ruta}': {e}" + Style.RESET_ALL)
        return False

def menu():
    print(Fore.CYAN + "\n=== TitanSend CLI ===" + Style.RESET_ALL)
    print("1. Cifrar archivo")
    print("2. Descifrar archivo")
    print("3. Fragmentar clave (Shamir)")
    print("4. Reconstruir clave (Shamir)")
    print("5. Enviar archivo")
    print("6. Recibir archivo")
    print("7. Escanear dispositivos Bluetooth")
    print("8. Verificar disponibilidad de Tor")
    print("9. Generar par de claves RSA")
    print("10. Ver registro cifrado")
    print("11. Enviar archivo por P2P/Onion")
    print("12. Recibir archivo por P2P/Onion")
    print("13. Validar integridad de archivo cifrado")
    print("0. Salir")
    return input("Seleccione una opción: ")

def cifrar_archivo():
    print(Fore.YELLOW + "\n[Cifrado de archivo]" + Style.RESET_ALL)
    ruta_archivo = input("Ruta del archivo a cifrar: ").strip()
    ruta_clave_pub = input("Ruta de la clave pública del receptor (PEM): ").strip()
    password = input("Contraseña para derivar clave AES: ").strip()
    ruta_salida = input("Ruta de salida del archivo cifrado: ").strip()
    ruta_log = input("Ruta del registro cifrado (opcional, enter para omitir): ").strip()

    if not os.path.isfile(ruta_archivo):
        print(Fore.RED + "Archivo a cifrar no encontrado." + Style.RESET_ALL)
        return
    if not os.path.isfile(ruta_clave_pub):
        print(Fore.RED + "Clave pública no encontrada." + Style.RESET_ALL)
        return
    if not confirmar_sobrescritura(ruta_salida):
        return

    datos = leer_archivo_binario(ruta_archivo)
    if datos is None:
        return
    pem = leer_archivo_binario(ruta_clave_pub)
    if pem is None:
        return
    try:
        clave_pub = crypto.deserializar_clave_publica(pem)
    except Exception as e:
        print(Fore.RED + f"Clave pública inválida: {e}" + Style.RESET_ALL)
        return
    salt = os.urandom(16)
    clave_aes = crypto.generar_clave_aes(password, salt)
    import time
    timestamp = int(time.time()).to_bytes(8, 'big')
    nonce = os.urandom(8)
    datos_a_cifrar = timestamp + nonce + datos
    cifrado = crypto.cifrar_aes(datos_a_cifrar, clave_aes)
    firma = crypto.firmar_hmac(clave_aes, cifrado)
    try:
        clave_aes_cifrada = crypto.cifrar_con_publica(clave_pub, clave_aes)
    except Exception as e:
        print(Fore.RED + f"Error cifrando la clave AES: {e}" + Style.RESET_ALL)
        return
    resultado = salt + clave_aes_cifrada + firma + cifrado
    if not escribir_archivo_binario(ruta_salida, resultado):
        return
    print(Fore.GREEN + f"Archivo cifrado y guardado en {ruta_salida}" + Style.RESET_ALL)
    if ruta_log:
        try:
            log.guardar_log(f"Cifrado: {ruta_archivo} -> {ruta_salida}", clave_aes, ruta_log)
            print(Fore.BLUE + "Registro guardado." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error guardando registro: {e}" + Style.RESET_ALL)

def descifrar_archivo():
    print(Fore.YELLOW + "\n[Descifrado de archivo]" + Style.RESET_ALL)
    ruta_archivo = input("Ruta del archivo cifrado: ").strip()
    ruta_clave_priv = input("Ruta de la clave privada (PEM): ").strip()
    password = input("Contraseña para derivar clave AES: ").strip()
    ruta_salida = input("Ruta de salida del archivo descifrado: ").strip()
    ruta_log = input("Ruta del registro cifrado (opcional, enter para omitir): ").strip()

    if not os.path.isfile(ruta_archivo):
        print(Fore.RED + "Archivo cifrado no encontrado." + Style.RESET_ALL)
        return
    if not os.path.isfile(ruta_clave_priv):
        print(Fore.RED + "Clave privada no encontrada." + Style.RESET_ALL)
        return
    if not confirmar_sobrescritura(ruta_salida):
        return

    datos = leer_archivo_binario(ruta_archivo)
    if datos is None:
        return
    pem = leer_archivo_binario(ruta_clave_priv)
    if pem is None:
        return
    try:
        clave_priv = serialization.load_pem_private_key(pem, password=None)
    except Exception as e:
        print(Fore.RED + f"Clave privada inválida: {e}" + Style.RESET_ALL)
        return
    try:
        salt = datos[:16]
        clave_aes_cifrada = datos[16:16+256]
        firma = datos[16+256:16+256+32]
        cifrado = datos[16+256+32:]
        clave_aes = crypto.descifrar_con_privada(clave_priv, clave_aes_cifrada)
        if not crypto.verificar_hmac(clave_aes, cifrado, firma):
            print(Fore.RED + "Firma HMAC inválida. El archivo puede haber sido manipulado." + Style.RESET_ALL)
            return
        descifrado = crypto.descifrar_aes(cifrado, clave_aes)
        datos_final = descifrado[16:]
    except Exception as e:
        print(Fore.RED + f"Error durante el descifrado: {e}" + Style.RESET_ALL)
        return
    if not escribir_archivo_binario(ruta_salida, datos_final):
        return
    print(Fore.GREEN + f"Archivo descifrado y guardado en {ruta_salida}" + Style.RESET_ALL)
    if ruta_log:
        try:
            log.guardar_log(f"Descifrado: {ruta_archivo} -> {ruta_salida}", clave_aes, ruta_log)
            print(Fore.BLUE + "Registro guardado." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error guardando registro: {e}" + Style.RESET_ALL)

def fragmentar_clave():
    print(Fore.YELLOW + "\n[Fragmentación de clave con Shamir]" + Style.RESET_ALL)
    clave = input("Clave a fragmentar: ").strip()
    try:
        n = int(input("¿En cuántas partes? (n): "))
        k = int(input("¿Cuántas partes mínimas para recuperar? (k): "))
        if n < 2 or k < 2 or k > n:
            print(Fore.RED + "Valores de n y k no válidos." + Style.RESET_ALL)
            return
        partes = shamir.fragmentar_clave(clave, n, k)
        for idx, parte in enumerate(partes):
            print(f"Parte {idx+1}: {parte}")
    except Exception as e:
        print(Fore.RED + f"Error fragmentando clave: {e}" + Style.RESET_ALL)

def reconstruir_clave():
    print(Fore.YELLOW + "\n[Reconstrucción de clave con Shamir]" + Style.RESET_ALL)
    partes = []
    print("Ingrese las partes (una por línea, vacío para terminar):")
    while True:
        parte = input()
        if not parte.strip():
            break
        partes.append(parte.strip())
    try:
        clave = shamir.reconstruir_clave(partes)
        print(Fore.GREEN + f"Clave reconstruida: {clave}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error reconstruyendo clave: {e}" + Style.RESET_ALL)

def enviar_archivo():
    print(Fore.YELLOW + "\n[Enviar archivo cifrado]" + Style.RESET_ALL)
    ruta_archivo = input("Ruta del archivo cifrado: ").strip()
    print("Método de envío: 1) Bluetooth 2) QR 3) USB")
    metodo = input("Seleccione método: ").strip()
    if not os.path.isfile(ruta_archivo):
        print(Fore.RED + "Archivo no encontrado." + Style.RESET_ALL)
        return
    datos = leer_archivo_binario(ruta_archivo)
    if datos is None:
        return
    if metodo == "1":
        direccion = input("Dirección Bluetooth del receptor (deje vacío para escanear): ").strip()
        if not direccion:
            dispositivos = transport.escanear_bluetooth()
            if dispositivos:
                print("Dispositivos encontrados:")
                for idx, (nombre, addr) in enumerate(dispositivos):
                    print(f"{idx+1}. {nombre} ({addr})")
                seleccion = input("Seleccione el número de dispositivo: ").strip()
                try:
                    idx = int(seleccion) - 1
                    direccion = dispositivos[idx][1]
                except Exception:
                    print(Fore.RED + "Selección inválida." + Style.RESET_ALL)
                    return
            else:
                print(Fore.RED + "No se encontraron dispositivos Bluetooth." + Style.RESET_ALL)
                return
        transport.enviar_bluetooth(datos, direccion)
    elif metodo == "2":
        ruta_qr = input("Ruta para guardar el código QR: ").strip()
        if not confirmar_sobrescritura(ruta_qr):
            return
        transport.generar_qr(datos, ruta_qr)
    elif metodo == "3":
        ruta_usb = input("Ruta de salida en USB: ").strip()
        if not confirmar_sobrescritura(ruta_usb):
            return
        escribir_archivo_binario(ruta_usb, datos)
        print(Fore.GREEN + f"Datos guardados en {ruta_usb}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Método no válido." + Style.RESET_ALL)

def recibir_archivo():
    print(Fore.YELLOW + "\n[Recibir archivo cifrado]" + Style.RESET_ALL)
    print("Método de recepción: 1) Bluetooth 2) QR 3) USB")
    metodo = input("Seleccione método: ").strip()
    if metodo == "1":
        direccion = input("Dirección Bluetooth del emisor (deje vacío para escanear): ").strip()
        if not direccion:
            dispositivos = transport.escanear_bluetooth()
            if dispositivos:
                print("Dispositivos encontrados:")
                for idx, (nombre, addr) in enumerate(dispositivos):
                    print(f"{idx+1}. {nombre} ({addr})")
                seleccion = input("Seleccione el número de dispositivo: ").strip()
                try:
                    idx = int(seleccion) - 1
                    direccion = dispositivos[idx][1]
                except Exception:
                    print(Fore.RED + "Selección inválida." + Style.RESET_ALL)
                    return
            else:
                print(Fore.RED + "No se encontraron dispositivos Bluetooth." + Style.RESET_ALL)
                return
        datos = transport.recibir_bluetooth(direccion)
    elif metodo == "2":
        ruta_qr = input("Ruta del código QR: ").strip()
        datos = transport.leer_qr(ruta_qr)
    elif metodo == "3":
        ruta_usb = input("Ruta del archivo en USB: ").strip()
        datos = leer_archivo_binario(ruta_usb)
    else:
        print(Fore.RED + "Método no válido." + Style.RESET_ALL)
        return
    ruta_salida = input("Ruta de salida para guardar el archivo recibido: ").strip()
    if not confirmar_sobrescritura(ruta_salida):
        return
    if not escribir_archivo_binario(ruta_salida, datos):
        return
    print(Fore.GREEN + f"Archivo recibido y guardado en {ruta_salida}" + Style.RESET_ALL)

def escanear_bluetooth():
    print(Fore.YELLOW + "\n[Escaneo de dispositivos Bluetooth]" + Style.RESET_ALL)
    dispositivos = transport.escanear_bluetooth()
    if dispositivos:
        print("Dispositivos encontrados:")
        for idx, (nombre, addr) in enumerate(dispositivos):
            print(f"{idx+1}. {nombre} ({addr})")
    else:
        print(Fore.RED + "No se encontraron dispositivos Bluetooth." + Style.RESET_ALL)

def verificar_tor():
    print(Fore.YELLOW + "\n[Verificación de disponibilidad de Tor]" + Style.RESET_ALL)
    disponible = transport.verificar_tor()
    if disponible:
        print(Fore.GREEN + "Tor está disponible y funcionando." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Tor no está disponible o no se pudo conectar." + Style.RESET_ALL)

def generar_claves():
    print(Fore.YELLOW + "\n[Generar par de claves RSA]" + Style.RESET_ALL)
    ruta_priv = input("Ruta para guardar la clave privada (PEM): ").strip()
    ruta_pub = input("Ruta para guardar la clave pública (PEM): ").strip()
    if not confirmar_sobrescritura(ruta_priv) or not confirmar_sobrescritura(ruta_pub):
        return
    try:
        priv, pub = crypto.generar_par_claves()
        with open(ruta_priv, 'wb') as f:
            f.write(priv)
        with open(ruta_pub, 'wb') as f:
            f.write(pub)
        print(Fore.GREEN + "Claves generadas y guardadas correctamente." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error generando claves: {e}" + Style.RESET_ALL)

def ver_log():
    print(Fore.YELLOW + "\n[Ver registro cifrado]" + Style.RESET_ALL)
    ruta_log = input("Ruta del registro cifrado: ").strip()
    password = input("Contraseña para descifrar el log: ").strip()
    try:
        contenido = log.leer_log(ruta_log, password)
        print(Fore.BLUE + contenido + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error leyendo log: {e}" + Style.RESET_ALL)

def enviar_p2p():
    print(Fore.YELLOW + "\n[Enviar archivo por P2P/Onion]" + Style.RESET_ALL)
    # Implementa usando transport.enviar_p2p o transport.enviar_onion según tu backend
    print(Fore.RED + "Funcionalidad P2P/Onion no implementada en este ejemplo." + Style.RESET_ALL)

def recibir_p2p():
    print(Fore.YELLOW + "\n[Recibir archivo por P2P/Onion]" + Style.RESET_ALL)
    # Implementa usando transport.recibir_p2p o transport.recibir_onion según tu backend
    print(Fore.RED + "Funcionalidad P2P/Onion no implementada en este ejemplo." + Style.RESET_ALL)

def validar_integridad():
    print(Fore.YELLOW + "\n[Validar integridad de archivo cifrado]" + Style.RESET_ALL)
    ruta_archivo = input("Ruta del archivo cifrado: ").strip()
    ruta_clave_priv = input("Ruta de la clave privada (PEM): ").strip()
    if not os.path.isfile(ruta_archivo) or not os.path.isfile(ruta_clave_priv):
        print(Fore.RED + "Archivo o clave no encontrados." + Style.RESET_ALL)
        return
    datos = leer_archivo_binario(ruta_archivo)
    pem = leer_archivo_binario(ruta_clave_priv)
    try:
        clave_priv = serialization.load_pem_private_key(pem, password=None)
        salt = datos[:16]
        clave_aes_cifrada = datos[16:16+256]
        firma = datos[16+256:16+256+32]
        cifrado = datos[16+256+32:]
        clave_aes = crypto.descifrar_con_privada(clave_priv, clave_aes_cifrada)
        if crypto.verificar_hmac(clave_aes, cifrado, firma):
            print(Fore.GREEN + "Integridad verificada correctamente." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Integridad NO verificada. El archivo puede estar dañado o manipulado." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error validando integridad: {e}" + Style.RESET_ALL)

if __name__ == "__main__":
    while True:
        opcion = menu()
        if opcion == "1":
            cifrar_archivo()
        elif opcion == "2":
            descifrar_archivo()
        elif opcion == "3":
            fragmentar_clave()
        elif opcion == "4":
            reconstruir_clave()
        elif opcion == "5":
            enviar_archivo()
        elif opcion == "6":
            recibir_archivo()
        elif opcion == "7":
            escanear_bluetooth()
        elif opcion == "8":
            verificar_tor()
        elif opcion == "9":
            generar_claves()
        elif opcion == "10":
            ver_log()
        elif opcion == "11":
            enviar_p2p()
        elif opcion == "12":
            recibir_p2p()
        elif opcion == "13":
            validar_integridad()
        elif opcion == "0":
            print("¡Hasta luego!")
            sys.exit(0)
        else:
            print("Opción no válida.")