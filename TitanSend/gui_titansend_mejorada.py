import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
import time
from pathlib import Path

# Agregar el directorio del proyecto al path para importar titansend
sys.path.append(os.path.join(os.path.dirname(__file__), 'titansend'))

try:
    from titansend import crypto, auth, shamir_robusto, tor_setup
    TITANSEND_AVAILABLE = True
except ImportError:
    TITANSEND_AVAILABLE = False
    print("⚠️  TitanSend no disponible. Ejecutando en modo demo.")

class TitanSendGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TitanSend - Tu Búnker Digital Portátil")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.archivo_origen = tk.StringVar()
        self.clave_publica = tk.StringVar()
        self.clave_privada = tk.StringVar()
        self.password = tk.StringVar()
        self.operacion_actual = None
        self.progreso = None
        
        # Configurar estilo moderno
        self.configurar_estilo()
        
        self.crear_interfaz()
    
    def configurar_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores modernos
        style.configure('TFrame', background='#ecf0f1')
        style.configure('TLabel', background='#ecf0f1', font=('Segoe UI', 9))
        style.configure('TButton', font=('Segoe UI', 9, 'bold'))
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), foreground='#7f8c8d')
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Warning.TLabel', foreground='#f39c12')
        style.configure('Error.TLabel', foreground='#e74c3c')
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título principal
        titulo = ttk.Label(main_frame, text="🛡️ TitanSend", style='Title.TLabel')
        titulo.pack(pady=(0, 5))
        
        subtitulo = ttk.Label(main_frame, text="Tu Búnker Digital Portátil", style='Subtitle.TLabel')
        subtitulo.pack(pady=(0, 30))
        
        # Frame para botones principales
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Configurar grid para botones
        for i in range(3):
            btn_frame.columnconfigure(i, weight=1)
        
        # Botones principales con iconos y mejor diseño
        botones_principales = [
            ("🔒 Cifrar Archivo", self.mostrar_cifrado, '#3498db'),
            ("🔓 Descifrar Archivo", self.mostrar_descifrado, '#e74c3c'),
            ("✂️ Fragmentar Clave", self.mostrar_fragmentacion, '#9b59b6'),
            ("🔧 Recuperar Clave", self.mostrar_recuperacion, '#f39c12'),
            ("⚙️ Configuración", self.mostrar_configuracion, '#34495e'),
            ("📚 Ayuda", self.mostrar_ayuda, '#1abc9c')
        ]
        
        row = 0
        col = 0
        for texto, comando, color in botones_principales:
            btn = tk.Button(btn_frame, text=texto, command=comando,
                          bg=color, fg='white', font=('Segoe UI', 10, 'bold'),
                          relief=tk.FLAT, padx=20, pady=10, cursor='hand2')
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
            
            # Efectos hover
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.clarificar_color(color)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Frame de estado y logs
        self.crear_panel_estado(main_frame)
        
        # Información de TitanSend
        if TITANSEND_AVAILABLE:
            info_text = "✅ TitanSend disponible - Funciones completas"
            info_style = 'Success.TLabel'
        else:
            info_text = "⚠️ Modo demo - TitanSend no disponible"
            info_style = 'Warning.TLabel'
        
        ttk.Label(main_frame, text=info_text, style=info_style).pack(pady=(10, 0))
    
    def clarificar_color(self, color):
        """Clarifica un color para efectos hover"""
        # Simplificación: devuelve un color más claro
        return '#5dade2' if color == '#3498db' else color
    
    def crear_panel_estado(self, parent):
        """Crea el panel de estado y logs"""
        estado_frame = ttk.LabelFrame(parent, text="Estado y Logs", padding="10")
        estado_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Estado actual
        self.estado_label = ttk.Label(estado_frame, text="Listo para usar", style='Success.TLabel')
        self.estado_label.pack(anchor=tk.W)
        
        # Área de logs
        self.log_text = scrolledtext.ScrolledText(estado_frame, height=8, width=70, 
                                                font=('Consolas', 8))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.log_text.config(state=tk.DISABLED)
    
    def log(self, mensaje, tipo="info"):
        """Añade un mensaje al log"""
        timestamp = time.strftime("%H:%M:%S")
        color_map = {
            "info": "black",
            "success": "green",
            "warning": "orange",
            "error": "red"
        }
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {mensaje}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Actualizar estado
        self.estado_label.config(text=mensaje)
    
    def mostrar_cifrado(self):
        self.operacion_actual = "cifrar"
        self.crear_ventana_operacion("Cifrar Archivo", self.crear_formulario_cifrado)
    
    def mostrar_descifrado(self):
        self.operacion_actual = "descifrar"
        self.crear_ventana_operacion("Descifrar Archivo", self.crear_formulario_descifrado)
    
    def mostrar_fragmentacion(self):
        self.operacion_actual = "fragmentar"
        self.crear_ventana_operacion("Fragmentar Clave (Shamir)", self.crear_formulario_fragmentacion)
    
    def mostrar_recuperacion(self):
        self.operacion_actual = "recuperar"
        self.crear_ventana_operacion("Recuperar Clave (Shamir)", self.crear_formulario_recuperacion)
    
    def mostrar_configuracion(self):
        self.crear_ventana_operacion("Configuración Avanzada", self.crear_formulario_configuracion)
    
    def mostrar_ayuda(self):
        self.crear_ventana_operacion("Ayuda y Documentación", self.crear_formulario_ayuda)
    
    def crear_ventana_operacion(self, titulo, funcion_formulario):
        """Crea una ventana de operación con diseño mejorado"""
        ventana = tk.Toplevel(self.root)
        ventana.title(f"TitanSend - {titulo}")
        ventana.geometry("700x500")
        ventana.configure(bg='#ecf0f1')
        
        # Centrar ventana
        ventana.transient(self.root)
        ventana.grab_set()
        
        # Frame principal
        frame = ttk.Frame(ventana, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text=titulo, style='Title.TLabel').pack(pady=(0, 20))
        
        # Crear formulario específico
        funcion_formulario(frame, ventana)
    
    def crear_formulario_cifrado(self, frame, ventana):
        """Formulario mejorado para cifrado"""
        # Archivo a cifrar
        ttk.Label(frame, text="📁 Archivo a cifrar:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        archivo_frame = ttk.Frame(frame)
        archivo_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Entry(archivo_frame, textvariable=self.archivo_origen, font=('Segoe UI', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(archivo_frame, text="📂 Examinar", 
                  command=lambda: self.seleccionar_archivo(self.archivo_origen)).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Clave pública
        ttk.Label(frame, text="🔑 Clave pública del receptor:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        clave_frame = ttk.Frame(frame)
        clave_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Entry(clave_frame, textvariable=self.clave_publica, font=('Segoe UI', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(clave_frame, text="📂 Examinar", 
                  command=lambda: self.seleccionar_archivo(self.clave_publica, [("PEM files", "*.pem")])).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Contraseña
        ttk.Label(frame, text="🔐 Contraseña para derivar clave AES:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(frame, textvariable=self.password, show="*", font=('Segoe UI', 9)).pack(anchor=tk.W, pady=(0, 20))
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="🔒 Cifrar", 
                  command=lambda: self.ejecutar_cifrado(ventana)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="❌ Cancelar", 
                  command=ventana.destroy).pack(side=tk.RIGHT)
    
    def crear_formulario_descifrado(self, frame, ventana):
        """Formulario mejorado para descifrado"""
        # Archivo cifrado
        ttk.Label(frame, text="📁 Archivo cifrado:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        archivo_frame = ttk.Frame(frame)
        archivo_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Entry(archivo_frame, textvariable=self.archivo_origen, font=('Segoe UI', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(archivo_frame, text="📂 Examinar", 
                  command=lambda: self.seleccionar_archivo(self.archivo_origen, [("Binary files", "*.bin")])).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Clave privada
        ttk.Label(frame, text="🔑 Clave privada:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        clave_frame = ttk.Frame(frame)
        clave_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Entry(clave_frame, textvariable=self.clave_privada, font=('Segoe UI', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(clave_frame, text="📂 Examinar", 
                  command=lambda: self.seleccionar_archivo(self.clave_privada, [("PEM files", "*.pem")])).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Contraseña
        ttk.Label(frame, text="🔐 Contraseña usada para cifrar:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(frame, textvariable=self.password, show="*", font=('Segoe UI', 9)).pack(anchor=tk.W, pady=(0, 20))
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="🔓 Descifrar", 
                  command=lambda: self.ejecutar_descifrado(ventana)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="❌ Cancelar", 
                  command=ventana.destroy).pack(side=tk.RIGHT)
    
    def crear_formulario_fragmentacion(self, frame, ventana):
        """Formulario para fragmentación Shamir"""
        # Clave a fragmentar
        ttk.Label(frame, text="🔑 Clave a fragmentar:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        clave_entry = ttk.Entry(frame, font=('Segoe UI', 9), width=50)
        clave_entry.pack(anchor=tk.W, pady=(0, 15))
        
        # Parámetros Shamir
        params_frame = ttk.Frame(frame)
        params_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(params_frame, text="Número total de fragmentos (n):").pack(anchor=tk.W)
        n_spinbox = ttk.Spinbox(params_frame, from_=2, to=10, width=10)
        n_spinbox.pack(anchor=tk.W, pady=(0, 10))
        n_spinbox.set(5)
        
        ttk.Label(params_frame, text="Fragmentos mínimos para reconstruir (k):").pack(anchor=tk.W)
        k_spinbox = ttk.Spinbox(params_frame, from_=2, to=5, width=10)
        k_spinbox.pack(anchor=tk.W, pady=(0, 15))
        k_spinbox.set(3)
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="✂️ Fragmentar", 
                  command=lambda: self.ejecutar_fragmentacion(clave_entry.get(), n_spinbox.get(), k_spinbox.get(), ventana)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="❌ Cancelar", 
                  command=ventana.destroy).pack(side=tk.RIGHT)
    
    def crear_formulario_recuperacion(self, frame, ventana):
        """Formulario para recuperación Shamir"""
        ttk.Label(frame, text="📝 Ingresa los fragmentos (uno por línea):", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # Área de texto para fragmentos
        fragmentos_text = scrolledtext.ScrolledText(frame, height=10, width=60, font=('Consolas', 9))
        fragmentos_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="🔧 Recuperar", 
                  command=lambda: self.ejecutar_recuperacion(fragmentos_text.get("1.0", tk.END), ventana)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="❌ Cancelar", 
                  command=ventana.destroy).pack(side=tk.RIGHT)
    
    def crear_formulario_configuracion(self, frame, ventana):
        """Formulario de configuración avanzada"""
        # Notebook para pestañas
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña General
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        # Pestaña Tor
        tor_frame = ttk.Frame(notebook)
        notebook.add(tor_frame, text="Tor")
        
        # Pestaña Bluetooth
        bluetooth_frame = ttk.Frame(notebook)
        notebook.add(bluetooth_frame, text="Bluetooth")
        
        # Contenido de pestañas
        self.crear_config_general(general_frame)
        self.crear_config_tor(tor_frame)
        self.crear_config_bluetooth(bluetooth_frame)
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="💾 Guardar", 
                  command=lambda: self.guardar_configuracion(ventana)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="❌ Cancelar", 
                  command=ventana.destroy).pack(side=tk.RIGHT)
    
    def crear_config_general(self, frame):
        """Configuración general"""
        ttk.Label(frame, text="Configuración General", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 15))
        
        # Idioma
        ttk.Label(frame, text="Idioma:").pack(anchor=tk.W)
        idioma_combo = ttk.Combobox(frame, values=["Español", "English"], state="readonly")
        idioma_combo.pack(anchor=tk.W, pady=(0, 15))
        idioma_combo.set("Español")
        
        # Directorio de trabajo
        ttk.Label(frame, text="Directorio de trabajo:").pack(anchor=tk.W)
        dir_frame = ttk.Frame(frame)
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Entry(dir_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="📂 Examinar").pack(side=tk.RIGHT, padx=(5, 0))
    
    def crear_config_tor(self, frame):
        """Configuración de Tor"""
        ttk.Label(frame, text="Configuración de Tor", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 15))
        
        # Estado de Tor
        if TITANSEND_AVAILABLE:
            try:
                tor_disponible = tor_setup.verificar_tor_disponible()
                estado_tor = "✅ Disponible" if tor_disponible else "❌ No disponible"
            except:
                estado_tor = "❓ No verificado"
        else:
            estado_tor = "⚠️ Modo demo"
        
        ttk.Label(frame, text=f"Estado de Tor: {estado_tor}").pack(anchor=tk.W, pady=(0, 15))
        
        # Botones de Tor
        ttk.Button(frame, text="🔧 Configurar Tor automáticamente", 
                  command=self.configurar_tor).pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(frame, text="🌐 Verificar conectividad", 
                  command=self.verificar_tor).pack(anchor=tk.W, pady=(0, 5))
    
    def crear_config_bluetooth(self, frame):
        """Configuración de Bluetooth"""
        ttk.Label(frame, text="Configuración de Bluetooth", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Label(frame, text="Estado: ⚠️ Requiere pybluez").pack(anchor=tk.W, pady=(0, 15))
        ttk.Button(frame, text="📱 Escanear dispositivos", 
                  command=self.escanear_bluetooth).pack(anchor=tk.W, pady=(0, 5))
    
    def crear_formulario_ayuda(self, frame, ventana):
        """Formulario de ayuda mejorado"""
        # Notebook para diferentes secciones
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña Guía Rápida
        guia_frame = ttk.Frame(notebook)
        notebook.add(guia_frame, text="Guía Rápida")
        
        guia_texto = """
🔒 CIFRADO DE ARCHIVOS:
1. Selecciona el archivo a cifrar
2. Proporciona la clave pública del receptor
3. Ingresa una contraseña para derivar la clave AES
4. El archivo se cifra con RSA + AES + HMAC

🔓 DESCIFRADO DE ARCHIVOS:
1. Selecciona el archivo cifrado (.bin)
2. Proporciona tu clave privada
3. Ingresa la contraseña usada para cifrar
4. El archivo se descifra y verifica integridad

✂️ FRAGMENTACIÓN (Shamir):
- Divide una clave en múltiples partes
- Solo se necesitan algunas partes para reconstruir
- Útil para respaldos distribuidos

🔐 SEGURIDAD:
- RSA-2048 para claves
- AES-256 para datos
- HMAC para integridad
- PBKDF2 para derivación de claves
        """
        
        text_widget = scrolledtext.ScrolledText(guia_frame, wrap=tk.WORD, height=15, width=70)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        text_widget.insert(tk.END, guia_texto)
        text_widget.config(state=tk.DISABLED)
        
        # Pestaña Casos de Uso
        casos_frame = ttk.Frame(notebook)
        notebook.add(casos_frame, text="Casos de Uso")
        
        casos_texto = """
📰 PERIODISTAS BAJO CENSURA:
- Cifrar documentos sensibles
- Transferir por múltiples canales
- Fragmentar claves para respaldo

⚖️ ACTIVISTAS POLÍTICOS:
- Comunicación segura
- Transferencia anónima
- Protección de identidades

🏢 EMPRESAS CON INFORMACIÓN SENSIBLE:
- Cifrado de documentos
- Transferencia segura
- Auditoría de acceso

👤 USUARIOS QUE QUIEREN PRIVACIDAD:
- Cifrado personal
- Transferencia segura
- Respaldos distribuidos
        """
        
        text_widget2 = scrolledtext.ScrolledText(casos_frame, wrap=tk.WORD, height=15, width=70)
        text_widget2.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        text_widget2.insert(tk.END, casos_texto)
        text_widget2.config(state=tk.DISABLED)
        
        # Botón cerrar
        ttk.Button(frame, text="❌ Cerrar", command=ventana.destroy).pack(pady=(10, 0))
    
    def seleccionar_archivo(self, variable, tipos_archivo=None):
        """Selecciona un archivo con diálogo mejorado"""
        if tipos_archivo:
            archivo = filedialog.askopenfilename(filetypes=tipos_archivo)
        else:
            archivo = filedialog.askopenfilename()
        
        if archivo:
            variable.set(archivo)
            self.log(f"Archivo seleccionado: {os.path.basename(archivo)}")
    
    def ejecutar_cifrado(self, ventana):
        """Ejecuta el cifrado con integración real"""
        if not self.archivo_origen.get():
            messagebox.showerror("Error", "Selecciona un archivo para cifrar")
            return
        
        if not self.clave_publica.get():
            messagebox.showerror("Error", "Selecciona una clave pública")
            return
        
        if not self.password.get():
            messagebox.showerror("Error", "Ingresa una contraseña")
            return
        
        try:
            self.log("Iniciando cifrado...", "info")
            
            if TITANSEND_AVAILABLE:
                # Lógica real de cifrado
                with open(self.archivo_origen.get(), 'rb') as f:
                    datos = f.read()
                
                with open(self.clave_publica.get(), 'rb') as f:
                    pem = f.read()
                
                clave_pub = crypto.deserializar_clave_publica(pem)
                salt = os.urandom(16)
                clave_aes = crypto.generar_clave_aes(self.password.get(), salt)
                
                import time
                timestamp = int(time.time()).to_bytes(8, 'big')
                nonce = os.urandom(8)
                datos_a_cifrar = timestamp + nonce + datos
                
                cifrado = crypto.cifrar_aes(datos_a_cifrar, clave_aes)
                firma = crypto.firmar_hmac(clave_aes, cifrado)
                clave_aes_cifrada = crypto.cifrar_con_publica(clave_pub, clave_aes)
                
                resultado = salt + clave_aes_cifrada + firma + cifrado
                
                # Guardar archivo cifrado
                nombre_base = os.path.splitext(os.path.basename(self.archivo_origen.get()))[0]
                archivo_cifrado = f"{nombre_base}_cifrado.bin"
                
                with open(archivo_cifrado, 'wb') as f:
                    f.write(resultado)
                
                self.log(f"Archivo cifrado guardado como: {archivo_cifrado}", "success")
                messagebox.showinfo("Éxito", f"Archivo cifrado exitosamente\nGuardado como: {archivo_cifrado}")
            else:
                self.log("Modo demo - Simulando cifrado", "warning")
                messagebox.showinfo("Demo", "Modo demo - Archivo simulado como cifrado")
            
            ventana.destroy()
            
        except Exception as e:
            self.log(f"Error al cifrar: {str(e)}", "error")
            messagebox.showerror("Error", f"Error al cifrar: {str(e)}")
    
    def ejecutar_descifrado(self, ventana):
        """Ejecuta el descifrado con integración real"""
        if not self.archivo_origen.get():
            messagebox.showerror("Error", "Selecciona un archivo cifrado")
            return
        
        if not self.clave_privada.get():
            messagebox.showerror("Error", "Selecciona una clave privada")
            return
        
        if not self.password.get():
            messagebox.showerror("Error", "Ingresa la contraseña")
            return
        
        try:
            self.log("Iniciando descifrado...", "info")
            
            if TITANSEND_AVAILABLE:
                # Lógica real de descifrado
                with open(self.archivo_origen.get(), 'rb') as f:
                    datos = f.read()
                
                with open(self.clave_privada.get(), 'rb') as f:
                    pem = f.read()
                
                clave_priv = crypto.deserializar_clave_privada(pem)
                
                salt = datos[:16]
                clave_aes_cifrada = datos[16:16+256]
                firma = datos[16+256:16+256+32]
                cifrado = datos[16+256+32:]
                
                clave_aes = crypto.descifrar_con_privada(clave_priv, clave_aes_cifrada)
                
                if not crypto.verificar_hmac(clave_aes, cifrado, firma):
                    raise ValueError("Firma HMAC inválida. El archivo puede haber sido manipulado.")
                
                descifrado = crypto.descifrar_aes(cifrado, clave_aes)
                datos_final = descifrado[16:]
                
                # Guardar archivo descifrado
                nombre_base = os.path.splitext(os.path.basename(self.archivo_origen.get()))[0]
                archivo_descifrado = f"{nombre_base}_descifrado"
                
                with open(archivo_descifrado, 'wb') as f:
                    f.write(datos_final)
                
                self.log(f"Archivo descifrado guardado como: {archivo_descifrado}", "success")
                messagebox.showinfo("Éxito", f"Archivo descifrado exitosamente\nGuardado como: {archivo_descifrado}")
            else:
                self.log("Modo demo - Simulando descifrado", "warning")
                messagebox.showinfo("Demo", "Modo demo - Archivo simulado como descifrado")
            
            ventana.destroy()
            
        except Exception as e:
            self.log(f"Error al descifrar: {str(e)}", "error")
            messagebox.showerror("Error", f"Error al descifrar: {str(e)}")
    
    def ejecutar_fragmentacion(self, clave, n, k, ventana):
        """Ejecuta la fragmentación Shamir"""
        if not clave:
            messagebox.showerror("Error", "Ingresa una clave para fragmentar")
            return
        
        try:
            n = int(n)
            k = int(k)
            
            if k > n:
                messagebox.showerror("Error", "k no puede ser mayor que n")
                return
            
            self.log("Iniciando fragmentación Shamir...", "info")
            
            if TITANSEND_AVAILABLE:
                fragmentos = shamir_robusto.fragmentar_clave_robusto(clave, n, k)
                
                # Guardar fragmentos
                for i, fragmento in enumerate(fragmentos):
                    with open(f"fragmento_{i+1}.txt", 'w') as f:
                        f.write(fragmento)
                
                self.log(f"Clave fragmentada en {n} partes (umbral: {k})", "success")
                messagebox.showinfo("Éxito", f"Clave fragmentada exitosamente\nGenerados {n} fragmentos\nUmbral: {k}")
            else:
                self.log("Modo demo - Simulando fragmentación", "warning")
                messagebox.showinfo("Demo", "Modo demo - Fragmentación simulada")
            
            ventana.destroy()
            
        except Exception as e:
            self.log(f"Error en fragmentación: {str(e)}", "error")
            messagebox.showerror("Error", f"Error en fragmentación: {str(e)}")
    
    def ejecutar_recuperacion(self, fragmentos_texto, ventana):
        """Ejecuta la recuperación Shamir"""
        fragmentos = [line.strip() for line in fragmentos_texto.split('\n') if line.strip()]
        
        if len(fragmentos) < 2:
            messagebox.showerror("Error", "Se necesitan al menos 2 fragmentos")
            return
        
        try:
            self.log("Iniciando recuperación Shamir...", "info")
            
            if TITANSEND_AVAILABLE:
                clave_recuperada = shamir_robusto.reconstruir_clave_robusto(fragmentos)
                
                # Guardar clave recuperada
                with open("clave_recuperada.txt", 'w') as f:
                    f.write(clave_recuperada)
                
                self.log("Clave recuperada exitosamente", "success")
                messagebox.showinfo("Éxito", f"Clave recuperada exitosamente\nGuardada como: clave_recuperada.txt")
            else:
                self.log("Modo demo - Simulando recuperación", "warning")
                messagebox.showinfo("Demo", "Modo demo - Recuperación simulada")
            
            ventana.destroy()
            
        except Exception as e:
            self.log(f"Error en recuperación: {str(e)}", "error")
            messagebox.showerror("Error", f"Error en recuperación: {str(e)}")
    
    def configurar_tor(self):
        """Configura Tor automáticamente"""
        if TITANSEND_AVAILABLE:
            self.log("Configurando Tor...", "info")
            try:
                resultado = tor_setup.configurar_tor_automatico()
                self.log("Configuración de Tor completada", "success")
                messagebox.showinfo("Tor", "Configuración de Tor completada")
            except Exception as e:
                self.log(f"Error configurando Tor: {str(e)}", "error")
                messagebox.showerror("Error", f"Error configurando Tor: {str(e)}")
        else:
            messagebox.showinfo("Demo", "Función no disponible en modo demo")
    
    def verificar_tor(self):
        """Verifica la conectividad de Tor"""
        if TITANSEND_AVAILABLE:
            self.log("Verificando conectividad Tor...", "info")
            try:
                disponible = tor_setup.verificar_tor_disponible()
                if disponible:
                    self.log("Tor está disponible y funcionando", "success")
                    messagebox.showinfo("Tor", "Tor está disponible y funcionando")
                else:
                    self.log("Tor no está disponible", "warning")
                    messagebox.showwarning("Tor", "Tor no está disponible")
            except Exception as e:
                self.log(f"Error verificando Tor: {str(e)}", "error")
                messagebox.showerror("Error", f"Error verificando Tor: {str(e)}")
        else:
            messagebox.showinfo("Demo", "Función no disponible en modo demo")
    
    def escanear_bluetooth(self):
        """Escanea dispositivos Bluetooth"""
        messagebox.showinfo("Bluetooth", "Función de Bluetooth en desarrollo")
    
    def guardar_configuracion(self, ventana):
        """Guarda la configuración"""
        self.log("Configuración guardada", "success")
        messagebox.showinfo("Configuración", "Configuración guardada exitosamente")
        ventana.destroy()

def main():
    root = tk.Tk()
    app = TitanSendGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 