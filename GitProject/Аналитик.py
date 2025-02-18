import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt

class CSVAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ воздуха")
        self.data = None
        
        # Кнопка для загрузки файла
        self.load_button = tk.Button(root, text="Загрузить CSV", command=self.load_csv)
        self.load_button.pack(pady=10)
        
        # Таблица для отображения данных
        self.tree = ttk.Treeview(root, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка для анализа данных
        self.analyze_button = tk.Button(root, text="Анализировать", command=self.analyze_data)
        self.analyze_button.pack(pady=10)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                self.display_data()
                messagebox.showinfo("Успех", "Файл успешно загружен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def display_data(self):
        # Очищаем таблицу
        self.tree.delete(*self.tree.get_children())
        
        # Устанавливаем заголовки
        self.tree["columns"] = list(self.data.columns)
        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Добавляем данные в таблицу
        for row in self.data.itertuples(index=False):
            self.tree.insert("", "end", values=row)
    
    def analyze_data(self):
        if self.data is None:
            messagebox.showerror("Ошибка", "Сначала загрузите файл!")
            return
        
        try:
            # Пример анализа: расчет средних значений
            data = self.data
            data['Time'] = pd.to_datetime(data['Time'])
            for col in ['CO2', 'NO2', 'CH4']:
                data[col] = data[col].apply(lambda x: None if x < 0 else x)  # Удаляем значения ниже нуля

            daily_avg = data.groupby(data['Time'].dt.date).mean()

            # 4. Сравнение с нормативами
            daily_avg = daily_avg.apply(pd.to_numeric, errors='coerce')  # Преобразуем данные в числа, игнорируя ошибки
            norms = {'CO2': 400, 'NO2': 200, 'CH4': 5}  # Пороговые значения в ppm
            # Сравнение с нормативами
            exceeds = daily_avg.gt(pd.Series(norms), axis=1)

            # 5. Визуализация
            plt.figure(figsize=(10, 6))
            for col in ['CO2', 'NO2', 'CH4']:
                plt.plot(daily_avg.index, daily_avg[col], label=col)
                plt.axhline(norms[col], color='red', linestyle='--', label=f'{col} Норма')


            exceeded_days = daily_avg[exceeds.any(axis=1)]
            result_text = f"Дни с превышением нормативов:\n{exceeded_days}"

            # Отображение текста в графическом интерфейсе
            if hasattr(self, "result_label"):
                self.result_label.destroy()
            self.result_label = tk.Label(self.root, text=result_text, justify="center", font=("Arial", 12))
            self.result_label.pack(pady=10) 

            plt.xlabel('Дата')
            plt.ylabel('Концентрация (ppm)')
            plt.title('Среднесуточные уровни загрязняющих веществ')
            plt.legend()
            plt.show()
            root.mainloop()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить анализ: {e}")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVAnalyzerApp(root)
    root.geometry("800x600")
    root.mainloop()