class EntityNotFoundException(Exception):
    """Исключение, выбрасываемое когда сущность не найдена"""
    def __init__(self, entity_type: str, entity_id: int):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id {entity_id} not found")


class DeliveryCalculationException(Exception):
    """Исключение, выбрасываемое при ошибке расчёта доставки"""
    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(f"Delivery calculation failed: {message}")