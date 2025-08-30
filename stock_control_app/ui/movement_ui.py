import tkinter as tk
from tkinter import ttk

class MovementUI:
	def __init__(self, parent, read_only=False):
		self.frame = ttk.Frame(parent)
		label = ttk.Label(self.frame, text="Movimientos")
		label.pack(padx=10, pady=10)

		self.setup_filters()

		btn_frame = ttk.Frame(self.frame)
		btn_frame.pack(fill=tk.X, padx=10, pady=5)
		btn_nuevo = ttk.Button(btn_frame, text="Nuevo movimiento", command=self.open_new_movement)
		btn_nuevo.pack(side=tk.LEFT, padx=2)
		btn_editar = ttk.Button(btn_frame, text="Editar movimiento", command=self.edit_selected_movement)
		btn_editar.pack(side=tk.LEFT, padx=2)
		btn_eliminar = ttk.Button(btn_frame, text="Eliminar movimiento", command=self.delete_selected_movement)
		btn_eliminar.pack(side=tk.LEFT, padx=2)

		# Tabla de movimientos
		self.tree = ttk.Treeview(self.frame, columns=("id", "producto", "tipo", "cantidad", "fecha"), show="headings")
		self.tree.heading("id", text="ID")
		self.tree.heading("producto", text="Producto")
		self.tree.heading("tipo", text="Tipo")
		self.tree.heading("cantidad", text="Cantidad")
		self.tree.heading("fecha", text="Fecha")
		self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

		self.tree.bind("<Button-3>", self.show_context_menu)

		self.load_movements()

		# Menú contextual
		self.menu = tk.Menu(self.frame, tearoff=0)
		self.menu.add_command(label="Editar movimiento", command=self.edit_selected_movement)
		self.menu.add_command(label="Eliminar movimiento", command=self.delete_selected_movement)
		self.menu.add_separator()
		self.menu.add_command(label="Ver detalles", command=self.show_movement_details)
		self.menu.add_command(label="Duplicar movimiento", command=self.duplicate_selected_movement)

	def setup_filters(self):
		filter_frame = ttk.LabelFrame(self.frame, text="Filtros de movimientos")
		filter_frame.pack(fill=tk.X, padx=10, pady=5)
		# Fecha inicio
		self.start_date_var = tk.StringVar()
		self.end_date_var = tk.StringVar()
		self.type_var = tk.StringVar()
		self.product_var = tk.StringVar()
		
		ttk.Label(filter_frame, text="Desde:").grid(row=0, column=0, padx=5, pady=2)
		self.start_date_entry = ttk.Entry(filter_frame, textvariable=self.start_date_var, width=12)
		self.start_date_entry.grid(row=0, column=1, padx=5, pady=2)
		ttk.Label(filter_frame, text="Hasta:").grid(row=0, column=2, padx=5, pady=2)
		self.end_date_entry = ttk.Entry(filter_frame, textvariable=self.end_date_var, width=12)
		self.end_date_entry.grid(row=0, column=3, padx=5, pady=2)
		ttk.Label(filter_frame, text="Tipo:").grid(row=0, column=4, padx=5, pady=2)
		type_combo = ttk.Combobox(filter_frame, textvariable=self.type_var, values=["", "in", "out"], state="readonly", width=8)
		type_combo.grid(row=0, column=5, padx=5, pady=2)
		ttk.Label(filter_frame, text="Producto:").grid(row=0, column=6, padx=5, pady=2)
		self.product_entry = ttk.Entry(filter_frame, textvariable=self.product_var, width=15)
		self.product_entry.grid(row=0, column=7, padx=5, pady=2)
		ttk.Button(filter_frame, text="Aplicar filtros", command=self.apply_filters).grid(row=0, column=8, padx=10, pady=2)
		ttk.Button(filter_frame, text="Exportar CSV", command=self.export_movements_csv).grid(row=0, column=9, padx=10, pady=2)

	def load_movements(self):
		from services.movement_service import MovementService
		movimientos = MovementService.get_all_movements()
		movimientos = [dict(m) if not isinstance(m, dict) else m for m in movimientos]
		self.tree.delete(*self.tree.get_children())
		for m in movimientos:
			nombre = m.get("name") if m.get("name") is not None else "Producto eliminado"
			self.tree.insert("", "end", values=(m.get("id"), nombre, m.get("type"), m.get("quantity"), m.get("created_at")))

	def show_context_menu(self, event):
		row_id = self.tree.identify_row(event.y)
		if row_id:
			self.tree.selection_set(row_id)
			self.context_movement_id = int(self.tree.item(row_id, 'values')[0])
		else:
			self.context_movement_id = None
		self.menu.tk_popup(event.x_root, event.y_root)

	def get_selected_movement_id(self):
		# Prioriza el id del menú contextual si existe
		if hasattr(self, 'context_movement_id') and self.context_movement_id:
			return self.context_movement_id
		selected = self.tree.selection()
		if not selected:
			return None
		return int(self.tree.item(selected[0], 'values')[0])

	def edit_selected_movement(self):
		movement_id = self.get_selected_movement_id()
		if not movement_id:
			tk.messagebox.showwarning("Advertencia", "Selecciona un movimiento para editar")
			return
		from services.movement_service import MovementService
		movimiento = MovementService.get_all_movements()
		movimiento = [dict(m) if not isinstance(m, dict) else m for m in movimiento]
		movimiento = [m for m in movimiento if m.get("id") == movement_id]
		if not movimiento:
			tk.messagebox.showerror("Error", "Movimiento no encontrado")
			return
		movimiento = movimiento[0]
		self.open_edit_movement(movement_id, movimiento)

	def open_edit_movement(self, movement_id, movimiento):
		import tkinter.messagebox as messagebox
		from services.movement_service import MovementService
		from services.product_service import ProductService
		win = tk.Toplevel(self.frame)
		win.title("Editar movimiento")
		win.geometry("400x400")
		productos = ProductService.get_all_products()
		productos = [dict(p) if not isinstance(p, dict) else p for p in productos]
		producto_names = [f"{p['name']} (ID:{p['id']})" for p in productos]
		ttk.Label(win, text="Producto:").pack(pady=5)
		producto_var = tk.StringVar()
		producto_combo = ttk.Combobox(win, textvariable=producto_var, values=producto_names, state="readonly")
		producto_combo.pack(pady=5)
		idx_actual = next((i for i, p in enumerate(productos) if p['id'] == movimiento['product_id']), 0)
		producto_combo.current(idx_actual)
		ttk.Label(win, text="Tipo:").pack(pady=5)
		tipo_var = tk.StringVar()
		tipo_combo = ttk.Combobox(win, textvariable=tipo_var, values=["in", "out"], state="readonly")
		tipo_combo.pack(pady=5)
		tipo_combo.set(movimiento['type'])
		ttk.Label(win, text="Cantidad:").pack(pady=5)
		cantidad_var = tk.StringVar(value=str(movimiento['quantity']))
		entry_cantidad = ttk.Entry(win, textvariable=cantidad_var)
		entry_cantidad.pack(pady=5)
		ttk.Label(win, text="Motivo:").pack(pady=5)
		motivo_var = tk.StringVar(value=movimiento.get('reason', ''))
		entry_motivo = ttk.Entry(win, textvariable=motivo_var)
		entry_motivo.pack(pady=5)
		ttk.Label(win, text="Notas:").pack(pady=5)
		notas_var = tk.StringVar(value=movimiento.get('notes', ''))
		entry_notas = ttk.Entry(win, textvariable=notas_var)
		entry_notas.pack(pady=5)
		def guardar():
			if not producto_var.get() or not tipo_var.get() or not cantidad_var.get():
				messagebox.showerror("Error", "Completa todos los campos obligatorios.")
				return
			try:
				cantidad = int(cantidad_var.get())
			except ValueError:
				messagebox.showerror("Error", "La cantidad debe ser un número entero.")
				return
			idx = producto_combo.current()
			if idx < 0:
				messagebox.showerror("Error", "Selecciona un producto válido.")
				return
			producto_id = productos[idx]['id']
			movimiento_data = {
				"product_id": producto_id,
				"type": tipo_var.get(),
				"quantity": cantidad,
				"reason": motivo_var.get(),
				"notes": notas_var.get()
			}
			success, msg = MovementService.edit_movement(movement_id, movimiento_data)
			if success:
				messagebox.showinfo("Éxito", msg)
				win.destroy()
				self.load_movements()
				try:
					parent = self.frame.master
					if hasattr(parent, 'load_dashboard'):
						parent.load_dashboard()
					if hasattr(parent, 'product_ui') and hasattr(parent.product_ui, 'load_products'):
						parent.product_ui.load_products()
				except Exception:
					pass
			else:
				messagebox.showerror("Error", msg)
		ttk.Button(win, text="Guardar cambios", command=guardar).pack(pady=20)

	def delete_selected_movement(self):
		movement_id = self.get_selected_movement_id()
		if not movement_id:
			tk.messagebox.showwarning("Advertencia", "Selecciona un movimiento para eliminar")
			return
		import tkinter.messagebox as messagebox
		if not messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este movimiento?"):
			return
		from services.movement_service import MovementService
		success, msg = MovementService.delete_movement(movement_id)
		if success:
			messagebox.showinfo("Éxito", msg)
			self.load_movements()
			try:
				parent = self.frame.master
				if hasattr(parent, 'load_dashboard'):
					parent.load_dashboard()
				if hasattr(parent, 'product_ui') and hasattr(parent.product_ui, 'load_products'):
					parent.product_ui.load_products()
			except Exception:
				pass
		else:
			messagebox.showerror("Error", msg)

	def show_movement_details(self):
		movement_id = self.get_selected_movement_id()
		if not movement_id:
			tk.messagebox.showwarning("Advertencia", "Selecciona un movimiento para ver detalles")
			return
		from services.movement_service import MovementService
		movimiento = MovementService.get_all_movements()
		movimiento = [dict(m) if not isinstance(m, dict) else m for m in movimiento]
		movimiento = [m for m in movimiento if m.get("id") == movement_id]
		if not movimiento:
			tk.messagebox.showerror("Error", "Movimiento no encontrado")
			return
		movimiento = movimiento[0]
		nombre = movimiento.get('name') if movimiento.get('name') is not None else 'Producto eliminado'
		detalles = f"ID: {movimiento['id']}\nProducto: {nombre}\nTipo: {movimiento['type']}\nCantidad: {movimiento['quantity']}\nFecha: {movimiento['created_at']}\nMotivo: {movimiento.get('reason', '')}\nNotas: {movimiento.get('notes', '')}"
		tk.messagebox.showinfo("Detalles del movimiento", detalles)

	def duplicate_selected_movement(self):
		movement_id = self.get_selected_movement_id()
		if not movement_id:
			tk.messagebox.showwarning("Advertencia", "Selecciona un movimiento para duplicar")
			return
		from services.movement_service import MovementService
		movimiento = MovementService.get_all_movements()
		movimiento = [dict(m) if not isinstance(m, dict) else m for m in movimiento]
		movimiento = [m for m in movimiento if m.get("id") == movement_id]
		if not movimiento:
			tk.messagebox.showerror("Error", "Movimiento no encontrado")
			return
		movimiento = movimiento[0]
		movimiento_data = {
			"product_id": movimiento["product_id"],
			"type": movimiento["type"],
			"quantity": movimiento["quantity"],
			"reason": movimiento.get("reason", "Duplicado"),
			"notes": movimiento.get("notes", "")
		}
		success, msg = MovementService.create_movement(movimiento_data)
		if success:
			tk.messagebox.showinfo("Éxito", "Movimiento duplicado correctamente")
			self.load_movements()
			try:
				parent = self.frame.master
				if hasattr(parent, 'load_dashboard'):
					parent.load_dashboard()
				if hasattr(parent, 'product_ui') and hasattr(parent.product_ui, 'load_products'):
					parent.product_ui.load_products()
			except Exception:
				pass
		else:
			tk.messagebox.showerror("Error", msg)

	def open_new_movement(self):
		import tkinter.messagebox as messagebox
		from services.product_service import ProductService
		from services.movement_service import MovementService

		win = tk.Toplevel(self.frame)
		win.title("Registrar movimiento")
		win.geometry("400x400")

		# Obtener productos
		productos = ProductService.get_all_products()
		productos = [dict(p) if not isinstance(p, dict) else p for p in productos]
		producto_names = [f"{p['name']} (ID:{p['id']})" for p in productos]

		ttk.Label(win, text="Producto:").pack(pady=5)
		producto_var = tk.StringVar()
		producto_combo = ttk.Combobox(win, textvariable=producto_var, values=producto_names, state="readonly")
		producto_combo.pack(pady=5)

		ttk.Label(win, text="Tipo:").pack(pady=5)
		tipo_var = tk.StringVar()
		tipo_combo = ttk.Combobox(win, textvariable=tipo_var, values=["in", "out"], state="readonly")
		tipo_combo.pack(pady=5)

		ttk.Label(win, text="Cantidad:").pack(pady=5)
		cantidad_var = tk.StringVar()
		entry_cantidad = ttk.Entry(win, textvariable=cantidad_var)
		entry_cantidad.pack(pady=5)

		ttk.Label(win, text="Motivo:").pack(pady=5)
		motivo_var = tk.StringVar()
		entry_motivo = ttk.Entry(win, textvariable=motivo_var)
		entry_motivo.pack(pady=5)

		ttk.Label(win, text="Notas:").pack(pady=5)
		notas_var = tk.StringVar()
		entry_notas = ttk.Entry(win, textvariable=notas_var)
		entry_notas.pack(pady=5)

		def guardar():
			# Validar datos
			if not producto_var.get() or not tipo_var.get() or not cantidad_var.get():
				messagebox.showerror("Error", "Completa todos los campos obligatorios.")
				return
			try:
				cantidad = int(cantidad_var.get())
			except ValueError:
				messagebox.showerror("Error", "La cantidad debe ser un número entero.")
				return
			# Obtener ID de producto
			idx = producto_combo.current()
			if idx < 0:
				messagebox.showerror("Error", "Selecciona un producto válido.")
				return
			producto_id = productos[idx]['id']
			movimiento = {
				"product_id": producto_id,
				"type": tipo_var.get(),
				"quantity": cantidad,
				"reason": motivo_var.get(),
				"notes": notas_var.get()
			}
			success, msg = MovementService.create_movement(movimiento)
			if success:
				messagebox.showinfo("Éxito", msg)
				win.destroy()
				# Actualizar dashboard si existe
				try:
					parent = self.frame.master
					if hasattr(parent, 'load_dashboard'):
						parent.load_dashboard()
					# Actualizar productos si existe
					if hasattr(parent, 'product_ui') and hasattr(parent.product_ui, 'load_products'):
						parent.product_ui.load_products()
				except Exception:
					pass
				# Refrescar tabla de movimientos
				self.load_movements()
			else:
				messagebox.showerror("Error", msg)

		ttk.Button(win, text="Guardar", command=guardar).pack(pady=20)

	def apply_filters(self):
		from services.movement_service import MovementService
		movimientos = MovementService.get_all_movements()
		movimientos = [dict(m) if not isinstance(m, dict) else m for m in movimientos]
		start = self.start_date_var.get().strip()
		end = self.end_date_var.get().strip()
		tipo = self.type_var.get().strip()
		producto = self.product_var.get().strip().lower()
		filtered = []
		for m in movimientos:
			fecha = m.get("created_at", "")[:10]
			if start and fecha < start:
				continue
			if end and fecha > end:
				continue
			if tipo and m.get("type") != tipo:
				continue
			nombre = m.get("name") if m.get("name") is not None else "Producto eliminado"
			if producto and producto not in nombre.lower():
				continue
			filtered.append(m)
		self.tree.delete(*self.tree.get_children())
		for m in filtered:
			nombre = m.get("name") if m.get("name") is not None else "Producto eliminado"
			row = self.tree.insert("", "end", values=(m.get("id"), nombre, m.get("type"), m.get("quantity"), m.get("created_at")))
			if nombre == "Producto eliminado":
				self.tree.item(row, tags=("eliminado",))
		self.tree.tag_configure("eliminado", background="#ffe0e0")

	def export_movements_csv(self):
		import csv
		from tkinter import filedialog
		file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
		if not file_path:
			return
		rows = self.tree.get_children()
		with open(file_path, "w", newline='', encoding='utf-8') as f:
			writer = csv.writer(f)
			writer.writerow(["ID", "Producto", "Tipo", "Cantidad", "Fecha"])
			for row in rows:
				vals = self.tree.item(row, 'values')
				writer.writerow(vals)
		import tkinter.messagebox as messagebox
		messagebox.showinfo("Exportación", f"Movimientos exportados a {file_path}")
