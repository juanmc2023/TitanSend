"""
TitanSend - Tu Búnker Digital Portátil
=======================================

Un sistema de cifrado y transferencia segura de archivos con múltiples métodos
de transporte: Bluetooth, QR, USB, P2P y Tor.

Módulos principales:
- crypto: Cifrado/descifrado RSA y AES
- shamir: Fragmentación de claves (demo)
- transport: Métodos de transporte de datos
- log: Registro cifrado de operaciones
"""

# Importar módulos principales
from . import crypto
from . import shamir
from . import transport
from . import log
from . import auth
from . import shamir_robusto
from . import tor_setup
from . import wizard

# Versión del proyecto
__version__ = '1.0.0'

# Información del proyecto
__author__ = 'TitanSend Team'
__description__ = 'Tu Búnker Digital Portátil'

# Exportar módulos principales
__all__ = ['crypto', 'shamir', 'transport', 'log', 'auth', 'shamir_robusto', 'tor_setup', 'wizard'] 