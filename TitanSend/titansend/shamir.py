import random
import functools
import operator
import warnings

# =========================
# ADVERTENCIA: SOLO DEMO
# =========================
# Esta implementación de Shamir es solo para DEMOSTRACIÓN.
# NO USAR en producción ni para proteger información real.
# Usa un campo finito pequeño (PRIME=257) y solo soporta claves cortas.
# Para producción, usa una librería robusta como 'secretsharing' o 'sss'.

PRIME = 257  # Campo finito pequeño, solo para demo

def _eval_poly(poly, x):
    """Evalúa un polinomio en x sobre el campo PRIME."""
    res = 0
    for coef in reversed(poly):
        res = (res * x + coef) % PRIME
    # Asegurar que el resultado esté en el rango válido para bytes
    return res % 256

def fragmentar_clave(clave: str, n: int, k: int):
    """
    Fragmenta una clave en n partes, de las cuales k son necesarias para reconstruirla.
    Solo para DEMO. No usar para datos reales.
    """
    if k > n:
        raise ValueError("El umbral k no puede ser mayor que el número de fragmentos n")
    b = clave.encode()
    if len(b) > 32:
        raise ValueError('Clave muy larga para demo (máx 32 bytes)')
    warnings.warn("¡Esta implementación de Shamir es solo para DEMO! No usar en producción.", UserWarning)
    partes = []
    for byte in b:
        # Genera polinomio aleatorio de grado k-1
        coefs = [byte] + [random.randint(0, PRIME-1) for _ in range(k-1)]
        puntos = [(i, _eval_poly(coefs, i)) for i in range(1, n+1)]
        partes.append(puntos)
    # Serializa cada parte
    partes_serializadas = []
    for i in range(n):
        parte = bytes([p[i][1] for p in partes])
        partes_serializadas.append(parte.hex())
    return partes_serializadas

def reconstruir_clave(fragmentos):
    """
    Reconstruye la clave original a partir de fragmentos (mínimo k).
    Solo para DEMO. No usar para datos reales.
    """
    warnings.warn("¡Esta implementación de Shamir es solo para DEMO! No usar en producción.", UserWarning)
    n = len(fragmentos)
    b_partes = [bytes.fromhex(f) for f in fragmentos]
    longitud = len(b_partes[0])
    clave_bytes = bytearray()
    for idx in range(longitud):
        puntos = [(i+1, b_partes[i][idx]) for i in range(n)]
        # Lagrange interpolation en x=0
        total = 0
        for j, (xj, yj) in enumerate(puntos):
            num = den = 1
            for m, (xm, _) in enumerate(puntos):
                if m != j:
                    num = (num * (-xm)) % PRIME
                    den = (den * (xj - xm)) % PRIME
            lagrange = num * pow(den, -1, PRIME)
            total = (total + yj * lagrange) % PRIME
        clave_bytes.append(total)
    try:
        return clave_bytes.decode(errors='strict')
    except UnicodeDecodeError:
        return clave_bytes.decode(errors='ignore')

def es_fragmento_valido(fragmento):
    """
    Verifica si un fragmento tiene el formato esperado (hex y longitud razonable).
    """
    try:
        b = bytes.fromhex(fragmento)
        return 1 <= len(b) <= 32
    except Exception:
        return False

def advertencia_produccion():
    """
    Imprime una advertencia clara para el usuario.
    """
    print("⚠️  ADVERTENCIA: Esta implementación de Shamir es solo para DEMO y NO es segura para producción.")
    print("   Usa una librería robusta como 'secretsharing' o 'sss' para datos reales.")