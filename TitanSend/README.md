[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-green.svg)](LICENSE)
[![PyPI - Cryptography](https://img.shields.io/pypi/v/cryptography.svg?label=cryptography)](https://pypi.org/project/cryptography/)
[![PyPI - qrcode](https://img.shields.io/pypi/v/qrcode.svg?label=qrcode)](https://pypi.org/project/qrcode/)

# TitanSend

**TitanSend** es una solución profesional para la transferencia ultra segura de archivos entre dispositivos, sin necesidad de internet ni servidores externos. Utiliza criptografía avanzada y métodos de transporte físico para garantizar la máxima confidencialidad y control.

---

## 🚀 Características principales

- 🔒 **Cifrado híbrido fuerte:** AES-256 para el contenido, RSA-2048/4096 para la clave, y HMAC-SHA256 para integridad.
- 📱 **Múltiples métodos de transporte:** USB, QR optimizado, Bluetooth real (RFCOMM), P2P directo y Onion (Tor).
- ✂️ **Fragmentación de claves (Shamir):** Divide la clave en partes para backups distribuidos o acceso compartido.
- 🗂️ **Registro de actividad cifrado:** Guarda un historial de operaciones, accesible solo con la clave adecuada.
- 🧪 **Prueba automática incluida:** Valida todo el flujo de cifrado, descifrado y fragmentación.
- 🗃️ **Metadatos protegidos:** El archivo cifrado incluye nombre y tamaño originales, protegidos y ofuscados.
- 🖥️ **CLI avanzado:** Interfaz de línea de comandos profesional con subcomandos y validaciones robustas.

---

## 🛡️ ¿Para qué sirve?

- Transferir documentos confidenciales *sin riesgo de interceptación*.
- Realizar copias de seguridad *a prueba de hackers* y desastres.
- Compartir información sensible *sin dejar rastros digitales*.
- Implementar herencias digitales o cofres compartidos.
- **Comunicación anónima** a través de la red Tor.
- **Transferencias P2P directas** sin intermediarios.

---

## ⚙️ Instalación rápida

1. Clona el repositorio:
   ```bash
   git clone https://github.com/juanmc2023/TitanSend.git
   cd TitanSend
   ```

2. Instala las dependencias básicas:
   ```bash
   pip install -r requirements.txt
   ```

3. (Opcional) Para Bluetooth real:
   ```bash
   pip install pybluez
   ```
   > **Nota:** En Windows, pybluez solo funciona con Python ≤ 3.9

4. (Opcional) Para P2P y Onion (Tor):
   ```bash
   pip install stem PySocks
   ```

---

## 📝 Ejemplo de uso (CLI avanzado)

### Cifrar un archivo
```bash
python -m titansend.cli lock archivo.txt --public-key publica.pem --password tuclave --output archivo_cifrado.bin
```

### Descifrar un archivo
```bash
python -m titansend.cli unlock archivo_cifrado.bin --key privada.pem --password tuclave --output archivo_descifrado.txt
```

### Fragmentar una clave privada
```bash
python -m titansend.cli split privada.pem --shares 3 --threshold 2
```

### Reconstruir una clave privada
```bash
python -m titansend.cli reconstruct share_1.txt share_2.txt
```

### Enviar archivo cifrado por USB
```bash
python -m titansend.cli send archivo_cifrado.bin --method usb --output /ruta/usb/archivo.bin
```

### Enviar archivo cifrado por QR optimizado
```bash
python -m titansend.cli send archivo_cifrado.bin --method qr --output qr_base.png
```

### Enviar archivo cifrado por Bluetooth real
```bash
python -m titansend.cli send archivo_cifrado.bin --method bluetooth --address 00:11:22:33:44:55 --port 3
```

### Enviar archivo cifrado por P2P directo
```bash
python -m titansend.cli send archivo_cifrado.bin --method p2p --host 192.168.1.100 --port 8080
```

### Enviar archivo cifrado por Onion (Tor)
```bash
python -m titansend.cli send archivo_cifrado.bin --method onion --onion abc123def456.onion --port 8080
```

---

## 🧪 Pruebas automáticas

Incluye un script de test que valida:
- Generación de claves RSA
- Cifrado y descifrado de archivos
- Fragmentación y reconstrucción de claves
- Verificación de integridad

Ejecuta los tests con:
```bash
python -m unittest discover -s TitanSend/titansend -p 'test_*.py'
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más información.

---

## 🤝 Créditos y contacto

- Autor: juan martin
- Email: [tu@email.com]
- GitHub: [https://github.com/juanmc2023](https://github.com/juanmc2023)

¿Usaste TitanSend en un proyecto interesante? ¡Cuéntamelo y lo agrego aquí!

---

> **¡TitanSend: Seguridad y control total en tus transferencias!**