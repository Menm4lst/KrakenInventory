class DashboardService:
	@staticmethod
	def get_dashboard_stats():
		from services.product_service import ProductService
		from services.movement_service import MovementService
		products = ProductService.get_all_products()
		products = [dict(p) if not isinstance(p, dict) else p for p in products]
		products_by_id = {p['id']: p for p in products}
		total_products = len(products)
		total_value = sum(p.get('price', 0) * p.get('current_stock', 0) for p in products)
		# Calcular ganancias del día
		try:
			from datetime import datetime
			today = datetime.now().strftime('%Y-%m-%d')
			movements = MovementService.get_movements_by_date_range(today, today)
			movements = [dict(m) if not isinstance(m, dict) else m for m in movements]
			today_movements = len(movements)
			ganancias_dia = 0.0
			for m in movements:
				if m.get('type') == 'out':
					prod = products_by_id.get(m.get('product_id'))
					if prod:
						precio = prod.get('price', 0)
						costo = prod.get('cost', 0)
						cantidad = m.get('quantity', 0)
						ganancias_dia += (precio - costo) * cantidad
		except Exception:
			today_movements = 0
			ganancias_dia = 0.0
		# Si no hay productos, mostrar datos de ejemplo
		if total_products == 0:
			return {
				'total_products': 3,
				'total_value': 1500.0,
				'today_movements': 2,
				'ganancias_dia': 300.0
			}
		return {
			'total_products': total_products,
			'total_value': total_value,
			'today_movements': today_movements,
			'ganancias_dia': ganancias_dia
		}
