import random
import psycopg2
import os
import sys
import logging
import argparse
from datetime import datetime
import shutil
import re

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def clean_string(text):
    """Очистка строки от проблемных символов"""
    if not text:
        return ""
    text = str(text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'["\'`«»“”]', '', text)
    text = ''.join(c for c in text if ord(c) >= 32 and ord(c) <= 126)
    return text.strip()

def create_db_connection(host, port, database, user, password):
    """Создание подключения к БД"""
    try:
        host = clean_string(host)
        port = clean_string(port)
        database = clean_string(database)
        user = clean_string(user)
        password = clean_string(password)
        
        logger.info(f"Подключение к PostgreSQL: {host}:{port}/{database}")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10
        )
        conn.autocommit = False
        logger.info("✅ Подключение успешно!")
        return conn
        
    except Exception as e:
        logger.error(f"❌ Ошибка подключения: {e}")
        return None

def delete_orders_table(host, port, database, user, password, dry_run=False):
    """Удаление таблицы orders"""
    logger.info(f"{'[DRY-RUN] ' if dry_run else ''}Удаление таблицы orders")
    
    if dry_run:
        logger.info("[DRY-RUN] Имитация удаления")
        return True
    
    conn = create_db_connection(host, port, database, user, password)
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'orders'
            );
        """)
        exists = cur.fetchone()[0]
        
        if not exists:
            logger.warning("⚠️ Таблица orders не существует")
            cur.close()
            conn.close()
            return True
        
        cur.execute("DROP TABLE orders CASCADE;")
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info("✅ Таблица orders удалена!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def create_local_files(fraction=0.1, dry_run=False):
    """Создание и шифрование локальных файлов"""
    logger.info(f"{'[DRY-RUN] ' if dry_run else ''}Создание тестовых файлов...")
    
    test_dir = os.path.join(os.getcwd(), 'test_files')
    
    if dry_run:
        logger.info(f"[DRY-RUN] Будет создано 10 файлов, зашифровано {int(10 * fraction)}")
        return True
    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    
    files_created = []
    for i in range(1, 11):
        file_path = os.path.join(test_dir, f'test_file_{i:02d}.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Test file {i:02d}\n")
            f.write(f"Created: {datetime.now()}\n")
        files_created.append(file_path)
    
    logger.info(f"✅ Создано {len(files_created)} файлов")
    
    count = max(1, int(len(files_created) * fraction))
    selected = random.sample(files_created, count)
    
    encrypted = []
    for file_path in selected:
        new_path = file_path + '.encrypted'
        os.rename(file_path, new_path)
        encrypted.append(new_path)
        logger.info(f"   ✅ Зашифрован: {os.path.basename(file_path)}")
    
    logger.info(f"📊 Зашифровано: {len(encrypted)} из {len(files_created)}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Chaos Engineering DR Drill')
    parser.add_argument('--force', action='store_true', help='Принудительное выполнение')
    parser.add_argument('--dry-run', action='store_true', help='Режим симуляции')
    parser.add_argument('--host', default='localhost', help='Хост PostgreSQL')
    parser.add_argument('--port', default='5432', help='Порт PostgreSQL')
    parser.add_argument('--database', default='postgres', help='База данных')
    parser.add_argument('--user', default='postgres', help='Пользователь')
    parser.add_argument('--password', default='postgres', help='Пароль')
    parser.add_argument('--fraction', type=float, default=0.1, help='Доля файлов для шифрования')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("   CHAOS ENGINEERING - DR DRILL")
    print("="*60 + "\n")
    
    if not args.force:
        env = os.getenv("ENVIRONMENT", "production")
        if env.lower() != "test":
            logger.error(f"❌ Окружение: {env}")
            logger.info("   Используйте --force")
            sys.exit(1)
    
    if args.dry_run:
        logger.info("🔍 РЕЖИМ DRY-RUN\n")
    
    logger.info(f"🚀 Запуск: {datetime.now()}")
    
    # Удаление таблицы
    logger.info("-" * 50)
    if not delete_orders_table(args.host, args.port, args.database, args.user, args.password, args.dry_run):
        if not args.dry_run:
            sys.exit(1)
    
    # Создание файлов
    logger.info("-" * 50)
    if not create_local_files(args.fraction, args.dry_run):
        if not args.dry_run:
            sys.exit(1)
    
    logger.info("-" * 50)
    logger.info("✅ Готово!")
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Прервано")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        sys.exit(1)