import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror
import pickle

colors = {
    1: '#0805b3',
    2: '#e8ad0c',
    3: '#f2493d',
    4: '#08055e',
    5: '#520b03',
    6: '#156b5b',
    7: '#8a1c77',
    8: '#21d95b'  # Словник з кольорами для кнопок
}


class Button(tk.Button):  # Клас кнопки

    def __init__(self, master, x, y, number=0):
        '''Функція ініціалізації кнопок'''
        super(Button, self).__init__(master, width='3', font=('Areal 15 bold'))
        self.x = x  # Координата х
        self.y = y  # Координата у
        self.number = number  # Порядковий номер кнопки
        self.is_mine = False  # Чи є кнопка міною
        self.amount_bombs = 0  # Кількість мін у сусідніх кнопках
        self.is_open = False  # Чи буда ця кнопка натиснута


class Mines:  # Клас ігрового поля та всієї гри
    win = tk.Tk()  # Головне вікно
    ROW = 9  # Кількість рядків
    COLUMN = 9  # Кількість колонок
    AMOUNT_OF_MINES = 9  # Загальна кількість мін
    GAME_OVER = False  # Чи завершена гра
    FIRST_ClICK = True  # Чи це перше натискання
    RUNNING = True  # Параметр необхідний для запуску секундоміру

    def __init__(self):
        """Функція, яка ініціалізує кнопки та зчитує натискання на них"""
        self.buttons = []
        for i in range(Mines.ROW + 2):  # +2, тому що 1й рядок - бар'єрний, його кнопки не входять до списку звичайних
            temp = []  # Список, який містить координати усіх кнопок
            for j in range(Mines.COLUMN + 2):
                btn = Button(Mines.win, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button))  # Команда, яка робить кнопку натиснутою
                btn.bind('<Button-3>', self.right_click)  # Обробка натискання правою кнопкою миші
                btn.bind('<Button-2>', self.wheel_click)  # Обробка натискання колещатком миші
                temp.append(btn)
            self.buttons.append(temp)

    def create_widgets(self):
        """Функція, яка розміщує всі елементи на полі. Також вона створює секундомір"""
        Mines.win.title('Minesweeper')
        timer = tk.Label(self.win, text="0", fg="black", font="Verdana 30 bold")
        timer.grid(row=0, column=2, columnspan=2, sticky='nsew')
        bomb_count_label = tk.Label(self.win, text=Mines.AMOUNT_OF_MINES, fg="black", font="Verdana 30 bold")
        bomb_count_label.grid(row=0, column=8, columnspan=2, sticky='nsew')

        def counter_label(timer):
            def count():
                if Mines.RUNNING:
                    display = str(Mines.counter)
                    timer.config(text=display)
                    timer.after(1000, count)
                    Mines.counter += 1

            count()

        counter_label(timer)

        menubar = tk.Menu(self.win)
        self.win.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Перезапуск', command=self.restart)
        settings_menu.add_command(label='Настройки', command=self.create_settings)
        settings_menu.add_command(label='Выход', command=self.exit)
        menubar.add_cascade(label='Файл', menu=settings_menu)
        settings_menu_reg = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Пользователь', menu=settings_menu_reg)
        settings_menu_reg.add_command(label='Войти', command=self.login)
        settings_menu_reg.add_command(label='Зарегестрироваться', command=self.registration)
        settings_menu_reg.add_command(label='Таблица лидеров', command=self.rates_table)

        count = 1
        for i in range(1, Mines.ROW + 1):
            for j in range(1, Mines.COLUMN + 1):
                btn = self.buttons[i][j]
                btn.config(relief='raised')
                btn.number = count
                btn.grid(row=i, column=j, stick='NESW')
                count += 1

        for i in range(1, Mines.ROW + 1):
            tk.Grid.grid_rowconfigure(self.win, i, weight=1)
        for j in range(1, Mines.COLUMN + 1):
            tk.Grid.grid_columnconfigure(self.win, j, weight=1)

    def starting(self):
        """Функція запуску гри"""
        self.create_widgets()
        Mines.win.mainloop()

    cur_amount = AMOUNT_OF_MINES
    bad_flags = []  # Список з номерами мін, які не є бомбами, але на них стоять флажки

    def right_click(self, event):
        """Функція, яка обробляє натискання правої кнопки миші.
        Також вона виводить лічильник бомб, обробляє перемогу та підраховує
        кількість балів гравця за гру"""
        bomb_count_label = tk.Label(self.win, text=Mines.AMOUNT_OF_MINES, fg="black", font="Verdana 30 bold")
        bomb_count_label.grid(row=0, column=8, columnspan=2, sticky='nsew')  # Поле лічильника

        if Mines.GAME_OVER:  # Це необхідно для того, щоб після поразки не можна було ставити нові прапорці
            return
        cur_btn = event.widget


        if cur_btn['state'] == 'normal':
            cur_btn['state'] = 'disabled'
            cur_btn['text'] = '🚩'
            cur_btn['disabledforeground'] = 'red'
            Mines.cur_amount -= 1
            bomb_count_label['text'] = Mines.cur_amount  # Зміна значення на лічильнику
            if cur_btn.number in Mines.static_bombs_places:
                Mines.bomb_places.remove(cur_btn.number)  # Видалення номеру натиснутої кнопки із списка з бомбами
            else:
                Mines.bad_flags.append(cur_btn.number)  # Додавання номеру кнопки, якщо це не міна
            print(Mines.bad_flags)
        elif cur_btn['text'] == '🚩':
            cur_btn['text'] = ''
            cur_btn['state'] = 'normal'
            Mines.cur_amount += 1
            bomb_count_label['text'] = Mines.cur_amount  # Зміна значення на лічильнику
            if cur_btn.number in Mines.static_bombs_places:  #
                Mines.bomb_places.append(cur_btn.number)  # Додавання номеру натиснутої кнопки до списка з бомбами
            else:
                Mines.bad_flags.remove(cur_btn.number)  # Видалення номеру кнопки, якщо це не міна
        if Mines.bomb_places == [] and Mines.cur_amount == 0:  # Умова перемоги: жодної бомби в списку з бомбами
            # та жодного зайвого прапорця
            Mines.RUNNING = False  # Зупинка секундоміра
            showinfo('WIN!', 'Вы выграли!')  # Показ повідомлення про перемогу
            Mines.cur_points = Mines.AMOUNT_OF_MINES - Mines.cur_amount - len(Mines.bad_flags)  # Кількість
            # вгаданих мін
            if Mines.ind != -1:
                Mines.rate_l[Mines.ind] = int(Mines.rate_l[Mines.ind]) + int(Mines.cur_points)  # Підрахунок балів
            with open('rate', 'wb') as f:
                pickle.dump(Mines.rate_l, f)  # Завантаження оновлених результатів до файлу
            Mines.GAME_OVER = True  # Ввімкнення стану програшу

    def wheel_click(self, event):
        """Функція, яка обробляє натискання колещатка миші"""
        if Mines.GAME_OVER:
            return
        cur_btn = event.widget
        if cur_btn['state'] == 'normal':
            cur_btn['state'] = 'disabled'
            cur_btn['text'] = '?'
            cur_btn['disabledforeground'] = '#eb7434'
        elif cur_btn['text'] == '?':
            cur_btn['text'] = ''
            cur_btn['state'] = 'normal'

    clicked_buttons = []  # Список натиснутих кнопок

    cur_points = 0  # Кількість очків

    def click(self, clicked_button: Button):
        """Функція, яка обробляє натискання миші на кнопку. Є однією з найголовніших функцій.
         Також обробляє поразку"""
        if Mines.FIRST_ClICK:  # Перевірка, чи є це натискання першим
            self.insert_mines(clicked_button.number)  # Метод, який розставляє міни
            self.amount_mines_near()  # Метод, який рахує кількість мін поряд з кнопкою
            self.print_buttons()  # Метод, який виводить в консоль координати кнопок та міни
            Mines.FIRST_ClICK = False

        if Mines.GAME_OVER:
            return None

        color = colors.get(clicked_button.amount_bombs, 'black')
        if clicked_button.is_mine:  # Натиснута кнопка - міна
            clicked_button.config(text='💣', bg='red', disabledforeground='black')
            clicked_button.is_open = True
            Mines.RUNNING = False
            Mines.GAME_OVER = True
            showinfo('GAME OVER', 'Вы проиграли!')
            print('bad_f:', len(Mines.bad_flags))
            Mines.cur_points = Mines.AMOUNT_OF_MINES - Mines.cur_amount - len(Mines.bad_flags)
            print('rate: ', Mines.rate_l)
            print(('ind', Mines.ind))
            if Mines.ind != -1:
                Mines.rate_l[Mines.ind] = int(Mines.rate_l[Mines.ind]) + int(Mines.cur_points)
                print(Mines.sort(Mines.rate_l_dinamic))
                # Mines.load_result_dic()[Mines.cur_user].append(Mines.cur_points)
                Mines.result_dic_updated[Mines.cur_user].append(Mines.cur_points)
                print(Mines.result_dic_updated)
                with open('result_dict', 'wb') as f:
                    pickle.dump(Mines.result_dic_updated, f)
            with open('rate', 'wb') as f:
                pickle.dump(Mines.rate_l, f)
            for i in range(1, Mines.ROW + 1):  # Прояв усіх мін
                for j in range(1, Mines.COLUMN + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn['text'] = '💣'
        elif clicked_button.amount_bombs:  # Натиснута кнопка не міна, але поряд є міни
            clicked_button.config(text=clicked_button.amount_bombs, disabledforeground=color)
            clicked_button.is_open = True
            Mines.clicked_buttons.append(clicked_button.number)
        else:  # Натиснута кнопка не міна, і мін поряд немає
            clicked_button.config(text='')
            clicked_button.is_open = True
            for row in [-1, 0, 1]:  # Відкривання "пустої" зони
                for col in [-1, 0, 1]:
                    btn = self.buttons[clicked_button.x + row][clicked_button.y + col]
                    if not btn.is_open and btn.number != 0 and btn['text'] != '🚩' and btn['text'] != '?':
                        self.click(btn)
        clicked_button.config(state='disabled')
        clicked_button.config(relief=tk.SUNKEN)

    def restart(self):
        """Функція, яка перезапускає гру не виходячи з головного вікна.
        Фактично вона відкатує усі налаштування гри до початкових"""
        [child.destroy() for child in self.win.winfo_children()]  # Руйнування усіх кнопок
        self.__init__()
        Mines.RUNNING = True
        Mines.counter = 0
        self.create_widgets()
        Mines.all_places.clear()
        Mines.bomb_places.clear()
        Mines.clicked_buttons.clear()
        Mines.static_bombs_places.clear()
        Mines.cur_amount = Mines.AMOUNT_OF_MINES
        Mines.FIRST_ClICK = True
        Mines.GAME_OVER = False

    def change_settings(self, row: tk.Entry, column: tk.Entry, mines: tk.Entry):
        """Функція, яка дозволяє гравцю самостійно ввести розміри поля та кількість мін"""
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:  # Якщо значення - не цілі числа
            showerror('Ошибка', 'Вы ввели неправильное значение!')
            return
        Mines.ROW = int(row.get())
        Mines.COLUMN = int(column.get())
        Mines.AMOUNT_OF_MINES = int(mines.get())
        self.restart()

    def create_settings(self):
        """Функція, яка створює вікно налаштувань"""
        win_settings = tk.Toplevel(self.win)
        win_settings.wm_title('Настройки')
        tk.Label(win_settings, text='Количество строк').grid(row=0, column=0)
        tk.Label(win_settings, text='Количество колонок').grid(row=1, column=0)
        tk.Label(win_settings, text='Количество мин').grid(row=2, column=0)
        row_entry = tk.Entry(win_settings)
        row_entry.insert(0, Mines.ROW)
        row_entry.grid(row=0, column=1, padx=20, pady=20)
        col_entry = tk.Entry(win_settings)
        col_entry.insert(0, Mines.COLUMN)
        col_entry.grid(row=1, column=1, padx=20, pady=20)
        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, Mines.AMOUNT_OF_MINES)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)
        save_btn = tk.Button(win_settings, text='Применить',
                             command=lambda: self.change_settings(row_entry, col_entry, mines_entry))
        save_btn.grid(row=4, column=1, columnspan=2, pady=20, sticky='w')

        def select_lvl():
            """Функція, необхідна для зчитування того, який режим обрав гравець.
            Вона вводить сталі розміри поля та кількості мін"""
            lvl = lvl_var.get()
            if lvl == 1:
                Mines.ROW = 9
                Mines.COLUMN = 9
                Mines.AMOUNT_OF_MINES = 10
                self.restart()
            elif lvl == 2:
                Mines.ROW = 16
                Mines.COLUMN = 16
                Mines.AMOUNT_OF_MINES = 40
                self.restart()
            elif lvl == 3:
                Mines.ROW = 16
                Mines.COLUMN = 30
                Mines.AMOUNT_OF_MINES = 90
                self.restart()

        lvl_var = tk.IntVar()
        tk.Radiobutton(win_settings, text='Новичок', variable=lvl_var, value=1, command=select_lvl).grid(row=3,
                                                                                                         column=0)
        tk.Radiobutton(win_settings, text='Любитель', variable=lvl_var, value=2, command=select_lvl).grid(row=3,
                                                                                                          column=1)
        tk.Radiobutton(win_settings, text='Эксперт', variable=lvl_var, value=3, command=select_lvl).grid(row=3,
                                                                                                         column=2)

    def exit(self):
        """Функція, яка обробляє вихід з гри. Також в ній реалізован запит про збереження гри"""

        save_ask = tk.Toplevel(self.win)
        save_ask.wm_title('Сохранение')
        save_ask.geometry('200x100')
        tk.Label(save_ask, text='').grid(row=1, column=1)
        tk.Label(save_ask, text='        Сохранить результат игры?').grid(row=2, column=1, columnspan=2, sticky='es')
        tk.Label(save_ask, text='').grid(row=3, column=1)
        yes_button = tk.Button(save_ask, text='Да', command=lambda:
        [Mines.saving(Mines.static_bombs_places), Mines.load(), Mines.saving_click(Mines.clicked_buttons),
         Mines.load_click(), Mines.win.destroy()])
        yes_button.grid(row=4, column=1, sticky='se')
        no_button = tk.Button(save_ask, text='Нет', command=lambda: [Mines.clearing(), Mines.win.destroy()])
        no_button.grid(row=4, column=2, sticky='s')

    def saving(bomb_places):
        """Функція, яка зберігає положення бомб даної гри у файл"""
        Mines.SAVING = True
        with open('bin_saving', 'wb') as f:
            pickle.dump(bomb_places, f)

    def load():
        """Функція, яка зчитує положення бомб даної гри з файлу"""
        try:
            with open('bin_saving', 'rb') as f:
                return pickle.load(f)
        except EOFError:
            return None

    bin_saving_bombs = load()

    def saving_click(click_places):
        """Функція, яка зберігає номери натиснутих кнопок у файл"""
        Mines.SAVING = True
        with open('bin_saving_click', 'wb') as f:
            pickle.dump(click_places, f)

    def load_click():
        """Функція, яка зчитує номери натиснутих кнопок з файлу"""
        try:
            with open('bin_saving_click', 'rb') as k:
                return pickle.load(k)
        except EOFError:
            return None

    bin_clicked_buttons = load_click()

    def clearing():
        """Функція, яка очищує файли, в яких зберігалися положення мін на натиснутих кнопок"""
        open('bin_saving', 'w').close()
        open('bin_saving_click', 'w').close()

    logins = []
    passwords = []
    rates = []

    def registration(self):
        """Функція, яка створює вікно реєстрації"""

        def get_inf():
            login_inf = login.get()
            password_inf = password.get()
            check_pass = password_check.get()
            if login_inf == '':
                showerror('Ошибка!', 'Введите логин')
            elif login_inf in Mines.login_l:
                showerror('Ошибка!', 'Имя занято')
            elif password_inf == '':
                showerror('Ошибка!', 'Введите пароль')
            elif len(password_inf) < 8:
                showerror('Ошибка!', 'Пароль должен содержать минимум 8 символов')
            elif check_pass == '':
                showerror('Ошибка!', 'Введите пароль повторно')
            elif password_inf != check_pass:
                showerror('Ошибка!', 'Пароли не совпадают')
            else:
                Mines.login_l.append(login_inf)
                Mines.password_l.append(password_inf)
                Mines.rate_l.append(0)
                print(Mines.login_l)
                print(Mines.password_l)
                print(Mines.rate_l)
                with open('logins', 'wb') as f:
                    pickle.dump(Mines.login_l, f)
                with open('passwords', 'wb') as f:
                    pickle.dump(Mines.password_l, f)
                with open('rate', 'wb') as f:
                    pickle.dump(Mines.rate_l, f)
                reg_win.destroy()

        def show_pass():
            """Функція, яка змінює "*" на символи, які насправді були введені в паролі"""
            password['text'] = password.get()

        reg_win = tk.Toplevel(self.win)
        reg_win.attributes('-topmost', True)
        reg_win.wm_title('Регистрация')
        reg_win.geometry('300x250')
        tk.Label(reg_win, text='Введите логин').grid(row=0, column=0)
        tk.Label(reg_win, text='Введите пароль').grid(row=1, column=0)
        tk.Label(reg_win, text='Повторите пароль').grid(row=2, column=0)
        login = tk.Entry(reg_win)
        login.grid(row=0, column=1, padx=20, pady=20)
        password = tk.Entry(reg_win, show='*')
        password.grid(row=1, column=1, padx=20, pady=20)
        password_check = tk.Entry(reg_win, show='*')
        password_check.grid(row=2, column=1, padx=20, pady=20)
        save_btn = tk.Button(reg_win, text='Oк', height=1, width=6, command=get_inf)
        save_btn.grid(row=4, column=0, pady=20)
        show_btn = tk.Button(reg_win, text='Показать пароль', height=1, width=13, command=show_pass)
        show_btn.grid(row=4, column=1, pady=20)

    def rate_load():
        """Функція, яка зчитує список з рейтингами гравців з файлу"""
        try:
            with open('rate', 'rb') as f:
                return pickle.load(f)
        except EOFError:
            return []

    rate_l = rate_load()
    rate_l_dinamic = rate_load()
    rate_l_dinamic2 = rate_load()

    def login_load():
        """Функція, яка зчитує список з логінами гравців з файлу"""
        try:
            with open('logins', 'rb') as f:
                return pickle.load(f)
        except EOFError:
            return []

    login_l = login_load()
    login_l_dinamic = login_load()

    def password_load():
        """Функція, яка зчитує список з паролями гравців з файлу"""
        try:
            with open('passwords', 'rb') as f:
                return pickle.load(f)
        except EOFError:
            return []

    password_l = password_load()

    print(rate_l)
    print(login_l)
    print(password_l)

    result_dict = {login_l: [] for login_l in login_l}

    def load_result_dic():
        """Функція, яка зчитує результати гравців з файлу"""
        try:
            with open('result_dict', 'rb') as k:
                return pickle.load(k)
        except EOFError:
            return None

    result_dic_updated = load_result_dic()
    print(result_dic_updated)
    cur_user = ''
    ind = -1

    def login(self):
        """Функція, яка створює вікно аутентифікації"""

        def get_inf_2():
            login_inf = login.get()
            password_inf = password.get()
            if login_inf == '':
                showerror('Ошибка!', 'Введите логин')
            elif password_inf == '':
                showerror('Ошибка!', 'Введите пароль')
            elif login_inf not in Mines.login_l:
                showerror('Ошибка!', 'Такой пользователь не найден')
            else:
                Mines.ind = Mines.login_l.index(login_inf)
                if password_inf != Mines.password_l[Mines.ind]:
                    showerror('Ошибка!', 'Неправильный пароль')
                elif password_inf == Mines.password_l[Mines.ind]:
                    Mines.cur_user = login_inf
                    print('cur user: ', Mines.cur_user)
                    print('ind: ', Mines.ind)
                log_win.destroy()

        log_win = tk.Toplevel(self.win)
        log_win.wm_title('Авторизация')
        log_win.attributes('-topmost', True)
        log_win.geometry('300x200')
        tk.Label(log_win, text='Введите логин').grid(row=0, column=0)
        tk.Label(log_win, text='Введите пароль').grid(row=1, column=0)
        login = tk.Entry(log_win)
        login.grid(row=0, column=1, padx=20, pady=20)
        password = tk.Entry(log_win, show='*')
        password.grid(row=1, column=1, padx=20, pady=20)
        save_btn = tk.Button(log_win, text='Oк', height=1, width=6, command=get_inf_2)
        save_btn.grid(row=4, column=0, columnspan=2, pady=20)

    sort_logins = []

    def sort(rate_list):
        """Функція, яка сортує логіни гравців. На 1шому місці стає той, у кого найбільше балів"""
        n = len(rate_list)
        for i in range(n):
            maxi_ind = rate_list.index(max(rate_list))
            Mines.sort_logins.append(Mines.login_l_dinamic[maxi_ind])
            rate_list.pop(maxi_ind)
            Mines.login_l_dinamic.pop(maxi_ind)
        return Mines.sort_logins

    sort_rates_ = []

    def sort_rates(rate_list):
        """Функція, яка сортує бали гравців."""
        n = len(rate_list)
        for i in range(n):
            maxi_ind = rate_list.index(max(rate_list))
            Mines.sort_rates_.append(Mines.rate_l_dinamic2[maxi_ind])
            rate_list.pop(maxi_ind)
        return Mines.sort_rates_







    def rates_table(self):
        """Функція, яка створює рейтингове вікно"""

        def on_click(event):
            '''Функція, яка повертає текст натиснутої кнопки у вікні рейтингу'''
            global button_text
            button_text = event.widget.cget('text')
            return button_text



        def results():
            """Функція, яка створює вікно результатів кожного гравця"""
            self_res_win = tk.Toplevel(Mines.win)
            self_res_win['bg'] = "#FAFAFA"
            self_res_win.wm_title('Результаты')
            self_res_win.attributes('-topmost', True)
            self_res_win.geometry('600x200')
            user_name = tk.Label(self_res_win, height=1, text=f"Результаты игрока {button_text}:", bg="#FAFAFA",
                                 font="Bahnschrift 16")
            user_name.place(relx=0.5, y=15, anchor="center")
            user_results = tk.Label(self_res_win, height=1, text=Mines.result_dic_updated[button_text][10::-1],
                                    bg="#FAFAFA", font="Bahnschrift 16")
            user_results.place(relx=0.5, y=80, anchor="center")


        rate_win = tk.Toplevel(self.win)
        rate_win['bg'] = "#FAFAFA"
        rate_win.wm_title('Рейтинг')
        rate_win.attributes('-topmost', True)
        user_text = tk.Label(rate_win, height=1, text="Игрок", bg="#FAFAFA", font="Bahnschrift 16")
        score_text = tk.Label(rate_win, height=1, text="Счет", bg="#FAFAFA", font="Bahnschrift 16")
        user_text.place(relx=0.1, y=30, anchor="w")
        score_text.place(relx=0.9, y=30, anchor="e")
        pos = 80
        p = 0.15
        rate_win.resizable(False, False)
        for i, j in zip(Mines.sort(Mines.rate_l_dinamic), Mines.sort_rates(Mines.rate_l_dinamic2)):
            user_t = tk.Button(rate_win, height=1, text=i, bg="#FAFAFA", font="Bahnschrift 14", relief="flat",
                               command= results)
            user_t.place(relx=0.12, rely=p, anchor="w")
            user_t.bind('<Button-1>', on_click)
            user_sc = tk.Label(rate_win, height=1, text=j, bg="#FAFAFA", font="Bahnschrift 14")
            user_sc.place(relx=0.8, rely=p-0.035)
            p += 0.08
            rate_win.geometry(f'300x{pos + 40}')
            pos += 40

    counter = 0

    all_places = []
    bomb_places = []
    static_bombs_places = []

    def print_buttons(self):
        """Функція, яка виводить розміщення бомб та звичайних кнопок в консоль"""
        for i in range(1, Mines.ROW + 1):
            for j in range(1, Mines.COLUMN + 1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    print('B', end=' ')
                else:
                    print(btn.amount_bombs, end=' ')
            print()
        num = 1
        for i in range(1, Mines.ROW + 1):
            for j in range(1, Mines.COLUMN + 1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    Mines.all_places.append('B')
                else:
                    Mines.all_places.append(num)
                num += 1
        print(Mines.all_places)
        index = 1
        for i in Mines.all_places:
            if i == 'B':
                Mines.bomb_places.append(index)
            index += 1
        print(Mines.bomb_places)

        index1 = 1
        for i in Mines.all_places:
            if i == 'B':
                Mines.static_bombs_places.append(index1)
            index1 += 1

    def insert_mines(self, number: int):
        """Функція, яка розставляє міни"""
        ind_mines = self.mines_places(number)
        for i in range(1, Mines.ROW + 1):
            for j in range(1, Mines.COLUMN + 1):
                btn = self.buttons[i][j]
                if btn.number in ind_mines:
                    btn.is_mine = True

    def amount_mines_near(self):
        for i in range(1, Mines.ROW + 1):
            for j in range(1, Mines.COLUMN + 1):
                btn = self.buttons[i][j]
                amount_bombs = 0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neighbor = self.buttons[i + row_dx][j + col_dx]
                            if neighbor.is_mine:
                                amount_bombs += 1
                btn.amount_bombs = amount_bombs

    def mines_places(self, exclude_number):
        """Функція, яка створює список із мінами"""
        ind = list(range(1, Mines.ROW * Mines.COLUMN + 1))
        ind.remove(exclude_number)
        shuffle(ind)
        return ind[:Mines.AMOUNT_OF_MINES]


game = Mines()
game.starting()
