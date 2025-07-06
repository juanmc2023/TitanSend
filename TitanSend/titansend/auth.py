"""
Autenticación Avanzada para TitanSend
=====================================

Proporciona funciones para:
- Fingerprints de claves públicas
- Firmas digitales de archivos
- Verificación de identidad entre emisor y receptor
- Protección contra ataques MitM
"""

import hashlib
import hmac
import os
import time
import base64
from typing import Dict, Optional, Tuple
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ed25519
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

class AutenticadorAvanzado:
    """
    Clase para manejar autenticación avanzada y verificación de identidad.
    """
    
    def __init__(self):
        self.algoritmo_hash = hashes.SHA256()
        self.algoritmo_hmac = hashes.SHA256()
    
    def generar_fingerprint_clave(self, clave_publica) -> str:
        """
        Genera un fingerprint de una clave pública para identificación visual.
        
        Args:
            clave_publica: Clave pública RSA o Ed25519
            
        Returns:
            Fingerprint en formato hexadecimal
        """
        # Serializar la clave pública
        if hasattr(clave_publica, 'public_bytes'):
            datos_clave = clave_publica.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        else:
            raise ValueError("Clave pública inválida")
        
        # Generar hash SHA256
        hash_obj = hashlib.sha256(datos_clave)
        fingerprint = hash_obj.hexdigest()
        
        return fingerprint
    
    def generar_fingerprint_visual(self, clave_publica) -> str:
        """
        Genera un fingerprint visual (formato similar a SSH).
        
        Args:
            clave_publica: Clave pública
            
        Returns:
            Fingerprint en formato visual (ej: "12:34:56:78:9a:bc:de:f0")
        """
        fingerprint_hex = self.generar_fingerprint_clave(clave_publica)
        
        # Convertir a formato visual
        bytes_fingerprint = bytes.fromhex(fingerprint_hex)
        visual_parts = []
        
        for i in range(0, len(bytes_fingerprint), 2):
            if i + 1 < len(bytes_fingerprint):
                visual_parts.append(f"{bytes_fingerprint[i]:02x}:{bytes_fingerprint[i+1]:02x}")
            else:
                visual_parts.append(f"{bytes_fingerprint[i]:02x}")
        
        return ":".join(visual_parts)
    
    def firmar_archivo(self, datos: bytes, clave_privada) -> bytes:
        """
        Firma digitalmente un archivo usando la clave privada.
        
        Args:
            datos: Datos a firmar
            clave_privada: Clave privada RSA
            
        Returns:
            Firma digital en bytes
        """
        if not hasattr(clave_privada, 'sign'):
            raise ValueError("Clave privada inválida")
        
        # Generar hash de los datos
        hash_obj = hashlib.sha256(datos)
        hash_datos = hash_obj.digest()
        
        # Firmar el hash
        firma = clave_privada.sign(
            hash_datos,
            padding.PSS(
                mgf=padding.MGF1(self.algoritmo_hash),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            self.algoritmo_hash
        )
        
        return firma
    
    def verificar_firma_archivo(self, datos: bytes, firma: bytes, clave_publica) -> bool:
        """
        Verifica la firma digital de un archivo.
        
        Args:
            datos: Datos originales
            firma: Firma digital
            clave_publica: Clave pública RSA
            
        Returns:
            True si la firma es válida, False en caso contrario
        """
        if not hasattr(clave_publica, 'verify'):
            raise ValueError("Clave pública inválida")
        
        try:
            # Generar hash de los datos
            hash_obj = hashlib.sha256(datos)
            hash_datos = hash_obj.digest()
            
            # Verificar la firma
            clave_publica.verify(
                firma,
                hash_datos,
                padding.PSS(
                    mgf=padding.MGF1(self.algoritmo_hash),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                self.algoritmo_hash
            )
            return True
        except InvalidSignature:
            return False
    
    def generar_challenge_response(self, clave_publica_receptor, clave_privada_emisor) -> Tuple[str, str]:
        """
        Genera un challenge-response para verificar identidad.
        
        Args:
            clave_publica_receptor: Clave pública del receptor
            clave_privada_emisor: Clave privada del emisor
            
        Returns:
            Tupla (challenge, response)
        """
        # Generar challenge aleatorio
        challenge = os.urandom(32)
        challenge_b64 = base64.b64encode(challenge).decode('utf-8')
        
        # Firmar el challenge
        firma = self.firmar_archivo(challenge, clave_privada_emisor)
        response_b64 = base64.b64encode(firma).decode('utf-8')
        
        return challenge_b64, response_b64
    
    def verificar_challenge_response(self, challenge: str, response: str, 
                                  clave_publica_emisor) -> bool:
        """
        Verifica un challenge-response.
        
        Args:
            challenge: Challenge en base64
            response: Response en base64
            clave_publica_emisor: Clave pública del emisor
            
        Returns:
            True si la verificación es exitosa
        """
        try:
            challenge_bytes = base64.b64decode(challenge)
            response_bytes = base64.b64decode(response)
            
            return self.verificar_firma_archivo(challenge_bytes, response_bytes, clave_publica_emisor)
        except Exception:
            return False
    
    def generar_verificacion_mitm(self, clave_publica_emisor: bytes, 
                                 clave_publica_receptor: bytes) -> str:
        """
        Genera una verificación para prevenir ataques MitM.
        
        Args:
            clave_publica_emisor: Clave pública del emisor
            clave_publica_receptor: Clave pública del receptor
            
        Returns:
            Hash de verificación
        """
        # Combinar ambas claves públicas
        datos_combinados = clave_publica_emisor + clave_publica_receptor
        
        # Generar hash
        hash_obj = hashlib.sha256(datos_combinados)
        return hash_obj.hexdigest()
    
    def verificar_identidad_manual(self, fingerprint_esperado: str, 
                                 fingerprint_recibido: str) -> bool:
        """
        Verificación manual de identidad (para uso humano).
        
        Args:
            fingerprint_esperado: Fingerprint que se espera
            fingerprint_recibido: Fingerprint recibido
            
        Returns:
            True si coinciden
        """
        return fingerprint_esperado.lower() == fingerprint_recibido.lower()
    
    def generar_certificado_simple(self, clave_publica, nombre_usuario: str) -> Dict:
        """
        Genera un certificado simple para identificación.
        
        Args:
            clave_publica: Clave pública
            nombre_usuario: Nombre del usuario
            
        Returns:
            Certificado en formato diccionario
        """
        fingerprint = self.generar_fingerprint_clave(clave_publica)
        fingerprint_visual = self.generar_fingerprint_visual(clave_publica)
        
        certificado = {
            "usuario": nombre_usuario,
            "fingerprint": fingerprint,
            "fingerprint_visual": fingerprint_visual,
            "algoritmo": "RSA-2048" if hasattr(clave_publica, 'key_size') else "Ed25519",
            "fecha_generacion": str(int(time.time())),
            "version": "1.0"
        }
        
        return certificado

# Funciones de conveniencia
def generar_fingerprint_clave(clave_publica) -> str:
    """Genera fingerprint de una clave pública."""
    auth = AutenticadorAvanzado()
    return auth.generar_fingerprint_clave(clave_publica)

def generar_fingerprint_visual(clave_publica) -> str:
    """Genera fingerprint visual de una clave pública."""
    auth = AutenticadorAvanzado()
    return auth.generar_fingerprint_visual(clave_publica)

def firmar_archivo(datos: bytes, clave_privada) -> bytes:
    """Firma digitalmente un archivo."""
    auth = AutenticadorAvanzado()
    return auth.firmar_archivo(datos, clave_privada)

def verificar_firma_archivo(datos: bytes, firma: bytes, clave_publica) -> bool:
    """Verifica la firma digital de un archivo."""
    auth = AutenticadorAvanzado()
    return auth.verificar_firma_archivo(datos, firma, clave_publica)

def generar_certificado_simple(clave_publica, nombre_usuario: str) -> Dict:
    """Genera un certificado simple para identificación."""
    auth = AutenticadorAvanzado()
    return auth.generar_certificado_simple(clave_publica, nombre_usuario) 