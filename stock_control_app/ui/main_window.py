import tkinter as tk
from tkinter import ttk, messagebox
import json

from services.dashboard_service import DashboardService
from services.alert_service import AlertService
from ui.product_ui import ProductUI
from ui.movement_ui import MovementUI
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

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exportar CSV", command=self.export_csv)
        file_menu.add_command(label="Importar CSV", command=self.import_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        # Menú Configuración
        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="Configuración", command=self.show_config)
        menubar.add_cascade(label="Configuración", menu=config_menu)

        self.root.config(menu=menubar)

    def show_tab(self, index):
        self.notebook.select(index)
        if index == 0:
            self.load_dashboard()

    def setup_ui(self):
        # Frame principal con barra lateral
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Barra lateral de navegación con iconos PNG y efecto glass
        from PIL import Image, ImageTk
        sidebar = tk.Frame(main_frame, bg="#1a2636", width=80, highlightthickness=0)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        icon_files = [
            "assets/sidebar_dashboard.png",
            "assets/sidebar_products.png",
            "assets/sidebar_movements.png"
        ]
        nav_texts = ["Dashboard", "Productos", "Movimientos"]
        self.nav_buttons = []
        self.nav_icons = []
        for idx, icon_path in enumerate(icon_files):
            try:
                img = Image.open(icon_path).resize((32,32))
                icon = ImageTk.PhotoImage(img)
            except:
                icon = None
            btn = tk.Button(sidebar, image=icon, text=nav_texts[idx], compound=tk.TOP,
                            font=("Segoe UI", 10), fg="#fff", bg="#1a2636", bd=0, relief=tk.FLAT,
                            activebackground="#00aaff", activeforeground="#fff", cursor="hand2",
                            command=lambda i=idx: self.show_tab(i))
            btn.image = icon
            btn.pack(pady=25, padx=10, fill=tk.X, ipadx=10, ipady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#00aaff", fg="#fff"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1a2636", fg="#fff"))
            self.nav_buttons.append(btn)
            self.nav_icons.append(icon)

        # Header con efecto glass y logo
        header = tk.Frame(main_frame, bg="#e9ecef", highlightbackground="#b0c4de", highlightthickness=2)
        header.pack(fill=tk.X, padx=0, pady=(0,0))
        try:
            logo_img = Image.open("logo.png").resize((40,40))
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header, image=logo_photo, bg="#e9ecef")
            logo_label.image = logo_photo
            logo_label.pack(side=tk.LEFT, padx=(10,10), pady=10)
        except:
            logo_label = tk.Label(header, text="🗃️", font=("Segoe UI", 28), bg="#e9ecef")
            logo_label.pack(side=tk.LEFT, padx=(10,10), pady=10)
        tk.Label(header, text="Kraken Inventory", font=("Segoe UI", 20, "bold"), fg="#1a2636", bg="#e9ecef").pack(side=tk.LEFT, pady=10)

        # Frame de contenido principal con fondo glass
        content_frame = tk.Frame(main_frame, bg="#f8fbff", highlightbackground="#b0c4de", highlightthickness=2)
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
    def load_dashboard(self):
        # Limpiar frame del dashboard
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()

        # Obtener datos del dashboard
        stats = DashboardService.get_dashboard_stats()
        low_stock = AlertService.get_low_stock_products()

        # Botón actualizar dashboard
        btn_refresh = ttk.Button(self.dashboard_frame, text="Actualizar", command=self.load_dashboard)
        btn_refresh.pack(anchor=tk.NE, padx=10, pady=5)

        # Tarjetas visuales para estadísticas
        card_frame = tk.Frame(self.dashboard_frame, bg="#e3f2fd", highlightbackground="#b0c4de", highlightthickness=2)
        card_frame.pack(fill=tk.X, padx=10, pady=10)
        def make_card(parent, title, value, color):
            card = tk.Frame(parent, bg=color, bd=0, relief=tk.RIDGE, highlightbackground="#b0c4de", highlightthickness=2)
            card.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)
            tk.Label(card, text=title, font=("Segoe UI", 12, "bold"), bg=color, fg="#1a2636").pack(anchor=tk.W)
            tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), bg=color, fg="#00aaff").pack(anchor=tk.W)

        make_card(card_frame, "Total de productos", stats['total_products'], "#e3f2fd")
        make_card(card_frame, "Valor inventario", f"${stats['total_value']:.2f}", "#e0f7fa")
        make_card(card_frame, "Movimientos hoy", stats['today_movements'], "#fce4ec")
        make_card(card_frame, "Ganancias del día", f"${stats['ganancias_dia']:.2f}", "#e8f5e9")

        # Mostrar mensaje y gráfico de ejemplo si no hay productos
        from services.product_service import ProductService
        products = ProductService.get_all_products()
        if not products:
            msg = tk.Label(self.dashboard_frame, text="No hay productos en la base de datos. Agrega productos para ver estadísticas reales.", font=("Segoe UI", 13, "bold"), fg="#1a2636", bg="#e3f2fd")
            msg.pack(pady=20)
            # Gráfico de ejemplo
            try:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                fig, ax = plt.subplots(figsize=(6,2.5))
                names = ["Ejemplo A", "Ejemplo B", "Ejemplo C"]
                stocks = [10, 5, 8]
                ax.bar(names, stocks, color='#00aaff')
                ax.set_title('Stock por producto (Ejemplo)')
                ax.set_ylabel('Unidades')
                ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
                fig.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=self.dashboard_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.X, padx=10, pady=5)
            except Exception as e:
                ttk.Label(self.dashboard_frame, text=f"Error gráfico: {e}", foreground="red").pack()

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