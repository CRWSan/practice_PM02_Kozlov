"""
Вариант 8: Множества (set)
Ошибки:
1. Изменение множества во время итерации (RuntimeError)
2. Логическая ошибка в теоретико-множественной операции (неправильная формула Jaccard)
3. Утечка памяти: глобальный кеш множеств без очистки
4. Рекурсивный обход без выхода (скрытая рекурсия через вложенные циклы)
"""

import math
import time
import tracemalloc
from typing import Set, List, Dict, Any

# Глобальный кеш множеств - потенциальная утечка памяти
CACHE: Dict[str, Set[int]] = {}
# Глобальный список для хранения результатов - тоже утечка
HISTORY: List[float] = []


def jaccard_similarity(set_a: Set[int], set_b: Set[int]) -> float:
    """
    Вычисляет меру Жаккара между двумя множествами.
    Ошибка: неправильная формула - используется объединение вместо пересечения в числителе
    Правильно: |A ∩ B| / |A ∪ B|
    Ошибка: |A ∪ B| / |A ∩ B| (обратное отношение)
    """
    if not set_a or not set_b:
        return 0.0
    
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    
    # ЛОГИЧЕСКАЯ ОШИБКА: перепутан числитель и знаменатель
    # Должно быть: intersection / union
    # А здесь: union / intersection
    if intersection == 0:
        return 0.0
    return union / intersection  # Ошибка! Должно быть intersection / union


def process_sets(data: List[Dict[str, Any]]) -> List[float]:
    """
    Основная функция обработки множеств.
    Содержит ошибку изменения множества во время итерации.
    """
    results = []
    breakpoint()
    for item in data:
        # ОШИБКА 1: изменение множества во время итерации
        # item['set'] - это множество, которое мы изменяем
        current_set = item['set'].copy()  # копия для безопасной работы
        
        # Вложенные циклы с изменением множества
        for element in current_set:  # Итерируем по копии
            # Пытаемся удалить элементы, которые не подходят
            # Ошибка: изменяем исходное множество item['set'] во время итерации
            if element % 2 == 0:
                # ОШИБКА: удаление из множества во время итерации по нему
                # item['set'].remove(element)  # Это вызовет RuntimeError
                pass  # Закомментировано, чтобы не падало сразу
        
        # Альтернативная ошибка: добавление во время итерации
        # for element in item['set']:  # Итерируем по исходному множеству
        #     if element > 10:
        #         item['set'].add(element * 2)  # Изменяем множество во время итерации
        
        # ОШИБКА 2: вызов jaccard_similarity с неправильными параметрами
        # Используем item['set'] напрямую (может быть изменено)
        set_a = item.get('set_a', set())
        set_b = item.get('set_b', set())
        
        # Если нет set_b, используем current_set
        if not set_b:
            set_b = current_set
        
        # Вычисляем схожесть
        similarity = jaccard_similarity(set_a, set_b)
        
        # УТЕЧКА ПАМЯТИ: кешируем все результаты без ограничения
        cache_key = f"{hash(frozenset(set_a))}_{hash(frozenset(set_b))}"
        CACHE[cache_key] = set_a | set_b  # Сохраняем объединение
        
        # Еще одна утечка: сохраняем все результаты
        HISTORY.append(similarity)
        
        results.append(similarity)
    
    return results


def recursive_process(data: List[Dict[str, Any]], depth: int = 0) -> None:
    """
    Скрытая рекурсия через вложенные циклы.
    ОШИБКА 4: рекурсивный вызов без условия выхода при определенных условиях.
    """
    if not data:
        return
    
    # Ошибка: при depth > 5 рекурсия не останавливается
    if depth > 5:
        # ОШИБКА: бесконечная рекурсия
        # рекурсивный вызов с теми же данными и увеличенной глубиной
        recursive_process(data, depth + 1)  # Нет выхода!
        return
    
    for item in data:
        if 'children' in item and item['children']:
            # Рекурсивный обход
            recursive_process(item['children'], depth + 1)
        elif 'set' in item:
            # Ошибка: при depth == 5 вызываем рекурсию без изменения данных
            if depth == 5:
                recursive_process(data, depth + 1)  # Бесконечная рекурсия!
            # Обработка множества
            for element in item['set']:
                if element > 100:
                    # Ошибка: изменение множества при итерации
                    # item['set'].add(element // 2)  # Изменяем множество
                    pass


def generate_test_data() -> List[Dict[str, Any]]:
    """Генерация тестовых данных с множествами."""
    data = []
    
    # Нормальные данные
    data.append({
        'set_a': {1, 2, 3, 4, 5},
        'set_b': {4, 5, 6, 7, 8},
        'set': {1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
        'children': []
    })
    
    data.append({
        'set_a': {10, 20, 30, 40},
        'set_b': {20, 30, 40, 50},
        'set': {10, 20, 30, 40, 50, 60},
        'children': []
    })
    
    # Данные с пустыми множествами
    data.append({
        'set_a': set(),
        'set_b': {1, 2, 3},
        'set': {1, 2, 3, 4, 5},
        'children': []
    })
    
    # Данные с вложенными структурами для рекурсии
    data.append({
        'set_a': {1, 2, 3},
        'set_b': {3, 4, 5},
        'set': {1, 2, 3, 4, 5, 6, 7, 8},
        'children': [
            {
                'set': {10, 11, 12},
                'set_a': {10, 11},
                'set_b': {11, 12},
                'children': []
            },
            {
                'set': {20, 21, 22},
                'set_a': {20, 21},
                'set_b': {21, 22},
                'children': []
            }
        ]
    })
    
    return data


def main():
    """Главная функция."""
    # Запускаем отслеживание памяти
    tracemalloc.start()
    
    print("Запуск обработки данных (Вариант 8)...")
    print("=" * 60)
    
    # Генерируем тестовые данные
    test_data = generate_test_data()
    
    try:
        # Основная обработка
        results = process_sets(test_data)
        print(f"Результаты обработки: {results}")
        
        # Рекурсивная обработка (может вызвать RecursionError)
        print("\nЗапуск рекурсивной обработки...")
        recursive_process(test_data)
        
        # Вывод информации о кеше
        print(f"\nРазмер кеша: {len(CACHE)}")
        print(f"Размер истории: {len(HISTORY)}")
        
        # Демонстрация утечки - добавляем еще данные
        print("\nДобавление дополнительных данных...")
        for i in range(100):
            test_data.append({
                'set_a': {i, i+1, i+2},
                'set_b': {i+2, i+3, i+4},
                'set': {i, i+1, i+2, i+3, i+4},
                'children': []
            })
        
        # Повторная обработка (увеличит утечку)
        more_results = process_sets(test_data)
        print(f"Обработано еще {len(more_results)} элементов")
        
        print(f"\nРазмер кеша после добавления: {len(CACHE)}")
        print(f"Размер истории после добавления: {len(HISTORY)}")
        
    except RuntimeError as e:
        print(f"\nОШИБКА ВРЕМЕНИ ВЫПОЛНЕНИЯ: {e}")
        import traceback
        traceback.print_exc()
        
    except RecursionError as e:
        print(f"\nОШИБКА РЕКУРСИИ: {e}")
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print(f"\nНЕОЖИДАННАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Статистика памяти
        snapshot = tracemalloc.take_snapshot()
        print("\n" + "=" * 60)
        print("СТАТИСТИКА ПАМЯТИ:")
        print("=" * 60)
        
        # Топ-10 строк по потреблению памяти
        top_stats = snapshot.statistics('lineno')
        print("\nТоп-10 строк кода по потреблению памяти:")
        for i, stat in enumerate(top_stats[:10], 1):
            print(f"  {i}. {stat}")
        
        # Статистика по файлам
        print("\nТоп-5 файлов по потреблению памяти:")
        top_files = snapshot.statistics('filename')
        for i, stat in enumerate(top_files[:5], 1):
            print(f"  {i}. {stat}")
        
        # Сравнение с предыдущим снимком (если есть)
        print("\nОбщее количество выделенной памяти:")
        total_memory = sum(stat.size for stat in top_stats)
        print(f"  {total_memory / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()