from data.repositories import MovementRepository, ProductRepository


class MovementService:
    @staticmethod
    def get_all_movements():
        return MovementRepository.get_all()

    @staticmethod
    def create_movement(movement_data):
        # Verificar que el producto existe
        product = ProductRepository.get_by_id(movement_data["product_id"])
        if not product:
            return False, "Producto no encontrado"
        # Calcular cambio de stock
        quantity_change = movement_data["quantity"]
        if movement_data["type"] == "out":
            quantity_change = -quantity_change
        # Verificar que el stock no sea negativo
        if product["current_stock"] + quantity_change < 0:
            return False, "Stock insuficiente para este movimiento"
        # Crear movimiento
        MovementRepository.create(movement_data)
        # Actualizar stock del producto
        new_stock = product["current_stock"] + quantity_change
        ProductRepository.update_stock(movement_data["product_id"], new_stock)
        return True, "Movimiento registrado correctamente"

    @staticmethod
    def edit_movement(movement_id, movement_data):
        # Obtener movimiento original
        from data.repositories import MovementRepository
        original = MovementRepository.get_by_id(movement_id)
        if not original:
            return False, "Movimiento no encontrado"
        # Revertir stock anterior
        product = ProductRepository.get_by_id(original["product_id"])
        if not product:
            return False, "Producto no encontrado"
        revert_quantity = original["quantity"]
        if original["type"] == "out":
            revert_quantity = -revert_quantity
        ProductRepository.update_stock(original["product_id"], product["current_stock"] - revert_quantity)
        # Actualizar movimiento
        MovementRepository.update(movement_id, movement_data)
        # Aplicar nuevo stock
        product = ProductRepository.get_by_id(movement_data["product_id"])
        quantity_change = movement_data["quantity"]
        if movement_data["type"] == "out":
            quantity_change = -quantity_change
        ProductRepository.update_stock(movement_data["product_id"], product["current_stock"] + quantity_change)
        return True, "Movimiento editado correctamente"

    @staticmethod
    def delete_movement(movement_id):
        # Obtener movimiento
        from data.repositories import MovementRepository
        movimiento = MovementRepository.get_by_id(movement_id)
        if not movimiento:
            return False, "Movimiento no encontrado"
        # Revertir stock
        product = ProductRepository.get_by_id(movimiento["product_id"])
        if not product:
            return False, "Producto no encontrado"
        revert_quantity = movimiento["quantity"]
        if movimiento["type"] == "out":
            revert_quantity = -revert_quantity
        ProductRepository.update_stock(movimiento["product_id"], product["current_stock"] - revert_quantity)
        # Eliminar movimiento
        MovementRepository.delete(movement_id)
        return True, "Movimiento eliminado correctamente"

    @staticmethod
    def get_movements_by_product(product_id):
        return MovementRepository.get_by_product_id(product_id)

    @staticmethod
    def get_movements_by_date_range(start_date, end_date):
        return MovementRepository.get_by_date_range(start_date, end_date)