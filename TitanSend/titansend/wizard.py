"""
Asistente para Principiantes - TitanSend
=======================================

Wizard interactivo que guía al usuario paso a paso en el proceso de:
- Cifrado de archivos
- Selección de método de transporte
- Descifrado de archivos
- Verificación de identidad
"""

import os
import sys
from typing import Optional, Dict, List
from colorama import Fore, Style, init
from . import crypto, auth, transport

# Inicializar colorama para colores en terminal
init(autoreset=True)

class TitanSendWizard:
    """
    Asistente interactivo para principiantes.
    """
    
    def __init__(self):
        self.pasos_completados = []
        self.configuracion_actual = {}
        
    def mostrar_bienvenida(self):
        """Muestra la pantalla de bienvenida."""
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}    🛡️  TitanSend - Tu Búnker Digital Portátil")
        print(f"{Fore.CYAN}    Asistente para Principiantes")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print()
        print("¡Bienvenido a TitanSend! Este asistente te guiará paso a paso")
        print("para cifrar y transferir archivos de forma segura.")
        print()
        print("¿Qué quieres hacer?")
        print("1. 🔒 Cifrar un archivo para enviar")
        print("2. 🔓 Descifrar un archivo recibido")
        print("3. 📚 Aprender sobre TitanSend")
        print("4. ⚙️  Configurar opciones avanzadas")
        print("5. 🚪 Salir")
        print()
        
        while True:
            opcion = input("Selecciona una opción (1-5): ").strip()
            if opcion in ['1', '2', '3', '4', '5']:
                return opcion
            else:
                print(f"{Fore.RED}❌ Opción inválida. Por favor selecciona 1-5.{Style.RESET_ALL}")
    
    def wizard_cifrado(self):
        """Guía al usuario en el proceso de cifrado."""
        print(f"\n{Fore.YELLOW}🔒 PASO 1: Seleccionar archivo a cifrar{Style.RESET_ALL}")
        print("="*50)
        
        # Paso 1: Seleccionar archivo
        archivo_origen = self._seleccionar_archivo("archivo a cifrar")
        if not archivo_origen:
            return
        
        self.configuracion_actual['archivo_origen'] = archivo_origen
        
        # Paso 2: Generar o seleccionar claves
        print(f"\n{Fore.YELLOW}🔑 PASO 2: Configurar claves de cifrado{Style.RESET_ALL}")
        print("="*50)
        
        if not self._configurar_claves():
            return
        
        # Paso 3: Seleccionar método de transporte
        print(f"\n{Fore.YELLOW}📤 PASO 3: Seleccionar método de envío{Style.RESET_ALL}")
        print("="*50)
        
        metodo_transporte = self._seleccionar_transporte()
        if not metodo_transporte:
            return
        
        self.configuracion_actual['metodo_transporte'] = metodo_transporte
        
        # Paso 4: Cifrar archivo
        print(f"\n{Fore.YELLOW}🔒 PASO 4: Cifrando archivo{Style.RESET_ALL}")
        print("="*50)
        
        if self._cifrar_archivo():
            print(f"{Fore.GREEN}✅ ¡Archivo cifrado exitosamente!{Style.RESET_ALL}")
            self._mostrar_instrucciones_envio()
        else:
            print(f"{Fore.RED}❌ Error al cifrar el archivo.{Style.RESET_ALL}")
    
    def wizard_descifrado(self):
        """Guía al usuario en el proceso de descifrado."""
        print(f"\n{Fore.YELLOW}🔓 PASO 1: Seleccionar archivo cifrado{Style.RESET_ALL}")
        print("="*50)
        
        # Paso 1: Seleccionar archivo cifrado
        archivo_cifrado = self._seleccionar_archivo("archivo cifrado", extensiones=['.bin', '.enc'])
        if not archivo_cifrado:
            return
        
        # Paso 2: Seleccionar clave privada
        print(f"\n{Fore.YELLOW}🔑 PASO 2: Seleccionar clave privada{Style.RESET_ALL}")
        print("="*50)
        
        clave_privada = self._seleccionar_clave_privada()
        if not clave_privada:
            return
        
        # Paso 3: Descifrar archivo
        print(f"\n{Fore.YELLOW}🔓 PASO 3: Descifrando archivo{Style.RESET_ALL}")
        print("="*50)
        
        if self._descifrar_archivo(archivo_cifrado, clave_privada):
            print(f"{Fore.GREEN}✅ ¡Archivo descifrado exitosamente!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Error al descifrar el archivo.{Style.RESET_ALL}")
    
    def _seleccionar_archivo(self, descripcion: str, extensiones: List[str] = None) -> Optional[str]:
        """Ayuda al usuario a seleccionar un archivo."""
        print(f"Por favor, ingresa la ruta del {descripcion}:")
        
        while True:
            ruta = input("Ruta del archivo: ").strip()
            
            if not ruta:
                print(f"{Fore.YELLOW}💡 Sugerencia: Puedes arrastrar el archivo aquí desde el explorador.{Style.RESET_ALL}")
                continue
            
            # Limpiar ruta si viene con comillas
            ruta = ruta.strip('"').strip("'")
            
            if not os.path.exists(ruta):
                print(f"{Fore.RED}❌ El archivo no existe. Verifica la ruta.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}💡 Sugerencia: Asegúrate de estar en la carpeta correcta.{Style.RESET_ALL}")
                continue
            
            if not os.path.isfile(ruta):
                print(f"{Fore.RED}❌ La ruta no es un archivo válido.{Style.RESET_ALL}")
                continue
            
            if extensiones:
                extension = os.path.splitext(ruta)[1].lower()
                if extension not in extensiones:
                    print(f"{Fore.YELLOW}⚠️  El archivo no tiene una extensión esperada ({', '.join(extensiones)}){Style.RESET_ALL}")
                    confirmar = input("¿Continuar de todas formas? (s/n): ").strip().lower()
                    if confirmar != 's':
                        continue
            
            # Mostrar información del archivo
            tamaño = os.path.getsize(ruta)
            print(f"{Fore.GREEN}✅ Archivo seleccionado: {ruta}")
            print(f"   Tamaño: {self._formatear_tamaño(tamaño)}{Style.RESET_ALL}")
            
            return ruta
    
    def _configurar_claves(self) -> bool:
        """Ayuda al usuario a configurar las claves."""
        print("¿Tienes ya un par de claves RSA?")
        print("1. Sí, tengo claves existentes")
        print("2. No, generar nuevas claves")
        print("3. No sé qué son las claves (explicar)")
        
        while True:
            opcion = input("Selecciona una opción (1-3): ").strip()
            
            if opcion == '1':
                return self._seleccionar_claves_existentes()
            elif opcion == '2':
                return self._generar_nuevas_claves()
            elif opcion == '3':
                self._explicar_claves()
                continue
            else:
                print(f"{Fore.RED}❌ Opción inválida.{Style.RESET_ALL}")
    
    def _explicar_claves(self):
        """Explica qué son las claves RSA."""
        print(f"\n{Fore.CYAN}📚 ¿Qué son las claves RSA?{Style.RESET_ALL}")
        print("Las claves RSA son como un candado digital:")
        print("• La CLAVE PÚBLICA es como el candado abierto - cualquiera puede usarla")
        print("• La CLAVE PRIVADA es como la llave - solo tú la tienes")
        print()
        print("Cuando cifras un archivo:")
        print("1. Usas la clave PÚBLICA del receptor para cifrar")
        print("2. Solo el receptor puede descifrar con su clave PRIVADA")
        print()
        print("Es como enviar una caja fuerte cerrada:")
        print("• Cualquiera puede ver la caja (clave pública)")
        print("• Solo el destinatario tiene la llave (clave privada)")
        print()
        input("Presiona Enter para continuar...")
    
    def _seleccionar_claves_existentes(self) -> bool:
        """Ayuda al usuario a seleccionar claves existentes."""
        print("Por favor, proporciona las rutas de tus claves:")
        
        # Clave pública del receptor
        clave_publica = input("Ruta de la clave PÚBLICA del receptor: ").strip()
        if not os.path.exists(clave_publica):
            print(f"{Fore.RED}❌ Clave pública no encontrada.{Style.RESET_ALL}")
            return False
        
        self.configuracion_actual['clave_publica'] = clave_publica
        
        # Verificar fingerprint
        try:
            with open(clave_publica, 'rb') as f:
                pem = f.read()
            clave_pub = crypto.deserializar_clave_publica(pem)
            fingerprint = auth.generar_fingerprint_visual(clave_pub)
            print(f"{Fore.GREEN}✅ Clave pública válida")
            print(f"   Fingerprint: {fingerprint}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Clave pública inválida: {e}{Style.RESET_ALL}")
            return False
        
        return True
    
    def _generar_nuevas_claves(self) -> bool:
        """Genera nuevas claves RSA."""
        print("Generando nuevas claves RSA...")
        
        try:
            # Generar claves
            clave_priv, clave_pub = crypto.generar_claves_rsa()
            
            # Guardar claves
            clave_priv_pem = crypto.serializar_clave_privada(clave_priv)
            clave_pub_pem = crypto.serializar_clave_publica(clave_pub)
            
            # Nombres de archivo
            nombre_base = input("Nombre base para las claves (ej: 'mi_clave'): ").strip()
            if not nombre_base:
                nombre_base = "titansend_clave"
            
            archivo_priv = f"{nombre_base}_privada.pem"
            archivo_pub = f"{nombre_base}_publica.pem"
            
            # Guardar archivos
            with open(archivo_priv, 'wb') as f:
                f.write(clave_priv_pem)
            with open(archivo_pub, 'wb') as f:
                f.write(clave_pub_pem)
            
            print(f"{Fore.GREEN}✅ Claves generadas exitosamente:")
            print(f"   Clave privada: {archivo_priv}")
            print(f"   Clave pública: {archivo_pub}")
            
            # Mostrar fingerprint
            fingerprint = auth.generar_fingerprint_visual(clave_pub)
            print(f"   Fingerprint: {fingerprint}")
            print()
            print(f"{Fore.YELLOW}⚠️  IMPORTANTE:")
            print(f"   • Guarda la clave privada en un lugar seguro")
            print(f"   • Comparte la clave pública con quien quieras recibir archivos")
            print(f"   • Nunca compartas la clave privada{Style.RESET_ALL}")
            
            self.configuracion_actual['clave_publica'] = archivo_pub
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error generando claves: {e}{Style.RESET_ALL}")
            return False
    
    def _seleccionar_transporte(self) -> Optional[str]:
        """Ayuda al usuario a seleccionar el método de transporte."""
        print("¿Cómo quieres enviar el archivo?")
        print("1. 📱 Bluetooth (cerca)")
        print("2. 📄 Código QR (cerca)")
        print("3. 💾 USB/Pendrive (físico)")
        print("4. 🌐 P2P/Onion (internet)")
        print("5. 📧 Otro método")
        
        while True:
            opcion = input("Selecciona método (1-5): ").strip()
            
            if opcion == '1':
                return 'bluetooth'
            elif opcion == '2':
                return 'qr'
            elif opcion == '3':
                return 'usb'
            elif opcion == '4':
                return 'p2p'
            elif opcion == '5':
                print("Otros métodos disponibles:")
                print("• Email (adjuntar archivo)")
                print("• Mensajería (Telegram, Signal)")
                print("• Nube (Google Drive, Dropbox)")
                return 'otro'
            else:
                print(f"{Fore.RED}❌ Opción inválida.{Style.RESET_ALL}")
    
    def _cifrar_archivo(self) -> bool:
        """Cifra el archivo seleccionado."""
        try:
            archivo_origen = self.configuracion_actual['archivo_origen']
            clave_publica = self.configuracion_actual['clave_publica']
            
            # Leer archivo
            with open(archivo_origen, 'rb') as f:
                datos = f.read()
            
            # Leer clave pública
            with open(clave_publica, 'rb') as f:
                pem = f.read()
            clave_pub = crypto.deserializar_clave_publica(pem)
            
            # Generar contraseña
            password = input("Contraseña para derivar clave AES: ").strip()
            if not password:
                print(f"{Fore.RED}❌ La contraseña es obligatoria.{Style.RESET_ALL}")
                return False
            
            # Cifrar
            salt = os.urandom(16)
            clave_aes = crypto.generar_clave_aes(password, salt)
            
            import time
            timestamp = int(time.time()).to_bytes(8, 'big')
            nonce = os.urandom(8)
            datos_a_cifrar = timestamp + nonce + datos
            
            cifrado = crypto.cifrar_aes(datos_a_cifrar, clave_aes)
            firma = crypto.firmar_hmac(clave_aes, cifrado)
            clave_aes_cifrada = crypto.cifrar_con_publica(clave_pub, clave_aes)
            
            resultado = salt + clave_aes_cifrada + firma + cifrado
            
            # Guardar archivo cifrado
            nombre_base = os.path.splitext(os.path.basename(archivo_origen))[0]
            archivo_cifrado = f"{nombre_base}_cifrado.bin"
            
            with open(archivo_cifrado, 'wb') as f:
                f.write(resultado)
            
            self.configuracion_actual['archivo_cifrado'] = archivo_cifrado
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error cifrando archivo: {e}{Style.RESET_ALL}")
            return False
    
    def _mostrar_instrucciones_envio(self):
        """Muestra instrucciones para enviar el archivo."""
        metodo = self.configuracion_actual.get('metodo_transporte')
        archivo = self.configuracion_actual.get('archivo_cifrado')
        
        print(f"\n{Fore.CYAN}📤 INSTRUCCIONES PARA ENVIAR{Style.RESET_ALL}")
        print("="*50)
        
        if metodo == 'bluetooth':
            print("1. Activa Bluetooth en ambos dispositivos")
            print("2. Empareja los dispositivos")
            print(f"3. Envía el archivo: {archivo}")
            print("4. El receptor debe usar TitanSend para descifrar")
            
        elif metodo == 'qr':
            print("1. Genera código QR del archivo cifrado")
            print("2. Muestra el código al receptor")
            print("3. El receptor escanea y descifra")
            
        elif metodo == 'usb':
            print("1. Copia el archivo cifrado a un USB")
            print(f"   Archivo: {archivo}")
            print("2. Entrega el USB al receptor")
            print("3. El receptor usa TitanSend para descifrar")
            
        elif metodo == 'p2p':
            print("1. Configura conexión P2P o Tor")
            print("2. Comparte la dirección de conexión")
            print("3. Transfiere el archivo cifrado")
            
        print(f"\n{Fore.YELLOW}💡 El archivo cifrado está listo: {archivo}{Style.RESET_ALL}")
    
    def _seleccionar_clave_privada(self) -> Optional[str]:
        """Ayuda al usuario a seleccionar su clave privada."""
        print("Por favor, proporciona la ruta de tu clave privada:")
        
        while True:
            ruta = input("Ruta de la clave privada: ").strip()
            
            if not os.path.exists(ruta):
                print(f"{Fore.RED}❌ Clave privada no encontrada.{Style.RESET_ALL}")
                continue
            
            try:
                with open(ruta, 'rb') as f:
                    pem = f.read()
                clave_priv = crypto.deserializar_clave_privada(pem)
                print(f"{Fore.GREEN}✅ Clave privada válida{Style.RESET_ALL}")
                return ruta
            except Exception as e:
                print(f"{Fore.RED}❌ Clave privada inválida: {e}{Style.RESET_ALL}")
                continue
    
    def _descifrar_archivo(self, archivo_cifrado: str, clave_privada: str) -> bool:
        """Descifra el archivo seleccionado."""
        try:
            # Leer archivo cifrado
            with open(archivo_cifrado, 'rb') as f:
                datos = f.read()
            
            # Leer clave privada
            with open(clave_privada, 'rb') as f:
                pem = f.read()
            clave_priv = crypto.deserializar_clave_privada(pem)
            
            # Contraseña
            password = input("Contraseña usada para cifrar: ").strip()
            if not password:
                print(f"{Fore.RED}❌ La contraseña es obligatoria.{Style.RESET_ALL}")
                return False
            
            # Descifrar
            salt = datos[:16]
            clave_aes_cifrada = datos[16:16+256]
            firma = datos[16+256:16+256+32]
            cifrado = datos[16+256+32:]
            
            clave_aes = crypto.descifrar_con_privada(clave_priv, clave_aes_cifrada)
            
            if not crypto.verificar_hmac(clave_aes, cifrado, firma):
                print(f"{Fore.RED}❌ Firma HMAC inválida. El archivo puede haber sido manipulado.{Style.RESET_ALL}")
                return False
            
            descifrado = crypto.descifrar_aes(cifrado, clave_aes)
            datos_final = descifrado[16:]
            
            # Guardar archivo descifrado
            nombre_base = os.path.splitext(os.path.basename(archivo_cifrado))[0]
            archivo_descifrado = f"{nombre_base}_descifrado"
            
            with open(archivo_descifrado, 'wb') as f:
                f.write(datos_final)
            
            print(f"{Fore.GREEN}✅ Archivo descifrado guardado como: {archivo_descifrado}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error descifrando archivo: {e}{Style.RESET_ALL}")
            return False
    
    def _formatear_tamaño(self, bytes_size: int) -> str:
        """Formatea el tamaño de archivo en formato legible."""
        for unidad in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unidad}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    def mostrar_ayuda(self):
        """Muestra información de ayuda sobre TitanSend."""
        print(f"\n{Fore.CYAN}📚 ACERCA DE TITANSEND{Style.RESET_ALL}")
        print("="*50)
        print("TitanSend es tu búnker digital portátil para transferir")
        print("archivos de forma segura usando múltiples métodos.")
        print()
        print("🔒 Características de seguridad:")
        print("• Cifrado RSA-2048 para claves")
        print("• Cifrado AES-256 para datos")
        print("• Firmas HMAC para integridad")
        print("• Múltiples métodos de transporte")
        print()
        print("📤 Métodos de transporte:")
        print("• Bluetooth: Para dispositivos cercanos")
        print("• QR: Para transferencias rápidas")
        print("• USB: Para transferencias físicas")
        print("• P2P/Onion: Para transferencias por internet")
        print()
        print("🛡️ Casos de uso:")
        print("• Periodistas bajo censura")
        print("• Activistas políticos")
        print("• Empresas con información sensible")
        print("• Usuarios que quieren privacidad")
        print()
        input("Presiona Enter para continuar...")
    
    def ejecutar(self):
        """Ejecuta el wizard completo."""
        while True:
            opcion = self.mostrar_bienvenida()
            
            if opcion == '1':
                self.wizard_cifrado()
            elif opcion == '2':
                self.wizard_descifrado()
            elif opcion == '3':
                self.mostrar_ayuda()
            elif opcion == '4':
                print("Opciones avanzadas próximamente...")
            elif opcion == '5':
                print(f"{Fore.GREEN}¡Gracias por usar TitanSend!{Style.RESET_ALL}")
                break
            
            input("\nPresiona Enter para continuar...")

# Función de conveniencia
def ejecutar_wizard():
    """Ejecuta el wizard de TitanSend."""
    wizard = TitanSendWizard()
    wizard.ejecutar()

if __name__ == "__main__":
    ejecutar_wizard() 