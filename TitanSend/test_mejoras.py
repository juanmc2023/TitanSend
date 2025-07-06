"""
Test de Mejoras - TitanSend
============================

Prueba todas las mejoras implementadas:
- Shamir robusto
- Autenticación avanzada
- Fingerprints
- Firmas digitales
"""

import os
import sys
import time
from titansend import crypto, shamir_robusto, auth, shamir

def test_shamir_robusto():
    """Prueba la implementación robusta de Shamir."""
    print("🔒 Probando Shamir robusto...")
    
    # Datos de prueba
    secreto = "Mi secreto ultra seguro para producción"
    
    try:
        # Fragmentar
        fragmentos = shamir_robusto.fragmentar_clave_robusto(secreto, 5, 3)
        print(f"✅ Fragmentos generados: {len(fragmentos)}")
        
        # Verificar formato
        for i, frag in enumerate(fragmentos):
            if not shamir_robusto.verificar_fragmento_robusto(frag):
                print(f"❌ Fragmento {i} inválido")
                return False
        
        # Reconstruir con 3 fragmentos
        fragmentos_parciales = fragmentos[:3]
        reconstruido = shamir_robusto.reconstruir_clave_robusto(fragmentos_parciales)
        
        if reconstruido == secreto:
            print("✅ Reconstrucción exitosa con 3 fragmentos")
        else:
            print("❌ Error en reconstrucción")
            return False
        
        # Probar con diferentes fragmentos
        fragmentos_alternativos = [fragmentos[0], fragmentos[2], fragmentos[4]]
        reconstruido_alt = shamir_robusto.reconstruir_clave_robusto(fragmentos_alternativos)
        
        if reconstruido_alt == secreto:
            print("✅ Reconstrucción exitosa con fragmentos alternativos")
        else:
            print("❌ Error en reconstrucción alternativa")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test Shamir robusto: {e}")
        return False

def test_autenticacion_avanzada():
    """Prueba las funciones de autenticación avanzada."""
    print("🔐 Probando autenticación avanzada...")
    
    try:
        # Generar claves RSA
        clave_priv, clave_pub = crypto.generar_claves_rsa()
        
        # Generar fingerprints
        fingerprint = auth.generar_fingerprint_clave(clave_pub)
        fingerprint_visual = auth.generar_fingerprint_visual(clave_pub)
        
        print(f"✅ Fingerprint: {fingerprint}")
        print(f"✅ Fingerprint visual: {fingerprint_visual}")
        
        # Datos de prueba
        datos = b"Archivo de prueba para firma digital"
        
        # Firmar archivo
        firma = auth.firmar_archivo(datos, clave_priv)
        print(f"✅ Firma generada: {len(firma)} bytes")
        
        # Verificar firma
        if auth.verificar_firma_archivo(datos, firma, clave_pub):
            print("✅ Verificación de firma exitosa")
        else:
            print("❌ Error en verificación de firma")
            return False
        
        # Probar con datos modificados
        datos_modificados = b"Archivo modificado para firma digital"
        if not auth.verificar_firma_archivo(datos_modificados, firma, clave_pub):
            print("✅ Detección de manipulación exitosa")
        else:
            print("❌ No se detectó manipulación")
            return False
        
        # Generar certificado
        certificado = auth.generar_certificado_simple(clave_pub, "Usuario Test")
        print(f"✅ Certificado generado: {certificado['usuario']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test autenticación: {e}")
        return False

def test_cifrado_mejorado():
    """Prueba el cifrado con autenticación mejorada."""
    print("🔒 Probando cifrado mejorado...")
    
    try:
        # Generar claves
        clave_priv, clave_pub = crypto.generar_claves_rsa()
        
        # Datos de prueba
        datos_originales = b"Archivo secreto con autenticacion avanzada"
        
        # Cifrar con firma
        password = "miclaveultrasecreta"
        salt = os.urandom(16)
        clave_aes = crypto.generar_clave_aes(password, salt)
        
        timestamp = int(time.time()).to_bytes(8, 'big')
        nonce = os.urandom(8)
        datos_a_cifrar = timestamp + nonce + datos_originales
        
        cifrado = crypto.cifrar_aes(datos_a_cifrar, clave_aes)
        firma = crypto.firmar_hmac(clave_aes, cifrado)
        clave_aes_cifrada = crypto.cifrar_con_publica(clave_pub, clave_aes)
        
        resultado = salt + clave_aes_cifrada + firma + cifrado
        
        # Guardar archivo cifrado
        with open("test_cifrado_mejorado.bin", "wb") as f:
            f.write(resultado)
        
        # Descifrar
        salt2 = resultado[:16]
        clave_aes_cifrada2 = resultado[16:16+256]
        firma2 = resultado[16+256:16+256+32]
        cifrado2 = resultado[16+256+32:]
        
        clave_aes2 = crypto.descifrar_con_privada(clave_priv, clave_aes_cifrada2)
        
        if not crypto.verificar_hmac(clave_aes2, cifrado2, firma2):
            print("❌ Verificación HMAC falló")
            return False
        
        descifrado = crypto.descifrar_aes(cifrado2, clave_aes2)
        datos_final = descifrado[16:]
        
        if datos_final == datos_originales:
            print("✅ Cifrado/descifrado con autenticación exitoso")
        else:
            print("❌ Error en cifrado/descifrado")
            return False
        
        # Limpiar archivo de prueba
        os.remove("test_cifrado_mejorado.bin")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test cifrado mejorado: {e}")
        return False

def test_compatibilidad():
    """Prueba la compatibilidad con la implementación anterior."""
    print("🔄 Probando compatibilidad...")
    
    try:
        # Usar implementación anterior
        clave = "clave_test"
        partes_viejas = shamir.fragmentar_clave(clave, 3, 2)
        reconstruida_vieja = shamir.reconstruir_clave(partes_viejas[:2])
        
        if reconstruida_vieja == clave:
            print("✅ Implementación anterior funciona")
        else:
            print("❌ Error en implementación anterior")
            return False
        
        # Usar implementación nueva
        partes_nuevas = shamir_robusto.fragmentar_clave_robusto(clave, 3, 2)
        reconstruida_nueva = shamir_robusto.reconstruir_clave_robusto(partes_nuevas[:2])
        
        if reconstruida_nueva == clave:
            print("✅ Implementación nueva funciona")
        else:
            print("❌ Error en implementación nueva")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test compatibilidad: {e}")
        return False

def main():
    """Ejecuta todas las pruebas."""
    print("🧪 INICIANDO TESTS DE MEJORAS - TITANSEND")
    print("="*60)
    
    tests = [
        ("Shamir Robusto", test_shamir_robusto),
        ("Autenticación Avanzada", test_autenticacion_avanzada),
        ("Cifrado Mejorado", test_cifrado_mejorado),
        ("Compatibilidad", test_compatibilidad)
    ]
    
    resultados = {}
    
    for nombre, test_func in tests:
        print(f"\n🔍 {nombre}")
        print("-" * 40)
        
        try:
            resultado = test_func()
            resultados[nombre] = resultado
            
            if resultado:
                print(f"✅ {nombre}: PASÓ")
            else:
                print(f"❌ {nombre}: FALLÓ")
                
        except Exception as e:
            print(f"❌ {nombre}: ERROR - {e}")
            resultados[nombre] = False
    
    # Resumen
    print(f"\n📊 RESUMEN DE TESTS")
    print("="*60)
    
    pasados = sum(1 for r in resultados.values() if r)
    total = len(resultados)
    
    for nombre, resultado in resultados.items():
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"  {nombre}: {estado}")
    
    print(f"\n🎯 Resultado: {pasados}/{total} tests pasaron")
    
    if pasados == total:
        print("🎉 ¡Todas las mejoras funcionan correctamente!")
        return True
    else:
        print("⚠️  Algunos tests fallaron. Revisa los errores.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 