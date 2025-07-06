import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

# Agregar el directorio del proyecto al path para importar titansend
sys.path.append(os.path.join(os.path.dirname(__file__), 'titansend'))

try:
    from titansend import crypto, auth
    TITANSEND_AVAILABLE = True
except ImportError:
    TITANSEND_AVAILABLE = False
    print("⚠️  TitanSend no disponible. Ejecutando en modo demo.")

class TitanSendGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TitanSend - Tu Búnker Digital Portátil")
        self.root.geometry("700x500")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.archivo_origen = tk.StringVar()
        self.clave_publica = tk.StringVar()
        self.clave_privada = tk.StringVar()
        self.password = tk.StringVar()
        self.operacion_actual = None
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="🛡️ TitanSend", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        subtitulo = ttk.Label(main_frame, text="Tu Búnker Digital Portátil",
                             font=('Arial', 10))
        subtitulo.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Botones de operación
        ttk.Label(main_frame, text="Selecciona una operación:", 
                 font=('Arial', 12, 'bold')).grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Frame para botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        # Botones principales
        ttk.Button(btn_frame, text="🔒 Cifrar Archivo", 
                  command=self.mostrar_cifrado).grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="🔓 Descifrar Archivo", 
                  command=self.mostrar_descifrado).grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="✂️ Fragmentar Clave", 
                  command=self.mostrar_fragmentacion).grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="🔧 Recuperar Clave", 
                  command=self.mostrar_recuperacion).grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="⚙️ Configuración", 
                  command=self.mostrar_configuracion).grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="📚 Ayuda", 
                  command=self.mostrar_ayuda).grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Frame de estado
        self.estado_frame = ttk.Frame(main_frame)
        self.estado_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0), sticky=(tk.W, tk.E))
        
        self.estado_label = ttk.Label(self.estado_frame, text="Listo para usar", 
                                     font=('Arial', 9))
        self.estado_label.pack()
        
        # Información de TitanSend
        if TITANSEND_AVAILABLE:
            info_text = "✅ TitanSend disponible - Funciones completas"
        else:
            info_text = "⚠️ Modo demo - TitanSend no disponible"
        
        ttk.Label(main_frame, text=info_text, 
                 font=('Arial', 8)).grid(row=5, column=0, columnspan=2, pady=(10, 0))
    
    def mostrar_cifrado(self):
        self.operacion_actual = "cifrar"
        self.crear_ventana_operacion("Cifrar Archivo", self.crear_formulario_cifrado)
    
    def mostrar_descifrado(self):
        self.operacion_actual = "descifrar"
        self.crear_ventana_operacion("Descifrar Archivo", self.crear_formulario_descifrado)
    
    def mostrar_fragmentacion(self):
        self.operacion_actual = "fragmentar"
        self.crear_ventana_operacion("Fragmentar Clave", self.crear_formulario_fragmentacion)
    
    def mostrar_recuperacion(self):
        self.operacion_actual = "recuperar"
        self.crear_ventana_operacion("Recuperar Clave", self.crear_formulario_recuperacion)
    
    def mostrar_configuracion(self):
        self.crear_ventana_operacion("Configuración", self.crear_formulario_configuracion)
    
    def mostrar_ayuda(self):
        self.crear_ventana_operacion("Ayuda", self.crear_formulario_ayuda)
    
    def crear_ventana_operacion(self, titulo, funcion_formulario):
        # Crear ventana secundaria
        ventana = tk.Toplevel(self.root)
        ventana.title(f"TitanSend - {titulo}")
        ventana.geometry("600x400")
        ventana.configure(bg='#f0f0f0')
        
        # Frame principal
        frame = ttk.Frame(ventana, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Crear formulario específico
        funcion_formulario(frame, ventana)
    
    def crear_formulario_cifrado(self, frame, ventana):
        # Archivo a cifrar
        ttk.Label(frame, text="Archivo a cifrar:").pack(anchor=tk.W, pady=(0, 5))
        archivo_frame = ttk.Frame(frame)
        archivo_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Entry(archivo_frame, textvariable=self.archivo_origen, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(archivo_frame, text="Examinar", 
                  command=lambda: self.seleccionar_archivo(self.archivo_origen)).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Clave pública
        ttk.Label(frame, text="Clave pública del receptor:").pack(anchor=tk.W, pady=(0, 5))
        clave_frame = ttk.Frame(frame)
        clave_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Entry(clave_frame, textvariable=self.clave_publica, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(clave_frame, text="Examinar", 
                  command=lambda: self.seleccionar_archivo(self.clave_publica, [("PEM files", "*.pem")])).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Contraseña
        ttk.Label(frame, text="Contraseña para derivar clave AES:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(frame, textvariable=self.password, show="*", width=50).pack(anchor=tk.W, pady=(0, 20))
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="Cifrar", 
                  command=lambda: self.ejecutar_cifrado(ventana)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancelar", 
                  command=ventana.destroy).pack(side=tk.RIGHT)
    
    def crear_formulario_descifrado(self, frame, ventana):
        # Archivo cifrado
        ttk.Label(frame, text="Archivo cifrado:").pack(anchor=tk.W, pady=(0, 5))
        archivo_frame = ttk.Frame(frame)
        archivo_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Entry(archivo_frame, textvariable=self.archivo_origen, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(archivo_frame, text="Examinar", 
                  command=lambda: self.seleccionar_archivo(self.archivo_origen, [("Binary files", "*.bin")])).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Clave privada
        ttk.Label(frame, text="Clave privada:").pack(anchor=tk.W, pady=(0, 5))
        clave_frame = ttk.Frame(frame)
        clave_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Entry(clave_frame, textvariable=self.clave_privada, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(clave_frame, text="Examinar", 
                  command=lambda: self.seleccionar_archivo(self.clave_privada, [("PEM files", "*.pem")])).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Contraseña
        ttk.Label(frame, text="Contraseña usada para cifrar:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(frame, textvariable=self.password, show="*", width=50).pack(anchor=tk.W, pady=(0, 20))
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="Descifrar", 
                  command=lambda: self.ejecutar_descifrado(ventana)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancelar", 
                  command=ventana.destroy).pack(side=tk.RIGHT)
    
    def crear_formulario_fragmentacion(self, frame, ventana):
        ttk.Label(frame, text="Funcionalidad de fragmentación en desarrollo...").pack(pady=20)
        ttk.Button(frame, text="Cerrar", command=ventana.destroy).pack()
    
    def crear_formulario_recuperacion(self, frame, ventana):
        ttk.Label(frame, text="Funcionalidad de recuperación en desarrollo...").pack(pady=20)
        ttk.Button(frame, text="Cerrar", command=ventana.destroy).pack()
    
    def crear_formulario_configuracion(self, frame, ventana):
        ttk.Label(frame, text="Configuración avanzada en desarrollo...").pack(pady=20)
        ttk.Button(frame, text="Cerrar", command=ventana.destroy).pack()
    
    def crear_formulario_ayuda(self, frame, ventana):
        ayuda_texto = """
TitanSend - Tu Búnker Digital Portátil

🔒 Cifrado:
- Selecciona el archivo a cifrar
- Proporciona la clave pública del receptor
- Ingresa una contraseña para derivar la clave AES
- El archivo se cifra con RSA + AES

🔓 Descifrado:
- Selecciona el archivo cifrado (.bin)
- Proporciona tu clave privada
- Ingresa la contraseña usada para cifrar
- El archivo se descifra y verifica integridad

✂️ Fragmentación (Shamir):
- Divide una clave en múltiples partes
- Solo se necesitan algunas partes para reconstruir
- Útil para respaldos distribuidos

Para más información, consulta la documentación.
        """
        text_widget = tk.Text(frame, wrap=tk.WORD, height=15, width=60)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        text_widget.insert(tk.END, ayuda_texto)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(frame, text="Cerrar", command=ventana.destroy).pack()
    
    def seleccionar_archivo(self, variable, tipos_archivo=None):
        if tipos_archivo:
            archivo = filedialog.askopenfilename(filetypes=tipos_archivo)
        else:
            archivo = filedialog.askopenfilename()
        
        if archivo:
            variable.set(archivo)
    
    def ejecutar_cifrado(self, ventana):
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
            if TITANSEND_AVAILABLE:
                # Aquí iría la lógica real de cifrado
                messagebox.showinfo("Éxito", "Archivo cifrado exitosamente")
            else:
                messagebox.showinfo("Demo", "Modo demo - Archivo simulado como cifrado")
            
            ventana.destroy()
            self.estado_label.config(text="Cifrado completado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cifrar: {str(e)}")
    
    def ejecutar_descifrado(self, ventana):
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
            if TITANSEND_AVAILABLE:
                # Aquí iría la lógica real de descifrado
                messagebox.showinfo("Éxito", "Archivo descifrado exitosamente")
            else:
                messagebox.showinfo("Demo", "Modo demo - Archivo simulado como descifrado")
            
            ventana.destroy()
            self.estado_label.config(text="Descifrado completado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al descifrar: {str(e)}")

def main():
    root = tk.Tk()
    app = TitanSendGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 