
---

## **`test_cases.md`**

```markdown
# Тест-кейсы для валидации заказов

| ID | Название | Предусловия | Входные данные | Ожидаемый результат |
|----|----------|-------------|----------------|---------------------|
| TC1 | Сумма = 0.01 (мин) | - | total_amount=0.01 | valid=True, risk=0 |
| TC2 | Сумма = 999999.99 (макс) | - | total_amount=999999.99 | valid=True, risk=0.9 |
| TC3 | Сумма = 0 | - | total_amount=0 | valid=False, reason="больше 0" |
| TC4 | Сумма = 1000000 | - | total_amount=1000000 | valid=False, reason="меньше" |
| TC5 | Новый пользователь, сумма=15000 | user_created_at=now-6d | total_amount=15000 | valid=True |
| TC6 | Новый пользователь, сумма=15000.01 | user_created_at=now-6d | total_amount=15000.01 | valid=False |
| TC7 | Кол-во=50 | - | items_count=50 | valid=True |
| TC8 | Кол-во=51 | - | items_count=51 | valid=False |
| TC9 | Alcohol, 08:00 | age_verified=True | created_at=08:00 | valid=True |
| TC10 | Alcohol, 07:59 | age_verified=True | created_at=07:59 | valid=False |
| TC11 | Alcohol, 23:00 | age_verified=True | created_at=23:00 | valid=True |
| TC12 | Alcohol, 23:01 | age_verified=True | created_at=23:01 | valid=False |
| TC13 | Alcohol, age=False | created_at=12:00 | age_verified=False | valid=False |
| TC14 | Сумма > 100k | - | total_amount=200000 | valid=True, risk=0.9 |
| TC15 | Смена email < 1ч | - | email_changed=now-30min | valid=True, risk=0.2 |
| TC16 | Смена email = 1ч | - | email_changed=now-1h | valid=True, risk=0 |
| TC17 | Страны разные | - | delivery=RU, wallet=US | valid=True, risk=0.3 |
| TC18 | Комбинация рисков | - | amount=200k, email=now-10min, countries different | valid=True, risk=1.0 |
| TC19 | Новый + Alcohol + 02:00 | new user | category=Alcohol, time=02:00 | valid=False, 2 reasons |
| TC20 | Валидный с высоким риском | - | amount=500k, email=now-5min, countries diff | valid=True, risk=1.0 |
| TC21 | Отрицательная сумма | - | total_amount=-100 | valid=False |
| TC22 | Невалидная страна | - | delivery_country="XYZ" | valid=False (input error) |
| TC23 | Пустой order_id | - | order_id="" | valid=False (input error) |
| TC24 | Alcohol + новое время | age_verified=True | created_at=14:00 | valid=True |
| TC25 | Обычный заказ, все ок | - | all default | valid=True, risk=0 |
| TC26 | Новый пользователь, ровно 7 дней | user_created_at=now-7d | total_amount=20000 | valid=False |
| TC27 | Старый пользователь, сумма большая | user_created_at=now-365d | total_amount=800000 | valid=True, risk=0.9 |
| TC28 | Смена email ровно через час | - | email_changed=now-1h | valid=True, risk=0 |
| TC29 | Все риски вместе | - | amount=150k, email=now-30min, countries diff | valid=True, risk=1.0 |
| TC30 | Alcohol в 08:00:00 | age_verified=True | created_at=08:00:00 | valid=True |
| TC31 | Alcohol в 07:59:59 | age_verified=True | created_at=07:59:59 | valid=False |
| TC32 | Дубликат заказа | первый заказ | тот же заказ | результаты одинаковые |