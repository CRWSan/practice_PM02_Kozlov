import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import csv

def connect_db():
    """Подключение к базе данных MySQL"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="xa7FSEMbBnmC-RV",
            database="variant8_work"
        )
        return connection
    except Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось подключиться: {e}")
        return None

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление базой данных")
        self.root.geometry("900x600")
        
        self.current_table = None
        self.columns = []
        self.entries = {}
        
        # Создаём интерфейс
        self.create_widgets()
        
        # Загружаем список таблиц
        self.load_tables()
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # === Верхняя панель с выбором таблицы ===
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(top_frame, text="Выберите таблицу:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.table_combo = ttk.Combobox(top_frame, width=30, state="readonly")
        self.table_combo.pack(side=tk.LEFT, padx=5)
        self.table_combo.bind("<<ComboboxSelected>>", self.on_table_select)
        
        tk.Button(top_frame, text="🔄 Обновить список", command=self.load_tables, 
                 bg="#87CEEB", width=15).pack(side=tk.LEFT, padx=5)
        
        # === Панель поиска ===
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5, padx=10, fill=tk.X)
        
        tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="🔍 Найти", command=self.search, 
                 width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(search_frame, text="Показать всех", command=self.refresh_table, 
                 width=12).pack(side=tk.LEFT, padx=2)
        
        # === Рамка для полей ввода ===
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # === Кнопки действий ===
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="➕ Добавить", command=self.add_record, 
                  bg="#90EE90", width=12).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="✏️ Обновить", command=self.update_record, 
                  bg="#FFD700", width=12).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="🗑️ Удалить", command=self.delete_record, 
                  bg="#FF6347", width=12).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="🧹 Очистить", command=self.clear_entries, 
                  width=12).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="📤 Экспорт в CSV", command=self.export_to_csv, 
                  bg="#DDA0DD", width=15).grid(row=0, column=4, padx=5)
        
        # === Таблица Treeview ===
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создаём скроллы
        scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree = ttk.Treeview(tree_frame, show="headings",
                                 yscrollcommand=scroll_y.set,
                                 xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Привязываем событие выбора строки
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def load_tables(self):
        """Загрузить список таблиц из базы данных"""
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            table_names = [table[0] for table in tables]
            self.table_combo['values'] = table_names
            
            if table_names:
                self.table_combo.set("")
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить таблицы: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def get_table_structure(self, table_name):
        """Получить структуру таблицы"""
        conn = connect_db()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        try:
            # Получаем информацию о колонках
            cursor.execute(f"DESCRIBE {table_name}")
            columns_info = cursor.fetchall()
            
            columns = []
            for col in columns_info:
                col_name = col[0]
                col_type = col[1]
                col_null = col[2]
                col_key = col[3]
                col_extra = col[5]
                
                column = {
                    "name": col_name,
                    "label": col_name.capitalize(),
                    "required": col_null == 'NO' and col_key != 'PRI',
                    "pk": col_key == 'PRI',
                    "auto_increment": 'auto_increment' in col_extra.lower() if col_extra else False
                }
                columns.append(column)
            
            return columns
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось получить структуру таблицы: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def create_input_fields(self):
        """Создать поля ввода на основе структуры таблицы"""
        # Очищаем существующие поля
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        self.entries = {}
        
        # Создаём метки и поля для каждого столбца
        row_num = 0
        col_num = 0
        max_cols = 3  # Максимум 3 поля в строке
        
        for col in self.columns:
            # Пропускаем PK с AUTO_INCREMENT
            if col.get('pk') and col.get('auto_increment'):
                continue
            
            # Метка
            label_text = col['label']
            if col.get('required'):
                label_text += " *"
            
            label = tk.Label(self.input_frame, text=f"{label_text}:", font=("Arial", 9))
            label.grid(row=row_num, column=col_num*2, padx=5, pady=5, sticky="e")
            
            # Поле ввода
            entry = tk.Entry(self.input_frame, width=25)
            entry.grid(row=row_num, column=col_num*2+1, padx=5, pady=5)
            self.entries[col['name']] = entry
            
            col_num += 1
            if col_num >= max_cols:
                col_num = 0
                row_num += 1
        
        # Добавляем информационную метку
        info_label = tk.Label(self.input_frame, text="* - обязательные поля", 
                             font=("Arial", 8), fg="red")
        info_label.grid(row=row_num+1, column=0, columnspan=max_cols*2, pady=5)
    
    def on_table_select(self, event):
        """При выборе таблицы"""
        self.current_table = self.table_combo.get()
        if not self.current_table:
            return
        
        # Получаем структуру таблицы
        self.columns = self.get_table_structure(self.current_table)
        if not self.columns:
            return
        
        # Создаём поля ввода
        self.create_input_fields()
        
        # Настраиваем Treeview
        self.setup_treeview()
        
        # Загружаем данные
        self.refresh_table()
        
        messagebox.showinfo("Информация", f"Загружена таблица: {self.current_table}")
    
    def setup_treeview(self):
        """Настроить колонки Treeview"""
        # Очищаем текущие колонки
        for col in self.tree['columns']:
            self.tree.heading(col, text="")
            self.tree.column(col, width=0)
        
        # Устанавливаем новые колонки
        columns_names = [col['name'] for col in self.columns]
        self.tree['columns'] = columns_names
        
        # Настраиваем заголовки
        for col in self.columns:
            self.tree.heading(col['name'], text=col['label'])
            # Автоматическая ширина: 120 для ID, 100 для остальных
            width = 120 if col.get('pk') else 100
            self.tree.column(col['name'], width=width, anchor="center", minwidth=80)
    
    def refresh_table(self):
        """Обновить данные в таблице Treeview"""
        if not self.current_table or not self.columns:
            return
        
        # Очищаем текущие данные
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Получаем данные из БД
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Формируем запрос SELECT
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.current_table}"
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def on_select(self, event):
        """При выборе строки в таблице — заполняем поля ввода"""
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        
        # Заполняем поля ввода
        for i, col in enumerate(self.columns):
            col_name = col['name']
            if col_name in self.entries:
                self.entries[col_name].delete(0, tk.END)
                self.entries[col_name].insert(0, str(values[i]) if values[i] is not None else "")
    
    def get_pk_name(self):
        """Вернуть имя первичного ключа"""
        for col in self.columns:
            if col.get('pk'):
                return col['name']
        return None
    
    def get_pk_value(self):
        """Получить значение PK выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            return None
        
        values = self.tree.item(selected[0])['values']
        pk_name = self.get_pk_name()
        if not pk_name:
            return None
        
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        return values[pk_index]
    
    def add_record(self):
        """Добавить новую запись"""
        if not self.current_table:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return
        
        # Собираем значения из полей ввода
        values = {}
        for col_name, entry in self.entries.items():
            values[col_name] = entry.get().strip()
        
        # Проверяем обязательные поля
        for col in self.columns:
            col_name = col['name']
            if col.get('required') and col_name in self.entries and not values[col_name]:
                messagebox.showwarning("Ошибка", f"Поле '{col['label']}' обязательно для заполнения")
                return
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Формируем INSERT-запрос
        columns_names = list(values.keys())
        placeholders = ", ".join(["%s"] * len(columns_names))
        query = f"INSERT INTO {self.current_table} ({', '.join(columns_names)}) VALUES ({placeholders})"
        
        try:
            cursor.execute(query, list(values.values()))
            conn.commit()
            messagebox.showinfo("Успех", "Запись добавлена")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def update_record(self):
        """Обновить выбранную запись"""
        if not self.current_table:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return
        
        pk_value = self.get_pk_value()
        if not pk_value:
            messagebox.showwarning("Предупреждение", "Выберите запись для обновления")
            return
        
        # Собираем новые значения из полей
        new_values = {}
        for col_name, entry in self.entries.items():
            new_values[col_name] = entry.get().strip()
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Формируем UPDATE-запрос
        pk_name = self.get_pk_name()
        set_clause = ", ".join([f"{col} = %s" for col in new_values.keys()])
        query = f"UPDATE {self.current_table} SET {set_clause} WHERE {pk_name} = %s"
        
        try:
            params = list(new_values.values()) + [pk_value]
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Успех", "Запись обновлена")
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def delete_record(self):
        """Удалить выбранную запись"""
        if not self.current_table:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return
        
        pk_value = self.get_pk_value()
        if not pk_value:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить запись?"):
            return
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        pk_name = self.get_pk_name()
        query = f"DELETE FROM {self.current_table} WHERE {pk_name} = %s"
        
        try:
            cursor.execute(query, (pk_value,))
            conn.commit()
            messagebox.showinfo("Успех", "Запись удалена")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def search(self):
        """Поиск по таблице"""
        if not self.current_table or not self.columns:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return
        
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
        
        # Ищем по всем текстовым полям
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Формируем условие LIKE для всех колонок
        text_columns = [col['name'] for col in self.columns if not col.get('pk')]
        
        if not text_columns:
            self.refresh_table()
            return
        
        conditions = " OR ".join([f"{col} LIKE %s" for col in text_columns])
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.current_table} WHERE {conditions}"
        
        try:
            cursor.execute(query, tuple([f"%{keyword}%"] * len(text_columns)))
            rows = cursor.fetchall()
            
            # Очищаем таблицу
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            # Заполняем результатами поиска
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            
            if not rows:
                messagebox.showinfo("Результат", "Записи не найдены")
        except Error as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def export_to_csv(self):
        """Экспорт данных в CSV"""
        if not self.current_table or not self.columns:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return
        
        filename = f"{self.current_table}_export.csv"
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT * FROM {self.current_table}"
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([col['label'] for col in self.columns])
                writer.writerows(rows)
            
            messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def clear_entries(self):
        """Очистить все поля ввода"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

def main():
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()