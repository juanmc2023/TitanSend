import sys
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QLabel, QVBoxLayout, QPushButton, QComboBox, QFileDialog, QLineEdit, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, QTranslator, QLocale
from PySide6.QtGui import QIcon

IDIOMAS = {
    'Español': 'es',
    'English': 'en'
}

class BienvenidaPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Bienvenido a TitanSend")
        layout = QVBoxLayout()
        label = QLabel("<h2>🛡️ TitanSend - Tu Búnker Digital Portátil</h2>\n<p>Asistente paso a paso para cifrar, descifrar y transferir archivos de forma segura.</p>")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.combo_idioma = QComboBox()
        self.combo_idioma.addItems(IDIOMAS.keys())
        layout.addWidget(QLabel("Selecciona tu idioma:"))
        layout.addWidget(self.combo_idioma)
        self.setLayout(layout)

    def nextId(self):
        return 1

class SeleccionOperacionPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("¿Qué quieres hacer?")
        layout = QVBoxLayout()
        self.combo_operacion = QComboBox()
        self.combo_operacion.addItems([
            "Cifrar un archivo",
            "Descifrar un archivo",
            "Fragmentar clave (Shamir)",
            "Recuperar clave (Shamir)",
            "Configuración avanzada",
            "Ayuda y documentación"
        ])
        layout.addWidget(QLabel("Selecciona la operación principal:"))
        layout.addWidget(self.combo_operacion)
        self.setLayout(layout)

    def nextId(self):
        op = self.combo_operacion.currentIndex()
        if op == 0:
            return 2  # Cifrar
        elif op == 1:
            return 3  # Descifrar
        elif op == 2:
            return 4  # Fragmentar
        elif op == 3:
            return 5  # Recuperar
        elif op == 4:
            return 6  # Configuración
        else:
            return 7  # Ayuda

class CifrarArchivoPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Cifrar un archivo")
        layout = QVBoxLayout()
        self.label_info = QLabel("Selecciona el archivo que deseas cifrar:")
        layout.addWidget(self.label_info)
        self.edit_archivo = QLineEdit()
        btn_browse = QPushButton("Examinar...")
        btn_browse.clicked.connect(self.seleccionar_archivo)
        layout.addWidget(self.edit_archivo)
        layout.addWidget(btn_browse)
        self.label_clave = QLabel("Ruta de la clave pública del receptor:")
        self.edit_clave = QLineEdit()
        btn_browse_clave = QPushButton("Examinar clave...")
        btn_browse_clave.clicked.connect(self.seleccionar_clave)
        layout.addWidget(self.label_clave)
        layout.addWidget(self.edit_clave)
        layout.addWidget(btn_browse_clave)
        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Contraseña para derivar clave AES:"))
        layout.addWidget(self.edit_password)
        self.setLayout(layout)

    def seleccionar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo")
        if archivo:
            self.edit_archivo.setText(archivo)

    def seleccionar_clave(self):
        clave, _ = QFileDialog.getOpenFileName(self, "Seleccionar clave pública", filter="*.pem")
        if clave:
            self.edit_clave.setText(clave)

    def nextId(self):
        return 8  # Mockup de progreso/confirmación

class DescifrarArchivoPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Descifrar un archivo")
        layout = QVBoxLayout()
        self.label_info = QLabel("Selecciona el archivo cifrado que deseas descifrar:")
        layout.addWidget(self.label_info)
        self.edit_archivo = QLineEdit()
        btn_browse = QPushButton("Examinar...")
        btn_browse.clicked.connect(self.seleccionar_archivo)
        layout.addWidget(self.edit_archivo)
        layout.addWidget(btn_browse)
        self.label_clave = QLabel("Ruta de la clave privada:")
        self.edit_clave = QLineEdit()
        btn_browse_clave = QPushButton("Examinar clave...")
        btn_browse_clave.clicked.connect(self.seleccionar_clave)
        layout.addWidget(self.label_clave)
        layout.addWidget(self.edit_clave)
        layout.addWidget(btn_browse_clave)
        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Contraseña usada para cifrar:"))
        layout.addWidget(self.edit_password)
        self.setLayout(layout)

    def seleccionar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo cifrado")
        if archivo:
            self.edit_archivo.setText(archivo)

    def seleccionar_clave(self):
        clave, _ = QFileDialog.getOpenFileName(self, "Seleccionar clave privada", filter="*.pem")
        if clave:
            self.edit_clave.setText(clave)

    def nextId(self):
        return 8  # Mockup de progreso/confirmación

class ProgresoPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Progreso y confirmación")
        layout = QVBoxLayout()
        self.label = QLabel("<b>Esta es una pantalla de ejemplo de progreso.</b>\nAquí se mostrarán los resultados y notificaciones.")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def nextId(self):
        return -1  # Fin del wizard

class TitanSendWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TitanSend - Asistente de Seguridad")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        self.setWindowIcon(QIcon())
        self.resize(600, 400)
        # Páginas
        self.addPage(BienvenidaPage())           # 0
        self.addPage(SeleccionOperacionPage())   # 1
        self.addPage(CifrarArchivoPage())        # 2
        self.addPage(DescifrarArchivoPage())     # 3
        self.addPage(ProgresoPage())             # 4 (Fragmentar - mockup)
        self.addPage(ProgresoPage())             # 5 (Recuperar - mockup)
        self.addPage(ProgresoPage())             # 6 (Configuración - mockup)
        self.addPage(ProgresoPage())             # 7 (Ayuda - mockup)
        self.addPage(ProgresoPage())             # 8 (Progreso/confirmación)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = TitanSendWizard()
    wizard.show()
    sys.exit(app.exec()) 