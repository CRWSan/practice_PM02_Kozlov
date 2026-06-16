# Сервис валидации заказов

## Установка

```bash
pip install pytest hypothesis freezegun pydantic

# Все тесты
pytest -v

# С детализацией
pytest -v --tb=short

# Конкретный тест
pytest test_validate_order.py::test_risk_score_in_range -v

# С отчетом о покрытии
pip install pytest-cov
pytest --cov=fake_validator