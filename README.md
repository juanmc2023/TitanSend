TitanSend
TitanSend es una solución profesional para la transferencia ultra segura de archivos entre dispositivos, sin necesidad de internet ni servidores externos. Utiliza criptografía avanzada y métodos de transporte físico para garantizar la máxima confidencialidad y control.

🚀 Características principales
🔒 Cifrado híbrido fuerte: AES-256 para el contenido, RSA-2048/4096 para la clave, y HMAC-SHA256 para integridad.
📲 Múltiples métodos de transporte: USB, Código QR optimizado (con compresión y fragmentación), Bluetooth real (RFCOMM), P2P directo y Onion (Tor).
✂ Fragmentación de claves (Shamir): Divide la clave en partes para backups distribuidos o acceso compartido.
📜 Registro de actividad cifrado: Guarda un historial de operaciones, accesible solo con la clave adecuada.
🧪 Prueba automática incluida: Valida todo el flujo de cifrado, descifrado y fragmentación.
🗂️ Metadatos protegidos: El archivo cifrado incluye nombre y tamaño originales, protegidos y ofuscados.
🖥️ CLI avanzado: Interfaz de línea de comandos profesional con subcomandos y validaciones robustas.
📱 QR optimizado: Compresión automática y fragmentación para archivos grandes (hasta 3KB por QR).
🔵 Bluetooth real: Soporte para RFCOMM con detección automática de compatibilidad y validación de archivos.
🌐 P2P y Onion: Conexiones directas TCP y anonimato con Tor, manteniendo cifrado extremo a extremo.
🟦 Bluetooth: Detección automática, validación de archivos, y fallback a simulación si no hay compatibilidad.
🟩 QR optimizado: Compresión zlib, fragmentación, checksum, y metadatos de fragmentación incluidos.
🟧 P2P/Onion: Conexiones directas TCP, soporte Tor, generación automática de direcciones Onion, y validaciones de seguridad robustas.
🛡️ ¿Para qué sirve?
Transferir documentos confidenciales sin riesgo de interceptación.
Realizar copias de seguridad a prueba de hackers y desastres.
Compartir información sensible sin dejar rastros digitales.
Implementar herencias digitales o cofres compartidos.
Comunicación anónima a través de la red Tor.
Transferencias P2P directas sin intermediarios.
⚙️ ¿Cómo funciona TitanSend?
Seleccionás un archivo: Puede ser cualquier tipo de documento, imagen, clave, etc.
Cifrado híbrido: El archivo se cifra con AES-256, la clave AES se cifra con la clave pública RSA del receptor, y se firma con HMAC para asegurar integridad.
(Opcional) Fragmentación de clave: Divide la clave en varias partes (Shamir), ideal para backups o acceso multiusuario.
Transmisión física y sin red: El archivo cifrado se transfiere por USB, QR optimizado, Bluetooth real, P2P directo o Onion (Tor), sin depender de internet ni servidores.
Descifrado local: El receptor usa su clave privada RSA y la contraseña para recuperar el archivo, validando la integridad con HMAC.
Registro cifrado: Opcionalmente, se guarda un log cifrado de cada operación.
Metadatos protegidos: El archivo cifrado contiene nombre y tamaño originales, solo accesibles tras descifrar.
QR inteligente: Compresión automática y fragmentación para archivos de cualquier tamaño.
Bluetooth robusto: Validación de archivos y detección automática de compatibilidad.
P2P y Onion: Conexiones directas o anónimas manteniendo el cifrado extremo a extremo.
Como si tomaras un archivo, lo metieras en una caja fuerte digital y se lo entregaras a alguien en mano, sin que nadie pueda interceptarlo ni saber qué había adentro.

🧪 Prueba automática
Incluye un script de test que valida:

Generación de claves RSA
Cifrado y descifrado de archivos
Fragmentación y reconstrucción de claves
Verificación de integridad
📦 Instalación rápida
Instala las dependencias básicas:

pip install cryptography qrcode colorama
(Opcional) Para Bluetooth real:

pip install pybluez
Nota: En Windows, pybluez solo funciona con Python ≤3.9

(Opcional) Para P2P y Onion (Tor):

pip install stem PySocks
Ejecuta el CLI avanzado:

python -m titansend.cli --help
📝 Ejemplo de uso (CLI avanzado)
Cifrar un archivo
python -m titansend.cli lock archivo.txt --public-key publica.pem --password tuclave --output archivo_cifrado.bin
Descifrar un archivo
python -m titansend.cli unlock archivo_cifrado.bin --key privada.pem --password tuclave --output archivo_descifrado.txt
Fragmentar una clave privada
python -m titansend.cli split privada.pem --shares 3 --threshold 2
Reconstruir una clave privada
python -m titansend.cli reconstruct share_1.txt share_2.txt
Enviar archivo cifrado por USB
python -m titansend.cli send archivo_cifrado.bin --method usb --output /ruta/usb/archivo.bin
Enviar archivo cifrado por QR optimizado
python -m titansend.cli send archivo_cifrado.bin --method qr --output qr_base.png
Características automáticas:

Compresión con zlib (nivel 9)
Fragmentación automática para archivos grandes
Hasta 3KB por QR (vs ~1KB estándar)
Enviar archivo cifrado por Bluetooth real
python -m titansend.cli send archivo_cifrado.bin --method bluetooth --address 00:11:22:33:44:55 --port 3
Enviar archivo cifrado por P2P directo
python -m titansend.cli send archivo_cifrado.bin --method p2p --host 192.168.1.100 --port 8080
Enviar archivo cifrado por Onion (Tor)
python -m titansend.cli send archivo_cifrado.bin --method onion --onion abc123def456.onion --port 8080
Enviar archivo cifrado por Tor (HTTP sobre la red Tor)
python -m titansend.cli send archivo_cifrado.bin --method tor --url http://127.0.0.1:5000/upload
Buscar dispositivos Bluetooth cercanos
python -m titansend.cli scan
Verificar disponibilidad de Tor
python -m titansend.cli check_tor
Generar nueva dirección Onion
python -m titansend.cli generate_onion --port 8080
Obtener dirección Onion actual
python -m titansend.cli get_onion_address
Recibir archivo cifrado por USB
python -m titansend.cli receive --method usb --input /ruta/usb/archivo.bin --output archivo_recibido.bin
Recibir archivo cifrado por QR optimizado
# Para un solo QR:
python -m titansend.cli receive --method qr --input qr_base.png --output archivo_recibido.bin

# Para múltiples QR (archivo grande):
python -m titansend.cli receive --method qr --input "qr_base_parte_01_de_03.png qr_base_parte_02_de_03.png qr_base_parte_03_de_03.png" --output archivo_recibido.bin
Recibir archivo cifrado por Bluetooth real
python -m titansend.cli receive --method bluetooth --output archivo_recibido.bin --port 3
Recibir archivo cifrado por P2P directo
python -m titansend.cli receive --method p2p --output archivo_recibido.bin --port 8080
Recibir archivo cifrado por Onion (Tor)
python -m titansend.cli receive --method onion --output archivo_recibido.bin --port 8080
Recibir archivo cifrado por Tor (HTTP sobre la red Tor)
python -m titansend.cli receive --method tor --url http://127.0.0.1:5000/download --output archivo_recibido.bin
🔵 Bluetooth real (RFCOMM)
Características:
Detección automática de compatibilidad
Validación de archivos TitanSend
Mensajes informativos con progreso de transferencia
Fallback automático a simulación si no hay compatibilidad
Requisitos:
pybluez instalado
En Windows: Python ≤3.9
Dispositivos Bluetooth emparejados
Flujo típico:
Receptor (esperando):
python -m titansend.cli receive --method bluetooth --output archivo_recibido.bin
Emisor (enviando):
python -m titansend.cli send archivo_cifrado.bin --method bluetooth --address XX:XX:XX:XX:XX:XX
📱 QR optimizado
Características:
Compresión automática con zlib (nivel 9)
Fragmentación automática para archivos grandes
Capacidad máxima: 2,956 bytes por QR
Verificación de integridad con checksum
Metadatos de fragmentación incluidos
Ventajas:
Hasta 3x más capacidad que QR estándar
Archivos de ~10-15KB en un solo QR
Archivos de cualquier tamaño con fragmentación
Reconstrucción automática desde múltiples QR
🌐 P2P y Onion (Tor)
Características:
Conexiones directas TCP sin intermediarios
Soporte completo para Tor con anonimato
Cifrado extremo a extremo mantenido en todo momento
Detección automática de disponibilidad de Tor/SOCKS
Generación de direcciones Onion automática
Validaciones de seguridad robustas
Ventajas:
Sin servidores centrales ni dependencias externas
Anonimato completo con Tor
Velocidad directa en P2P
Cifrado mantenido en todo el trayecto
Configuración automática de servicios Onion
Requisitos para Onion:
stem y PySocks instalados
Tor Browser o Tor daemon ejecutándose
Puerto de control Tor configurado (9051)
Flujo típico P2P:
Receptor (esperando):
python -m titansend.cli receive --method p2p --output archivo_recibido.bin --port 8080
Emisor (enviando):
python -m titansend.cli send archivo_cifrado.bin --method p2p --host 192.168.1.100 --port 8080
Flujo típico Onion:
Receptor (genera dirección Onion):
python -m titansend.cli generate_onion --port 8080
# Resultado: abc123def456.onion
Receptor (esperando):
python -m titansend.cli receive --method onion --output archivo_recibido.bin --port 8080
Emisor (enviando):
python -m titansend.cli send archivo_cifrado.bin --method onion --onion abc123def456.onion --port 8080
Verificación de Tor:
# Verificar disponibilidad
python -m titansend.cli check_tor

# Obtener dirección Onion actual
python -m titansend.cli get_onion_address
🧠 Ejemplo real
Juan quiere darle a Ana su testamento digital. Lo cifra con TitanSend, imprime un código QR optimizado (que incluye compresión automática), y Ana lo escanea. Nadie en internet supo nada. Todo quedó entre ellos, seguro y silencioso.

Ejemplo P2P/Onion:

María necesita enviar documentos confidenciales a Carlos en otro país. Usa TitanSend con Onion para crear una dirección anónima, Carlos se conecta a través de Tor, y los archivos se transfieren con cifrado extremo a extremo, sin que nadie pueda rastrear la comunicación.

⚠️ Notas importantes
La fragmentación de clave (Shamir) implementada es una versión mínima para demostración. Para producción, se recomienda usar una librería auditada y robusta.
Bluetooth real requiere pybluez y en Windows solo funciona con Python ≤3.9.
Los archivos transferidos por Bluetooth deben ser archivos cifrados válidos de TitanSend.
El QR optimizado incluye compresión automática y fragmentación para archivos grandes.
P2P y Onion son opcionales y requieren stem y PySocks para funcionalidad completa.
Tor debe estar ejecutándose para usar funcionalidades Onion.
El cifrado extremo a extremo se mantiene en todos los métodos de transporte.
🤝 Créditos y contacto
Autor: [juanmc2023]
