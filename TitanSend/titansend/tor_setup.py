"""
Configuración Automática de Tor para TitanSend
==============================================

Scripts para automatizar la descarga, configuración y arranque del cliente Tor.
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import tarfile
import json
from pathlib import Path
from typing import Optional, Dict, List

class TorSetup:
    """
    Clase para manejar la configuración automática de Tor.
    """
    
    def __init__(self):
        self.sistema = platform.system().lower()
        self.arquitectura = platform.machine().lower()
        self.directorio_tor = self._obtener_directorio_tor()
        self.config_tor = self.directorio_tor / "torrc"
        
    def _obtener_directorio_tor(self) -> Path:
        """Obtiene el directorio donde se instalará Tor."""
        if self.sistema == "windows":
            return Path.home() / "AppData" / "Local" / "TitanSend" / "Tor"
        elif self.sistema == "darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "TitanSend" / "Tor"
        else:  # Linux
            return Path.home() / ".local" / "share" / "titansend" / "tor"
    
    def _obtener_url_descarga(self) -> Optional[str]:
        """Obtiene la URL de descarga de Tor según el sistema."""
        base_url = "https://dist.torproject.org/tor"
        
        if self.sistema == "windows":
            if "64" in self.arquitectura:
                return f"{base_url}-0.4.8.10-win64.zip"
            else:
                return f"{base_url}-0.4.8.10-win32.zip"
        elif self.sistema == "darwin":
            return f"{base_url}-0.4.8.10-osx64.tar.gz"
        elif self.sistema == "linux":
            # Para Linux, intentamos usar el gestor de paquetes primero
            return None
        else:
            return None
    
    def verificar_tor_instalado(self) -> bool:
        """Verifica si Tor ya está instalado y funcionando."""
        try:
            # Intentar ejecutar tor --version
            resultado = subprocess.run(
                ["tor", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return resultado.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def instalar_tor_sistema(self) -> bool:
        """Intenta instalar Tor usando el gestor de paquetes del sistema."""
        if self.sistema == "linux":
            try:
                # Intentar con apt (Debian/Ubuntu)
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", "tor"], check=True)
                return True
            except subprocess.CalledProcessError:
                try:
                    # Intentar con yum (RHEL/CentOS)
                    subprocess.run(["sudo", "yum", "install", "-y", "tor"], check=True)
                    return True
                except subprocess.CalledProcessError:
                    return False
        return False
    
    def descargar_tor(self) -> bool:
        """Descarga Tor desde el sitio oficial."""
        url = self._obtener_url_descarga()
        if not url:
            print("❌ No se pudo determinar la URL de descarga para este sistema.")
            return False
        
        # Crear directorio de descarga
        self.directorio_tor.mkdir(parents=True, exist_ok=True)
        archivo_descarga = self.directorio_tor / "tor_download"
        
        try:
            print(f"📥 Descargando Tor desde {url}...")
            urllib.request.urlretrieve(url, archivo_descarga)
            return self._extraer_tor(archivo_descarga)
        except Exception as e:
            print(f"❌ Error descargando Tor: {e}")
            return False
    
    def _extraer_tor(self, archivo_descarga: Path) -> bool:
        """Extrae el archivo descargado de Tor."""
        try:
            if archivo_descarga.suffix == ".zip":
                with zipfile.ZipFile(archivo_descarga, 'r') as zip_ref:
                    zip_ref.extractall(self.directorio_tor)
            elif archivo_descarga.suffix == ".tar.gz":
                with tarfile.open(archivo_descarga, 'r:gz') as tar_ref:
                    tar_ref.extractall(self.directorio_tor)
            
            # Limpiar archivo de descarga
            archivo_descarga.unlink()
            return True
        except Exception as e:
            print(f"❌ Error extrayendo Tor: {e}")
            return False
    
    def configurar_tor(self) -> bool:
        """Configura Tor con parámetros básicos."""
        try:
            # Crear configuración básica
            config = f"""# Configuración básica de Tor para TitanSend
SocksPort 9050
DataDirectory {self.directorio_tor / "data"}
PidFile {self.directorio_tor / "tor.pid"}
Log notice file {self.directorio_tor / "tor.log"}
RunAsDaemon 1
"""
            
            # Escribir configuración
            with open(self.config_tor, 'w') as f:
                f.write(config)
            
            return True
        except Exception as e:
            print(f"❌ Error configurando Tor: {e}")
            return False
    
    def iniciar_tor(self) -> bool:
        """Inicia el servicio Tor."""
        try:
            # Buscar ejecutable de Tor
            tor_exe = self._buscar_ejecutable_tor()
            if not tor_exe:
                print("❌ No se encontró el ejecutable de Tor.")
                return False
            
            # Iniciar Tor como daemon
            subprocess.Popen([
                str(tor_exe),
                "-f", str(self.config_tor),
                "--runasdaemon", "1"
            ])
            
            # Esperar un poco para que inicie
            import time
            time.sleep(3)
            
            return self.verificar_conectividad_tor()
        except Exception as e:
            print(f"❌ Error iniciando Tor: {e}")
            return False
    
    def _buscar_ejecutable_tor(self) -> Optional[Path]:
        """Busca el ejecutable de Tor."""
        # Primero buscar en PATH
        try:
            resultado = subprocess.run(["which", "tor"], capture_output=True, text=True)
            if resultado.returncode == 0:
                return Path(resultado.stdout.strip())
        except:
            pass
        
        # Buscar en directorio de instalación
        posibles_rutas = [
            self.directorio_tor / "tor" / "tor.exe",
            self.directorio_tor / "tor" / "tor",
            self.directorio_tor / "bin" / "tor.exe",
            self.directorio_tor / "bin" / "tor"
        ]
        
        for ruta in posibles_rutas:
            if ruta.exists():
                return ruta
        
        return None
    
    def verificar_conectividad_tor(self) -> bool:
        """Verifica si Tor está funcionando correctamente."""
        try:
            import socket
            import socks
            
            # Configurar proxy SOCKS
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            socket.socket = socks.socksocket
            
            # Intentar conectar a un sitio web
            import urllib.request
            respuesta = urllib.request.urlopen("http://httpbin.org/ip", timeout=10)
            datos = respuesta.read()
            
            # Verificar que la IP no es la local
            ip_info = json.loads(datos.decode())
            if "origin" in ip_info:
                print(f"✅ Tor funcionando. IP externa: {ip_info['origin']}")
                return True
            
            return False
        except Exception as e:
            print(f"❌ Error verificando conectividad Tor: {e}")
            return False
    
    def obtener_direccion_onion(self) -> Optional[str]:
        """Obtiene la dirección .onion del servicio Tor."""
        try:
            # Leer archivo de hostname
            hostname_file = self.directorio_tor / "data" / "hidden_service" / "hostname"
            if hostname_file.exists():
                with open(hostname_file, 'r') as f:
                    return f.read().strip()
        except Exception:
            pass
        return None
    
    def configurar_servicio_hidden(self, puerto: int = 8080) -> bool:
        """Configura un servicio hidden en Tor."""
        try:
            # Crear directorio del servicio
            hidden_dir = self.directorio_tor / "data" / "hidden_service"
            hidden_dir.mkdir(parents=True, exist_ok=True)
            
            # Agregar configuración al torrc
            config_hidden = f"""
HiddenServiceDir {hidden_dir}
HiddenServicePort {puerto} 127.0.0.1:{puerto}
"""
            
            with open(self.config_tor, 'a') as f:
                f.write(config_hidden)
            
            return True
        except Exception as e:
            print(f"❌ Error configurando servicio hidden: {e}")
            return False
    
    def setup_completo(self) -> Dict:
        """Realiza la configuración completa de Tor."""
        resultado = {
            "tor_instalado": False,
            "tor_configurado": False,
            "tor_funcionando": False,
            "direccion_onion": None,
            "errores": []
        }
        
        print("🔧 Configurando Tor para TitanSend...")
        
        # Verificar si ya está instalado
        if self.verificar_tor_instalado():
            print("✅ Tor ya está instalado en el sistema.")
            resultado["tor_instalado"] = True
        else:
            # Intentar instalar con gestor de paquetes
            if self.instalar_tor_sistema():
                print("✅ Tor instalado usando gestor de paquetes.")
                resultado["tor_instalado"] = True
            else:
                # Descargar manualmente
                if self.descargar_tor():
                    print("✅ Tor descargado e instalado.")
                    resultado["tor_instalado"] = True
                else:
                    resultado["errores"].append("No se pudo instalar Tor")
                    return resultado
        
        # Configurar Tor
        if self.configurar_tor():
            print("✅ Tor configurado.")
            resultado["tor_configurado"] = True
        else:
            resultado["errores"].append("No se pudo configurar Tor")
        
        # Iniciar Tor
        if self.iniciar_tor():
            print("✅ Tor iniciado y funcionando.")
            resultado["tor_funcionando"] = True
        else:
            resultado["errores"].append("No se pudo iniciar Tor")
        
        # Obtener dirección onion si está disponible
        if resultado["tor_funcionando"]:
            direccion = self.obtener_direccion_onion()
            if direccion:
                print(f"🌐 Dirección .onion: {direccion}")
                resultado["direccion_onion"] = direccion
        
        return resultado

# Funciones de conveniencia
def configurar_tor_automatico() -> Dict:
    """Configura Tor automáticamente."""
    setup = TorSetup()
    return setup.setup_completo()

def verificar_tor_disponible() -> bool:
    """Verifica si Tor está disponible y funcionando."""
    setup = TorSetup()
    return setup.verificar_tor_instalado() and setup.verificar_conectividad_tor()

def obtener_direccion_onion_actual() -> Optional[str]:
    """Obtiene la dirección .onion actual si está disponible."""
    setup = TorSetup()
    return setup.obtener_direccion_onion()

if __name__ == "__main__":
    # Ejecutar configuración automática
    resultado = configurar_tor_automatico()
    print("\n📊 Resumen de configuración:")
    for clave, valor in resultado.items():
        print(f"  {clave}: {valor}") 