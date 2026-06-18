"""
Вариант 8: Множества (set) - ИСПРАВЛЕННАЯ ВЕРСИЯ
Все ошибки исправлены:
1. Изменение множества во время итерации - исправлено
2. Логическая ошибка в Jaccard - исправлена
3. Утечка памяти - исправлена (ограниченный кеш)
4. Рекурсивная ошибка - исправлена
"""

import math
import time
import tracemalloc
from typing import Set, List, Dict, Any
from collections import OrderedDict
from functools import lru_cache


class LimitedCache:
    """Ограниченный кеш с политикой LRU."""
    
    def __init__(self, max_size: int = 100):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def set(self, key: str, value: Set[int]) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            # Удаляем самый старый элемент
            self.cache.popitem(last=False)
        self.cache[key] = value
    
    def get(self, key: str) -> Set[int]:
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def clear(self) -> None:
        self.cache.clear()
    
    def __len__(self) -> int:
        return len(self.cache)


# Глобальный кеш с ограничением
CACHE = LimitedCache(max_size=100)
# Ограниченная история
MAX_HISTORY = 1000
HISTORY: List[float] = []


def add_to_history(value: float) -> None:
    """Добавление в историю с ограничением размера."""
    global HISTORY
    HISTORY.append(value)
    if len(HISTORY) > MAX_HISTORY:
        # Удаляем старые записи (FIFO)
        HISTORY = HISTORY[-MAX_HISTORY:]


def jaccard_similarity(set_a: Set[int], set_b: Set[int]) -> float:
    """
    Вычисляет меру Жаккара между двумя множествами.
    ИСПРАВЛЕНО: правильная формула |A ∩ B| / |A ∪ B|
    """
    if not set_a or not set_b:
        return 0.0
    
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    
    if union == 0:
        return 0.0
    
    # Исправлено: intersection / union
    return intersection / union


@lru_cache(maxsize=128)
def get_union_key(set_a_tuple: tuple, set_b_tuple: tuple) -> tuple:
    """Кешированное получение объединения множеств."""
    return tuple(sorted(set(set_a_tuple) | set(set_b_tuple)))


def process_sets(data: List[Dict[str, Any]]) -> List[float]:
    """
    Основная функция обработки множеств.
    ИСПРАВЛЕНО: безопасная работа с множествами.
    """
    results = []
    
    for idx, item in enumerate(data):
        # Безопасное копирование множества
        if 'set' in item:
            original_set = item['set']
            # Не изменяем исходное множество во время итерации
            # Создаем новое множество с нужными элементами
            filtered_set = {elem for elem in original_set if elem % 2 != 0}
            
            # Можно заменить исходное множество новым
            # item['set'] = filtered_set
        
        # Получаем множества для сравнения
        set_a = item.get('set_a', set())
        set_b = item.get('set_b', set())
        
        # Если нет set_b, используем set
        if not set_b and 'set' in item:
            set_b = item['set']
        
        # Вычисляем схожесть (исправленная формула)
        similarity = jaccard_similarity(set_a, set_b)
        
        # Кеширование с ограничением размера
        cache_key = f"{hash(frozenset(set_a))}_{hash(frozenset(set_b))}"
        if CACHE.get(cache_key) is None:
            union_result = set_a | set_b
            CACHE.set(cache_key, union_result)
        
        # Сохранение в историю с ограничением
        add_to_history(similarity)
        
        results.append(similarity)
    
    return results


def recursive_process(data: List[Dict[str, Any]], depth: int = 0, max_depth: int = 5) -> None:
    """
    Рекурсивная обработка.
    ИСПРАВЛЕНО: защита от бесконечной рекурсии.
    """
    if not data:
        return
    
    # Защита от слишком глубокой рекурсии
    if depth > max_depth:
        print(f"Достигнута максимальная глубина рекурсии ({max_depth}), остановка")
        return
    
    for item in data:
        if 'children' in item and item['children']:
            # Рекурсивный обход детей
            recursive_process(item['children'], depth + 1, max_depth)
        elif 'set' in item:
            # Безопасная обработка множества
            processed_set = {x for x in item['set'] if x <= 100}
            # Сохраняем результат обработки
            item['processed_set'] = processed_set


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
    
    print("Запуск обработки данных (Вариант 8 - ИСПРАВЛЕННАЯ ВЕРСИЯ)...")
    print("=" * 60)
    
    # Генерируем тестовые данные
    test_data = generate_test_data()
    
    try:
        # Основная обработка
        results = process_sets(test_data)
        print(f"Результаты обработки: {results}")
        
        # Проверка корректности результатов (Jaccard не должен быть > 1)
        for i, val in enumerate(results):
            if val > 1.0:
                print(f"Предупреждение: значение {val} > 1.0 для элемента {i}")
        
        # Рекурсивная обработка (без ошибок)
        print("\nЗапуск рекурсивной обработки...")
        recursive_process(test_data)
        
        # Вывод информации о кеше
        print(f"\nРазмер кеша: {len(CACHE)}")
        print(f"Размер истории: {len(HISTORY)}")
        
        # Проверка на утечку памяти
        print("\nДобавление дополнительных данных...")
        for i in range(100):
            test_data.append({
                'set_a': {i, i+1, i+2},
                'set_b': {i+2, i+3, i+4},
                'set': {i, i+1, i+2, i+3, i+4},
                'children': []
            })
        
        # Повторная обработка (кеш ограничен)
        more_results = process_sets(test_data)
        print(f"Обработано еще {len(more_results)} элементов")
        
        print(f"\nРазмер кеша после добавления: {len(CACHE)} (ограничен {CACHE.max_size})")
        print(f"Размер истории после добавления: {len(HISTORY)} (ограничен {MAX_HISTORY})")
        
        print("\n✅ Все ошибки исправлены!")
        
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Статистика памяти
        snapshot = tracemalloc.take_snapshot()
        print("\n" + "=" * 60)
        print("СТАТИСТИКА ПАМЯТИ:")
        print("=" * 60)
        
        top_stats = snapshot.statistics('lineno')
        print("\nТоп-10 строк кода" \
        " по потреблению памяти:")
        for i, stat in enumerate(top_stats[:10], 1):
            print(f"  {i}. {stat}")
        
        # Общее количество выделенной памяти
        total_memory = sum(stat.size for stat in top_stats)
        print(f"\nОбщее количество выделенной памяти: {total_memory / 1024 / 1024:.2f} MB")
        
        # Очистка ресурсов
        CACHE.clear()
        HISTORY.clear()
        print("Ресурсы очищены.")


if __name__ == "__main__":
    main()