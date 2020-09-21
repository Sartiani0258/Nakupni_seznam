import tkinter as tk
import psycopg2 # PostgreSQL
import shopping_list_back


class CustomerDataWin(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry('700x600-300-100')
        self.title("Udaje o zakaznikovy")

        # ===========Main frame & address frame=============
        main_label_frame = tk.LabelFrame(self, text='Your contact and billing details',
                                         bg='light blue', relief='groove')
        main_label_frame.pack(fill='both')
        address_label_frame = tk.LabelFrame(main_label_frame, text='Billing Address',
                                            bg='light blue', pady=10,
                                            relief='ridge')
        address_label_frame.grid(row=3, column=0, columnspan=2, sticky='w')
        # =========Popisne polia========================
        LabelClass(main_label_frame, "First name: ", 0, 0)
        LabelClass(main_label_frame, "Last name: ", 1, 0)
        LabelClass(main_label_frame, "Company: ", 2, 0)
        LabelClass(address_label_frame, "Street: ", 0, 0)
        LabelClass(address_label_frame, "City: ", 1, 0)
        LabelClass(address_label_frame, "ZIP: ", 2, 0)
        LabelClass(address_label_frame, "Phone: ", 0, 2)
        LabelClass(address_label_frame, "email: ", 1, 2)
        # ==============input polia ==================
        main_label_frame.columnconfigure(1, weight=1)
        self._first_name_txt = tk.Text(main_label_frame, height=1, width=15)
        self._first_name_txt.grid(row=0, column=1, sticky='w')

        self._last_name_txt = tk.Text(main_label_frame, height=1, width=15)
        self._last_name_txt.grid(row=1, column=1, sticky='w')
        self._company_txt = tk.Text(main_label_frame, height=1, width=15)
        self._company_txt.grid(row=2, column=1, sticky='w')

        self._street_txt = tk.Text(address_label_frame, height=1, width=30)
        self._street_txt.grid(row=0, column=1)
        self._city_txt = tk.Text(address_label_frame, height=1, width=30)
        self._city_txt.grid(row=1, column=1)
        self._zip_txt = tk.Text(address_label_frame, height=1, width=30)
        self._zip_txt.grid(row=2, column=1)
        self._phone_txt = tk.Text(address_label_frame, height=1, width=30)
        self._phone_txt.grid(row=0, column=3)
        self._email_txt = tk.Text(address_label_frame, height=1, width=30)
        self._email_txt.grid(row=1, column=3)
        # =============Button back & proceed ========================
        conf_button = tk.Button(main_label_frame, height=1, width=10, text='Proceed', command=self.read_data_input)
        conf_button.grid(row=4, column=2, sticky='es')

        back_button = tk.Button(main_label_frame, height=1, width=10, text='Back', command=self.first_window_items)
        back_button.grid(row=4, column=0, sticky='es')

    def read_data_input(self):  # nacita data z input text boxov
        first_name = self._first_name_txt.get('1.0', 'end')
        last_name = self._last_name_txt.get('1.0', 'end')
        company = self._company_txt.get('1.0', 'end')
        street = self._street_txt.get('1.0', 'end')
        city = self._city_txt.get('1.0', 'end')
        zip_ = self._zip_txt.get('1.0', 'end')
        phone = self._phone_txt.get('1.0', 'end')
        email = self._email_txt.get('1.0', 'end')
        customer_data = dict(first_name=first_name, last_name=last_name, company=company,
                             street=street, city=city, zip=zip_, phone=phone, email=email)
        DatabazaZakaznik(customer_data)
        CustomerDataWin.destroy(self)
        ProceedWindow()

    # vymaz ak nepotrebujes
    @staticmethod   # staticmethod lebo ju pouzivam v ramci inej init method
    def first_window_items():
        global customer_data_shopping_list

        if not customer_data_shopping_list:
            ruzinov = shopping_list_back.DatabazaElektro()
            nakupny_zoznam_window = shopping_list_back.FirstWindow()
            nakupny_zoznam_window.vloz_tov_do_listbox(ruzinov)
            nakupny_zoznam_window.mainloop()
            ruzinov.new_db.close()
            customer_data_shopping_list = nakupny_zoznam_window.nakup_v_kosiku
            # print('z funkcie3', customer_data_shopping_list)

            return customer_data_shopping_list

        else:
            print('customer data neni prazdne')
            ruzinov1 = shopping_list_back.DatabazaElektro()
            nakupny_zoznam_window1 = shopping_list_back.FirstWindow()
            nakupny_zoznam_window1.vloz_tov_do_listbox(ruzinov1)
            nakupny_zoznam_window1.mainloop()
            ruzinov1.new_db.close()
            customer_data_shopping_list += nakupny_zoznam_window1.nakup_v_kosiku

            return customer_data_shopping_list


class LabelClass(tk.Label):
    def __init__(self, container, text, row, column, bg='light gray', *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self['bg'] = bg
        self['text'] = text
        self.grid(row=row, column=column, sticky='w')


class DatabazaZakaznik(object):
    def __init__(self, data):
        self.new_db = psycopg2.connect(database='shopping_list', user='postgres',
                                       password='123456', host='localhost',
                                       port='5432')
        self.db_cursor = self.new_db.cursor()
        values = "(" + ','.join(["'" + str(i).rstrip() + "'" if i.rstrip() else 'NULL' for i in data.values()]) + ")"

        print(values)
        self.db_cursor.execute("INSERT INTO zakaznici (first_name, last_name, company, street, city, zip, phone, email)"
                                "VALUES {}".format(values))

        print("Customer data inserted")

        self.db_cursor.execute("SELECT customer_id FROM zakaznici "
                               "WHERE email LIKE '{}'".format(str(data['email']).rstrip()))
        customer_id = self.db_cursor.fetchone()
        for _id in customer_data_shopping_list:
            self.db_cursor.execute("INSERT INTO predany_tovar (tovar_id, customer_id) "
                               "VALUES ('{0}', '{1}')".format(_id[0], customer_id[0]))
        print("table predany_tovar updated")
        self.new_db.commit()
        self.new_db.close()


class ProceedWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry('700x600-300-100')
        self.title("Nakup potvrzen")
        tk.Label(self, text='Udaje vlozene a nakup realizovany', font=('Verdana', 20),
                 bg='light blue').pack(anchor='center', pady=200)


customer_data_shopping_list = list()

# =============== 1st window (items) ==============
shopping_list_okno = CustomerDataWin.first_window_items()
# =============== 2nd window (zakaznik) ==============
zakaznik_okno = CustomerDataWin()

print('Customer data shopping list', customer_data_shopping_list)
zakaznik_okno.mainloop()
