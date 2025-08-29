import tkinter as tk
from tkinter import ttk, messagebox
import json

from services.dashboard_service import DashboardService
from services.alert_service import AlertService
from ui.product_ui import ProductUI
from ui.movement_ui import MovementUI


class MainWindow:
    def __init__(self, root, config, read_only=False):
        self.root = root
        self.config = config
        self.read_only = read_only

        # Estilo moderno
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#f5f5f5")
        style.configure("TFrame", background="#f5f5f5", relief="flat")
        style.configure("TLabel", background="#f5f5f5", font=("Segoe UI", 11))
        style.configure("TLabelFrame", background="#e9ecef", font=("Segoe UI", 12, "bold"), borderwidth=2, relief="groove")
        style.configure("TButton", font=("Segoe UI", 10), borderwidth=0, relief="flat")
        style.map("TButton",
            background=[('active', '#00aaff'), ('!active', '#e9ecef')],
            foreground=[('active', '#fff'), ('!active', '#2d3e50')]
        )

        self.setup_ui()
        self.load_dashboard()
        self.check_alerts()
        
    def setup_ui(self):
        # Frame principal con barra lateral
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Barra lateral de navegación
        sidebar = tk.Frame(main_frame, bg="#2d3e50", width=70, highlightthickness=0)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Iconos para navegación (puedes reemplazar por imágenes PNG si lo deseas)
        nav_icons = [
            ("🏠", "Dashboard"),
            ("📦", "Productos"),
            ("🔄", "Movimientos")
        ]
        self.nav_buttons = []
        for idx, (icon, text) in enumerate(nav_icons):
            btn = tk.Button(sidebar, text=icon, font=("Segoe UI", 22), fg="#fff", bg="#2d3e50", bd=0, relief=tk.FLAT,
                            activebackground="#00aaff", activeforeground="#fff", cursor="hand2",
                            command=lambda i=idx: self.show_tab(i))
            btn.pack(pady=20, padx=10, fill=tk.X, ipadx=10, ipady=10)
            # Bordes redondeados y sombra (simulada)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#00aaff", fg="#fff"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#2d3e50", fg="#fff"))
            self.nav_buttons.append(btn)

        # Header con logo y nombre de empresa
        header = tk.Frame(main_frame, bg="#e9ecef", highlightbackground="#d1d5db", highlightthickness=2)
        header.pack(fill=tk.X, padx=0, pady=(0,0))
        try:
            from PIL import Image, ImageTk
            logo_img = Image.open("logo.png")
            logo_img = logo_img.resize((40,40))
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header, image=logo_photo, bg="#e9ecef")
            logo_label.image = logo_photo
            logo_label.pack(side=tk.LEFT, padx=(10,10), pady=10)
        except:
            logo_label = tk.Label(header, text="🗃️", font=("Segoe UI", 28), bg="#e9ecef")
            logo_label.pack(side=tk.LEFT, padx=(10,10), pady=10)
        tk.Label(header, text="Sistema de Control de Stock", font=("Segoe UI", 18, "bold"), fg="#2c3e50", bg="#e9ecef").pack(side=tk.LEFT, pady=10)

        # Frame de contenido principal
        content_frame = tk.Frame(main_frame, bg="#f5f5f5", highlightbackground="#d1d5db", highlightthickness=2)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Notebook para pestañas (oculto, controlado por barra lateral)
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Pestaña Dashboard
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")

        # Pestaña Productos
        self.product_ui = ProductUI(self.notebook, self.read_only)
        self.notebook.add(self.product_ui.frame, text="Productos")

        # Pestaña Movimientos
        self.movement_ui = MovementUI(self.notebook, self.read_only)
        self.notebook.add(self.movement_ui.frame, text="Movimientos")

        # Barra de estado mejorada
        self.status_bar = ttk.Label(self.root, text="Listo", relief=tk.SUNKEN, anchor=tk.W, background="#e9ecef", font=("Segoe UI", 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Menú
        self.setup_menu()

    def show_tab(self, index):
        self.notebook.select(index)
        # Efecto visual en barra lateral
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.config(bg="#00aaff", fg="#fff")
            else:
                btn.config(bg="#2d3e50", fg="#fff")
        
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar CSV", command=self.export_csv)
        file_menu.add_command(label="Importar CSV", command=self.import_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)

        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Configuración", command=self.show_config)
        tools_menu.add_separator()
        tools_menu.add_command(label="Backup BD", command=self.backup_db)
        tools_menu.add_command(label="Restaurar BD", command=self.restore_db)

    def backup_db(self):
        import shutil
        from tkinter import filedialog
        src = "stock_control.db"
        file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite DB", "*.db")])
        if not file_path:
            return
        try:
            shutil.copy(src, file_path)
            self.status_bar.config(text=f"Backup realizado: {file_path}")
        except Exception as e:
            self.status_bar.config(text=f"Error backup: {e}")

    def restore_db(self):
        import shutil
        from tkinter import filedialog, messagebox
        file_path = filedialog.askopenfilename(filetypes=[("SQLite DB", "*.db")])
        if not file_path:
            return
        try:
            shutil.copy(file_path, "stock_control.db")
            self.status_bar.config(text=f"Restauración exitosa desde: {file_path}")
            messagebox.showinfo("Restauración", "La base de datos fue restaurada correctamente. Reinicia la aplicación para ver los cambios.")
        except Exception as e:
            self.status_bar.config(text=f"Error restauración: {e}")
        
    def load_dashboard(self):
        # Limpiar frame del dashboard
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()

        # Obtener datos del dashboard
        stats = DashboardService.get_dashboard_stats()
        low_stock = AlertService.get_low_stock_products()

        # Mostrar estadísticas
        stats_frame = ttk.LabelFrame(self.dashboard_frame, text="Estadísticas")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(stats_frame, text=f"Total de productos: {stats['total_products']}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text=f"Valor total de inventario: ${stats['total_value']:.2f}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text=f"Movimientos hoy: {stats['today_movements']}").pack(anchor=tk.W, padx=5, pady=2)

        # Reporte gráfico: stock por producto
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from services.product_service import ProductService
            products = ProductService.get_all_products()
            if products:
                fig, ax = plt.subplots(figsize=(6,2.5))
                names = [p['name'] for p in products]
                stocks = [p['current_stock'] for p in products]
                ax.bar(names, stocks, color='#00aaff')
                ax.set_title('Stock por producto')
                ax.set_ylabel('Unidades')
                ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
                fig.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=self.dashboard_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.X, padx=10, pady=5)
        except Exception as e:
            ttk.Label(self.dashboard_frame, text=f"Error gráfico: {e}", foreground="red").pack()

        # Reporte gráfico: productos por categoría (pastel)
        try:
            from collections import Counter
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            products = ProductService.get_all_products()
            if products:
                categories = [p['category'] for p in products]
                counter = Counter(categories)
                fig2, ax2 = plt.subplots(figsize=(3,2.5))
                ax2.pie(counter.values(), labels=counter.keys(), autopct='%1.1f%%', colors=plt.cm.Paired.colors)
                ax2.set_title('Distribución por categoría')
                fig2.tight_layout()
                canvas2 = FigureCanvasTkAgg(fig2, master=self.dashboard_frame)
                canvas2.draw()
                canvas2.get_tk_widget().pack(side=tk.LEFT, padx=10, pady=5)
        except Exception as e:
            ttk.Label(self.dashboard_frame, text=f"Error gráfico: {e}", foreground="red").pack()

        # Mostrar alertas de stock bajo
        if low_stock:
            alerts_frame = ttk.LabelFrame(self.dashboard_frame, text="Alertas de Stock Bajo")
            alerts_frame.pack(fill=tk.X, padx=10, pady=5)

            for product in low_stock:
                alert_text = f"{product['name']} ({product['code']}): {product['current_stock']} unidades (mínimo: {product['min_stock']})"
                ttk.Label(alerts_frame, text=alert_text, foreground="red").pack(anchor=tk.W, padx=5, pady=2)
    
    def check_alerts(self):
        low_stock = AlertService.get_low_stock_products()
        if low_stock:
            messagebox.showwarning("Alertas de Stock", 
                                  f"{len(low_stock)} productos tienen stock bajo el mínimo")
    
    def export_csv(self):
        import csv
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        from services.product_service import ProductService
        products = ProductService.get_all_products()
        with open(file_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Código", "Nombre", "Descripción", "Categoría", "Stock", "Stock Mínimo", "Stock Máximo", "Costo", "Precio"])
            for p in products:
                writer.writerow([
                    p["id"], p["code"], p["name"], p["description"], p["category"],
                    p["current_stock"], p["min_stock"], p["max_stock"], p["cost"], p["price"]
                ])
        self.status_bar.config(text=f"Exportación exitosa: {file_path}")

    def import_csv(self):
        import csv
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        from services.product_service import ProductService
        with open(file_path, "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                product_data = {
                    "code": row["Código"],
                    "name": row["Nombre"],
                    "description": row["Descripción"],
                    "category": row["Categoría"],
                    "current_stock": int(row["Stock"]),
                    "min_stock": int(row["Stock Mínimo"]),
                    "max_stock": int(row["Stock Máximo"]),
                    "cost": float(row["Costo"]),
                    "price": float(row["Precio"])
                }
                success, _ = ProductService.create_product(product_data)
                if success:
                    count += 1
        self.status_bar.config(text=f"Importados {count} productos desde CSV")
    
    def show_config(self):
        # Implementar diálogo de configuración
        pass