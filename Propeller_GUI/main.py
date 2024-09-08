import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
import serial.tools.list_ports
import os


class TestApp(ThemedTk):
    def __init__(self):
        super().__init__(theme='arc')  # Используйте тему 'arc' для современного вида

        self.check_button = None
        self.port_combobox = None
        self.port_label = None
        self.port_frame = None

        self.test_list_frame = None
        self.test_info_label = None
        self.test_info_tab = None
        self.test_result_label = None
        self.test_button = None

        self.propeller_entries = None
        self.propeller_tab = None
        self.propeller_combobox = None
        self.propeller_label = None

        self.engine_entries = None
        self.engine_combobox = None
        self.engine_label = None
        self.engine_tab = None
        self.canvas = None

        self.ax3 = None
        self.ax2 = None
        self.ax1 = None
        self.figure = None
        self.graph_frame = None
        self.graph_tab = None

        self.title("Motor and Propeller Test")
        self.geometry("1000x600")  # Установите размер окна

        # Инициализация файлов
        self.engine_file = 'engines.txt'
        self.propeller_file = 'propellers.txt'
        self.test_history_file = 'test_history.txt'  # Файл с историей тестов

        self.create_menu()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Вкладка графиков
        self.create_graph_tab()

        # Вкладка добавления двигателей
        self.create_engine_tab()

        # Вкладка добавления пропеллеров
        self.create_propeller_tab()

        # Настройка выбора порта
        self.create_port_selection()

        # Обновляем выпадающие списки
        self.update_dropdowns()

        # Вкладка с историей тестов
        self.create_test_info_tab()

        # Интервал обновления в миллисекундах (5 секунд)
        self.update_interval = 5000
        self.last_modified_time = None
        self.check_for_updates()

    def create_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.quit)

    def create_graph_tab(self):
        self.graph_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_tab, text="Test")

        # Создание рамок для графиков
        self.graph_frame = ttk.Frame(self.graph_tab)
        self.graph_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Создание фигур для графиков
        # Установите размеры фигуры
        self.figure = Figure(figsize=(12, 3), dpi=100)
        self.ax1 = self.figure.add_subplot(131, title="RPM")
        self.ax2 = self.figure.add_subplot(132, title="Moment")
        self.ax3 = self.figure.add_subplot(133, title="Thrust")

        # Добавляем стильные рамки и фиксированный размер графиков
        self.create_graph_panel(self.ax1, "RPM")
        self.create_graph_panel(self.ax2, "Moment")
        self.create_graph_panel(self.ax3, "Thrust")

        # Добавление графиков на вкладку
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Окна ввода
        self.engine_label = ttk.Label(self.graph_tab, text="Engine:")
        self.engine_label.pack(pady=5, padx=10, anchor='w')
        self.engine_combobox = ttk.Combobox(
            self.graph_tab, values=self.load_engine_list())
        self.engine_combobox.pack(pady=5, padx=10, fill='x')

        self.propeller_label = ttk.Label(self.graph_tab, text="Propeller:")
        self.propeller_label.pack(pady=5, padx=10, anchor='w')
        self.propeller_combobox = ttk.Combobox(
            self.graph_tab, values=self.load_propeller_list())
        self.propeller_combobox.pack(pady=5, padx=10, fill='x')

    @staticmethod
    def create_graph_panel(ax, title):
        """ Создает стилизованный график """
        ax.set_title(title, fontsize=16, weight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)

        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')

        ax.grid(True, linestyle='--', alpha=0.5)  # Более легкая сетка
        ax.set_facecolor('#f7f7f7')  # Светлый фон
        ax.tick_params(axis='both', which='major',
                       labelsize=12)  # Увеличенные тики
        ax.tick_params(axis='both', which='minor', labelsize=10)

        # Прозрачная заливка под линией графика
        ax.fill_between([], [], color='#B2DFDB', alpha=0.3)  # Пример заливки

        # Установка плавной линии
        ax.plot([], [], color='#00796B', linewidth=2, alpha=0.85)  # Цвет линии

        # Легенда (по желанию)
        ax.legend(loc='upper left')

    # Пример обновления графиков с плавным обновлением
    def update_graphs(self, rpm, moment, thrust):
        # Очистка предыдущих данных
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        # Обновляем графики с новыми данными
        self.create_graph_panel(self.ax1, "RPM")
        self.create_graph_panel(self.ax2, "Moment")
        self.create_graph_panel(self.ax3, "Thrust")

        # Отображаем последние данные (пример для визуала)
        self.ax1.plot(rpm, label='RPM', color='#1976D2',
                      linewidth=2.5)  # Цветовая гамма
        self.ax2.plot(moment, label='Moment', color='#388E3C', linewidth=2.5)
        self.ax3.plot(thrust, label='Thrust', color='#D32F2F', linewidth=2.5)

        # Обновление графиков
        self.canvas.draw()

    def create_engine_tab(self):
        self.engine_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.engine_tab, text="Add Engine")

        # Настройка для динамического изменения размеров
        self.engine_tab.columnconfigure(1, weight=1)

        # Сетка для полей ввода характеристик двигателя
        ttk.Label(self.engine_tab, text="Engine Details", font=(
            "Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        self.engine_entries = {}
        labels = ["Name", "Brand", "Model", "Power", "Weight", "Other"]
        for i, label_text in enumerate(labels):
            label = ttk.Label(
                self.engine_tab, text=label_text + ":", font=("Arial", 12))
            label.grid(row=i + 1, column=0, padx=10, pady=5, sticky='e')

            entry = ttk.Entry(self.engine_tab)
            entry.grid(row=i + 1, column=1, padx=10, pady=5, sticky='ew')

            self.engine_entries[label_text] = entry

        add_button = ttk.Button(
            self.engine_tab, text="Add Engine", command=self.add_engine)
        add_button.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

    def create_propeller_tab(self):
        self.propeller_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.propeller_tab, text="Add Propeller")

        # Настройка для динамического изменения размеров
        self.propeller_tab.columnconfigure(1, weight=1)

        # Сетка для полей ввода характеристик пропеллера
        ttk.Label(self.propeller_tab, text="Propeller Details", font=(
            "Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        self.propeller_entries = {}
        labels = ["Name", "Brand", "Model", "Diameter", "Weight", "Other"]
        for i, label_text in enumerate(labels):
            label = ttk.Label(self.propeller_tab,
                              text=label_text + ":", font=("Arial", 12))
            label.grid(row=i + 1, column=0, padx=10, pady=5, sticky='e')

            entry = ttk.Entry(self.propeller_tab)
            entry.grid(row=i + 1, column=1, padx=10, pady=5, sticky='ew')

            self.propeller_entries[label_text] = entry

        add_button = ttk.Button(
            self.propeller_tab, text="Add Propeller", command=self.add_propeller)
        add_button.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

    def create_test_info_tab(self):
        """Создает вкладку с историей тестов"""
        self.test_info_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.test_info_tab, text="Test History")

        self.test_info_label = ttk.Label(
            self.test_info_tab, text="Test History", font=("Arial", 14))
        self.test_info_label.pack(pady=10)

        # Фрейм для списка тестов
        self.test_list_frame = ttk.Frame(self.test_info_tab)
        self.test_list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.update_test_list()

    def update_test_list(self):
        """Обновляет список тестов или выводит сообщение, если тестов нет"""
        # Чистим фрейм для обновления данных
        for widget in self.test_list_frame.winfo_children():
            widget.destroy()

        if not os.path.exists(self.test_history_file) or os.path.getsize(self.test_history_file) == 0:
            # Если тестов нет, показываем стильное сообщение
            no_tests_label = ttk.Label(self.test_list_frame, text="No tests have been conducted yet.",
                                       font=("Arial", 16), foreground="red")
            no_tests_label.pack(pady=20)
        else:
            # Если тесты есть, создаем список
            with open(self.test_history_file, 'r') as f:
                lines = f.readlines()

            for line in lines:
                engine, propeller, date = line.strip().split(',')
                # Создаем collapsible панель для каждого теста
                self.create_test_item(engine, propeller, date)

    def create_test_item(self, engine, propeller, date):
        """Создает элемент теста в виде collapsible панели"""
        frame = ttk.Frame(self.test_list_frame)
        frame.pack(fill='x', pady=5)

        header_frame = ttk.Frame(frame)
        header_frame.pack(fill='x')

        # Заголовок с информацией о двигателе, пропеллере и дате
        header_label = ttk.Label(header_frame, text=f"{engine} | {propeller} | {date}",
                                 font=("Arial", 12, "bold"))
        header_label.pack(side="left", fill='x')

        # Кнопка для раскрытия
        toggle_button = ttk.Button(
            header_frame, text="Details", command=lambda: self.toggle_details(details_frame))
        toggle_button.pack(side="right")

        # Фрейм для отображения деталей (сначала скрыт)
        details_frame = ttk.Frame(frame)
        details_frame.pack(fill='x', padx=20, pady=5)
        details_frame.pack_forget()  # Скрываем до нажатия

        # Добавляем пример деталей (будут реальные данные позже)
        details_label = ttk.Label(
            details_frame, text="Detailed information about the test...")
        details_label.pack(fill='x')

    @staticmethod
    def toggle_details(self, frame):
        """Скрыть/показать детали теста"""
        if frame.winfo_viewable():
            frame.pack_forget()
        else:
            frame.pack(fill='x', padx=20, pady=5)

    def check_for_updates(self):
        """Проверяет, изменился ли файл, и обновляет список тестов"""
        try:
            current_modified_time = os.path.getmtime(self.test_history_file)
            if self.last_modified_time is None or current_modified_time > self.last_modified_time:
                self.last_modified_time = current_modified_time
                self.update_test_list()
        except FileNotFoundError:
            self.last_modified_time = None
            self.update_test_list()

        # Запускаем проверку снова через заданный интервал
        self.after(self.update_interval, self.check_for_updates)

    # Пример тестового файла с данными
    def initialize_test_data(self):
        """Создаем тестовый файл с данными, если его нет"""
        if not os.path.exists(self.test_history_file):
            with open(self.test_history_file, 'w') as f:
                f.write("Engine1,Propeller1,2024-09-08\n")
                f.write("Engine2,Propeller2,2024-09-07\n")

    def create_port_selection(self):
        self.port_frame = ttk.Frame(self)
        self.port_frame.pack(pady=10, padx=10, fill='x')

        self.port_label = ttk.Label(self.port_frame, text="Select COM Port:")
        self.port_label.pack(side='left', padx=5)

        self.port_combobox = ttk.Combobox(self.port_frame)
        self.port_combobox['values'] = self.get_ports()
        self.port_combobox.pack(side='left', padx=5)

        # Кнопка для проверки порта
        self.check_button = ttk.Button(
            self.port_frame, text="Check Port", command=self.check_port)
        self.check_button.pack(side='left', padx=5)

        # Кнопка для запуска теста
        self.test_button = ttk.Button(
            self.port_frame, text="Run Test", command=self.run_test)
        self.test_button.pack(side='left', padx=5)

        # Лейбл для отображения результатов проверки порта
        self.test_result_label = ttk.Label(
            self.port_frame, text="", foreground="red")
        self.test_result_label.pack(side='left', padx=5)

    def get_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports if ports else ["No Ports Available"]

    def check_port(self):
        selected_port = self.port_combobox.get()
        if selected_port == "No Ports Available":
            self.test_result_label.config(
                text="No ports available", foreground="red")
            return

        try:
            with serial.Serial(selected_port, 9600, timeout=2) as ser:
                ser.write(b"TEST\n")
                response = ser.readline().decode().strip()
                if response == "OK":
                    self.test_result_label.config(
                        text="Port is working", foreground="green")
                else:
                    self.test_result_label.config(
                        text="Invalid response", foreground="red")
        except Exception as e:
            self.test_result_label.config(text=f"Error: {e}", foreground="red")

    def run_test(self):
        selected_port = self.port_combobox.get()
        if selected_port == "No Ports Available":
            self.test_result_label.config(
                text="No ports available", foreground="red")
            return

        try:
            with serial.Serial(selected_port, 9600, timeout=2) as ser:
                ser.write(b"START\n")
                response = ser.readline().decode().strip()
                if response == "OK":
                    self.test_result_label.config(
                        text="Test started", foreground="green")
                else:
                    self.test_result_label.config(
                        text="Invalid response", foreground="red")
        except Exception as e:
            self.test_result_label.config(text=f"Error: {e}", foreground="red")

    def add_engine(self):
        engine_data = {label: entry.get()
                       for label, entry in self.engine_entries.items()}
        with open(self.engine_file, 'a') as f:
            f.write(','.join(engine_data.values()) + '\n')
        self.update_dropdowns()

    def add_propeller(self):
        propeller_data = {label: entry.get()
                          for label, entry in self.propeller_entries.items()}
        with open(self.propeller_file, 'a') as f:
            f.write(','.join(propeller_data.values()) + '\n')
        self.update_dropdowns()

    def update_dropdowns(self):
        self.engine_combobox['values'] = self.load_engine_list()
        self.propeller_combobox['values'] = self.load_propeller_list()

    def load_engine_list(self):
        if os.path.exists(self.engine_file):
            with open(self.engine_file, 'r') as f:
                return [line.split(',')[0] for line in f]
        return ["No Engines Available"]

    def load_propeller_list(self):
        if os.path.exists(self.propeller_file):
            with open(self.propeller_file, 'r') as f:
                return [line.split(',')[0] for line in f]
        return ["No Propellers Available"]

    def update_graphs(self, rpm, moment, thrust):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.create_graph_panel(self.ax1, "RPM")
        self.create_graph_panel(self.ax2, "Moment")
        self.create_graph_panel(self.ax3, "Thrust")
        self.ax1.plot(rpm, label='RPM')
        self.ax2.plot(moment, label='Moment')
        self.ax3.plot(thrust, label='Thrust')
        self.ax1.legend()
        self.ax2.legend()
        self.ax3.legend()
        self.canvas.draw()


if __name__ == "__main__":
    app = TestApp()
    app.initialize_test_data()  # Инициализация тестовых данных
    app.mainloop()
