import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes, aead
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.exceptions import InvalidSignature

# =========================
# Constantes de seguridad
# =========================
AES_KEY_SIZE = 32
AES_IV_SIZE = 16
AES_GCM_NONCE_SIZE = 12
PBKDF2_ITER = 100_000
RSA_MIN_BITS = 2048

# =========================
# Generación y manejo de claves RSA
# =========================

def generar_claves_rsa(bits=RSA_MIN_BITS):
    """
    Genera un par de claves RSA.
    :param bits: Tamaño de la clave en bits (2048 o 4096 recomendado)
    :return: (clave_privada, clave_publica)
    """
    if bits < RSA_MIN_BITS:
        raise ValueError(f"El tamaño mínimo recomendado para RSA es {RSA_MIN_BITS} bits")
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
        backend=default_backend()
    )
    clave_publica = clave_privada.public_key()
    return clave_privada, clave_publica

def serializar_clave_publica(clave_publica):
    """
    Serializa una clave pública RSA a formato PEM.
    """
    return clave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def serializar_clave_privada(clave_privada, password=None):
    """
    Serializa una clave privada RSA a formato PEM.
    Si se provee password, la clave se cifra.
    """
    encryption = serialization.BestAvailableEncryption(password.encode()) if password else serialization.NoEncryption()
    return clave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
    )

def deserializar_clave_publica(pem):
    """
    Deserializa una clave pública RSA desde PEM.
    """
    clave = serialization.load_pem_public_key(pem, backend=default_backend())
    validar_tamano_clave_rsa(clave)
    return clave

def deserializar_clave_privada(pem, password=None):
    """
    Deserializa una clave privada RSA desde PEM.
    """
    clave = serialization.load_pem_private_key(pem, password=password, backend=default_backend())
    validar_tamano_clave_rsa(clave)
    return clave

# =========================
# Cifrado/descifrado asimétrico (RSA)
# =========================

def cifrar_con_publica(clave_publica, datos):
    """
    Cifra datos con una clave pública RSA usando OAEP+SHA256.
    """
    if not hasattr(clave_publica, "encrypt"):
        raise ValueError("Clave pública inválida")
    validar_tamano_clave_rsa(clave_publica)
    return clave_publica.encrypt(
        datos,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def descifrar_con_privada(clave_privada, datos):
    """
    Descifra datos con una clave privada RSA usando OAEP+SHA256.
    """
    if not hasattr(clave_privada, "decrypt"):
        raise ValueError("Clave privada inválida")
    validar_tamano_clave_rsa(clave_privada)
    return clave_privada.decrypt(
        datos,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

# =========================
# Derivación de clave AES desde contraseña
# =========================

def generar_clave_aes(password, salt, iteraciones=PBKDF2_ITER):
    """
    Deriva una clave AES-256 desde una contraseña y un salt usando PBKDF2-HMAC-SHA256.
    :param password: Contraseña (str)
    :param salt: Salt (bytes)
    :param iteraciones: Número de iteraciones PBKDF2 (por defecto 100000)
    :return: clave AES (bytes)
    """
    if not isinstance(password, str) or not isinstance(salt, bytes):
        raise ValueError("Password debe ser str y salt debe ser bytes")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=salt,
        iterations=iteraciones,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def generar_clave_aes_aleatoria():
    """
    Genera una clave AES-256 aleatoria.
    """
    return os.urandom(AES_KEY_SIZE)

# =========================
# Cifrado/descifrado simétrico (AES-CFB)
# =========================

def cifrar_aes(datos, clave):
    """
    Cifra datos con AES-256-CFB. Devuelve IV + datos cifrados.
    """
    if not isinstance(clave, bytes) or len(clave) != AES_KEY_SIZE:
        raise ValueError("La clave AES debe ser de 32 bytes (256 bits)")
    iv = os.urandom(AES_IV_SIZE)
    cipher = Cipher(algorithms.AES(clave), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    cifrado = encryptor.update(datos) + encryptor.finalize()
    return iv + cifrado

def descifrar_aes(datos, clave):
    """
    Descifra datos cifrados con AES-256-CFB (IV + cifrado).
    """
    if not isinstance(clave, bytes) or len(clave) != AES_KEY_SIZE:
        raise ValueError("La clave AES debe ser de 32 bytes (256 bits)")
    if len(datos) < AES_IV_SIZE:
        raise ValueError("Datos demasiado cortos para contener IV")
    iv = datos[:AES_IV_SIZE]
    cifrado = datos[AES_IV_SIZE:]
    cipher = Cipher(algorithms.AES(clave), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(cifrado) + decryptor.finalize()

# =========================
# Cifrado/descifrado simétrico (AES-GCM)
# =========================

def cifrar_aes_gcm(datos, clave):
    """
    Cifra datos con AES-256-GCM. Devuelve nonce + datos cifrados + tag.
    """
    if not isinstance(clave, bytes) or len(clave) != AES_KEY_SIZE:
        raise ValueError("La clave AES debe ser de 32 bytes (256 bits)")
    nonce = os.urandom(AES_GCM_NONCE_SIZE)
    aesgcm = aead.AESGCM(clave)
    cifrado = aesgcm.encrypt(nonce, datos, None)
    return nonce + cifrado

def descifrar_aes_gcm(datos, clave):
    """
    Descifra datos cifrados con AES-256-GCM (nonce + cifrado + tag).
    """
    if not isinstance(clave, bytes) or len(clave) != AES_KEY_SIZE:
        raise ValueError("La clave AES debe ser de 32 bytes (256 bits)")
    if len(datos) < AES_GCM_NONCE_SIZE:
        raise ValueError("Datos demasiado cortos para contener nonce")
    nonce = datos[:AES_GCM_NONCE_SIZE]
    cifrado = datos[AES_GCM_NONCE_SIZE:]
    aesgcm = aead.AESGCM(clave)
    return aesgcm.decrypt(nonce, cifrado, None)

# =========================
# HMAC para integridad/autenticidad
# =========================

def firmar_hmac(clave, datos):
    """
    Genera una firma HMAC-SHA256 de los datos usando la clave dada.
    """
    if not isinstance(clave, bytes):
        raise ValueError("La clave HMAC debe ser bytes")
    hmac = HMAC(clave, hashes.SHA256(), backend=default_backend())
    hmac.update(datos)
    return hmac.finalize()

def verificar_hmac(clave, datos, firma):
    """
    Verifica una firma HMAC-SHA256.
    """
    if not isinstance(clave, bytes):
        raise ValueError("La clave HMAC debe ser bytes")
    hmac = HMAC(clave, hashes.SHA256(), backend=default_backend())
    hmac.update(datos)
    try:
        hmac.verify(firma)
        return True
    except InvalidSignature:
        return False

# =========================
# Utilidades adicionales
# =========================

def validar_tamano_clave_rsa(clave):
    """
    Valida que la clave RSA tenga al menos 2048 bits.
    """
    if hasattr(clave, "key_size") and clave.key_size < RSA_MIN_BITS:
        raise ValueError(f"La clave RSA debe ser de al menos {RSA_MIN_BITS} bits")

def obtener_info_clave(clave):
    """
    Devuelve información básica de la clave (tipo, tamaño).
    """
    if hasattr(clave, "key_size"):
        return f"RSA {clave.key_size} bits"
    return str(type(clave))

# =========================
# NOTA: Para máxima seguridad, se recomienda usar AES-GCM.
# Puedes elegir entre cifrar_aes/cifrar_aes_gcm y descifrar_aes/descifrar_aes_gcm según el caso de uso.