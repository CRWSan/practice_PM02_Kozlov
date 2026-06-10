import bcrypt
import mysql.connector

connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='xa7FSEMbBnmC-RV',
    database='variant8_work'
)

cursor = connection.cursor()

# Очищаем таблицу
cursor.execute("TRUNCATE TABLE Пользователи")
print("Таблица Пользователи очищена")

# Создаем администратора
admin_login = "admin"
admin_password = "admin123"  # Измените на нужный пароль
admin_role = "admin"

hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
hashed_str = hashed.decode('utf-8')

cursor.execute(
    "INSERT INTO Пользователи (логин, пароль_hash, роль) VALUES (%s, %s, %s)",
    (admin_login, hashed_str, admin_role)
)
connection.commit()

print(f"Создан администратор:")
print(f"Логин: {admin_login}")
print(f"Пароль: {admin_password}")
print(f"Хеш: {hashed_str}")

cursor.close()
connection.close()