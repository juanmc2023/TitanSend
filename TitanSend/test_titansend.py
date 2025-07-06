import os
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'titansend'))
from titansend import crypto, shamir
from cryptography.hazmat.primitives import serialization

def test_titansend():
    print('--- Prueba automática TitanSend ---')
    # 1. Generar claves RSA
    priv, pub = crypto.generar_claves_rsa()
    with open('privada_test.pem', 'wb') as f:
        f.write(priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open('publica_test.pem', 'wb') as f:
        f.write(pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print('Claves RSA generadas.')

    # 2. Crear archivo de texto
    original = 'Mensaje ultra secreto de TitanSend\n'
    with open('secreto_test.txt', 'w') as f:
        f.write(original)
    print('Archivo de prueba creado.')

    # 3. Cifrar el archivo
    with open('secreto_test.txt', 'rb') as f:
        datos = f.read()
    with open('publica_test.pem', 'rb') as f:
        pem = f.read()
    salt = os.urandom(16)
    password = 'miclaveultrasecreta'
    clave_pub = crypto.deserializar_clave_publica(pem)
    clave_aes = crypto.generar_clave_aes(password, salt)
    import time
    timestamp = int(time.time()).to_bytes(8, 'big')
    nonce = os.urandom(8)
    datos_a_cifrar = timestamp + nonce + datos
    cifrado = crypto.cifrar_aes(datos_a_cifrar, clave_aes)
    firma = crypto.firmar_hmac(clave_aes, cifrado)
    clave_aes_cifrada = crypto.cifrar_con_publica(clave_pub, clave_aes)
    resultado = salt + clave_aes_cifrada + firma + cifrado
    with open('secreto_cifrado_test.bin', 'wb') as f:
        f.write(resultado)
    print('Archivo cifrado.')

    # 4. Descifrar el archivo
    with open('secreto_cifrado_test.bin', 'rb') as f:
        datos_c = f.read()
    with open('privada_test.pem', 'rb') as f:
        pem_priv = f.read()
    salt2 = datos_c[:16]
    clave_priv = serialization.load_pem_private_key(pem_priv, password=None)
    clave_aes_cifrada2 = datos_c[16:16+256]
    firma2 = datos_c[16+256:16+256+32]
    cifrado2 = datos_c[16+256+32:]
    clave_aes2 = crypto.descifrar_con_privada(clave_priv, clave_aes_cifrada2)
    assert crypto.verificar_hmac(clave_aes2, cifrado2, firma2), 'HMAC inválido!'
    descifrado = crypto.descifrar_aes(cifrado2, clave_aes2)
    print('DEBUG: descifrado (bytes):', descifrado)
    print('DEBUG: descifrado[:8] (timestamp):', descifrado[:8])
    print('DEBUG: descifrado[8:16] (nonce):', descifrado[8:16])
    print('DEBUG: descifrado[16:] (datos):', descifrado[16:])
    print('DEBUG: original (bytes):', datos)
    datos_final = descifrado[16:]
    with open('secreto_descifrado_test.txt', 'wb') as f:
        f.write(datos_final)
    print('Archivo descifrado.')

    # 5. Verificar que el contenido coincide
    with open('secreto_descifrado_test.txt', 'rb') as f:
        recuperado = f.read().decode()
    print('DEBUG: recuperado:', recuperado)
    print('DEBUG: original:', original)
    # Comparar ignorando diferencias de salto de línea
    assert recuperado.replace('\r\n', '\n') == original.replace('\r\n', '\n'), '¡El archivo descifrado NO coincide con el original!'
    print('Verificación OK: El archivo descifrado es idéntico al original.')

    # 6. Fragmentar y reconstruir la clave
    partes = shamir.fragmentar_clave(password, 3, 2)
    print('Fragmentos:', partes)
    reconstruida = shamir.reconstruir_clave(partes[:2])
    assert reconstruida == password, '¡La clave reconstruida NO coincide!'
    print('Fragmentación y reconstrucción de clave OK.')

    print('--- Prueba automática finalizada con éxito ---')

if __name__ == '__main__':
    test_titansend()
    print('\n--- Ejecutando tests de transporte Tor y P2P ---')
    import subprocess
    r1 = subprocess.run(['python', '-m', 'unittest', 'titansend/test_unit_transport_tor.py'], capture_output=True, text=True)
    print('Test Tor:')
    print(r1.stdout)
    if r1.stderr:
        print('STDERR:', r1.stderr)
    r2 = subprocess.run(['python', '-m', 'unittest', 'titansend/test_unit_transport_p2p.py'], capture_output=True, text=True)
    print('Test P2P:')
    print(r2.stdout)
    if r2.stderr:
        print('STDERR:', r2.stderr) 