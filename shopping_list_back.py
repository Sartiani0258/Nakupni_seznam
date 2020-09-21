import tkinter as tk
import psycopg2
import pandas

# este by som tam mohol vlozit try - except ze pri hlaseni chyby v databaze, nam spravi rollback()
# a este by som mohol vlozit pooling


class DatabazaElektro(object):
    def __init__(self):

        self.new_db = psycopg2.connect(database='shopping_list', user='postgres',
                                       password='123456', host='localhost',
                                       port='5432')

        self.db_cursor = self.new_db.cursor()
        self.db_cursor.execute("CREATE TABLE IF NOT EXISTS tovar "
                               "(Popis VARCHAR(50) UNIQUE NOT NULL, "
                               "Cena INTEGER NOT NULL, tovar_id SERIAL PRIMARY KEY)")

        self.db_cursor.execute("CREATE TABLE IF NOT EXISTS zakaznici (customer_id SERIAL PRIMARY KEY, "
                               "first_name VARCHAR(50) NOT NULL, last_name VARCHAR(50) NOT NULL, "
                               "company TEXT, street TEXT, city TEXT, zip INTEGER, phone TEXT, "
                               "email TEXT UNIQUE NOT NULL)")

        self.db_cursor.execute("CREATE TABLE IF NOT EXISTS predany_tovar("
                               "tovar_id INTEGER REFERENCES tovar(tovar_id), "
                               "customer_id INTEGER REFERENCES zakaznici (customer_id))")

        # =====nacitanie dat z excelu ============
        path = 'Portfolio.xlsx'
        list_of_gadgets = self.load_items_from_excel(path=path)

        for item in list_of_gadgets:    # vlozi polozky do databazy ak tam uz nie su
            if not (self.check_if_inserted(item[0], table='tovar', column='Popis')):
                self.db_cursor.execute("INSERT INTO tovar (Popis, Cena) VALUES (%s, %s)", (item[0], item[1]))

        self.new_db.commit()
        self.data_gadgets_list = []

    def updated_list_of_gadgets(self):
        self.db_cursor.execute("SELECT * FROM tovar")
        new_fetchall = self.db_cursor.fetchall()
        [self.data_gadgets_list.append(item) for item in new_fetchall]
        return self.data_gadgets_list

    def check_if_inserted(self, checking_item, table, column):
        self.db_cursor.execute("SELECT {0} FROM {1} WHERE {0} = '{2}'".format(column, table, checking_item))
        row = self.db_cursor.fetchone()
        return row

    @staticmethod  # ak by som tuto funkciu chcel pouzit funkciu na iny subor a nechel pristupit k vlastnostiam class
    def load_items_from_excel(path: str):
        df = pandas.read_excel(path, header=0)
        return df.values.tolist()


class FirstWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('700x600-300-100')
        self.title("Vyber tovaru")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=2)

        self.nakup_v_kosiku = []
        self.ram_vonkajsi = tk.LabelFrame(self, borderwidth=2, fg='white',
                                          text='Choose items to buy', bg='blue')

        self.ram_vonkajsi.columnconfigure(0, weight=2)
        self.ram_vonkajsi.columnconfigure(1, weight=1)
        self.ram_vonkajsi.columnconfigure(2, weight=2)
        self.ram_vonkajsi.grid(row=0, column=0, pady=40, padx=40, sticky='nsew')

        # ==tovar listbox + scrollbar
        self.listbox_tovar_frame = tk.Frame(self.ram_vonkajsi)
        self.listbox_tovar_frame.grid(row=0, column=0)
        self.listbox_tovar = tk.Listbox(self.listbox_tovar_frame, height=28, width=40, selectmode="extended")

        self.listbox_tovar.grid(row=0, column=0, sticky='nsew')
        scrollbar = tk.Scrollbar(self.listbox_tovar_frame, orient=tk.VERTICAL, command=self.listbox_tovar.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.listbox_tovar['yscrollcommand'] = scrollbar.set

        button_arrow = tk.Button(self.ram_vonkajsi, text="->", width=10, command=self.handle_selection)
        button_arrow.grid(row=0, column=1)

        # ====suma v kosiku ====
        self.sum_buying_cart = tk.IntVar(value=0)
        sum_buying_cart_frame = tk.Frame(self.ram_vonkajsi, bg='red')
        sum_buying_cart_frame.grid(row=1, column=3, sticky='ew')
        tk.Label(sum_buying_cart_frame, text='Suma v kosiku:   ').grid(row=0, column=0)
        sum_buying_cart_lbl = tk.Label(sum_buying_cart_frame, textvariable=self.sum_buying_cart, bg='red')
        sum_buying_cart_lbl.grid(row=0, column=1)
        tk.Label(sum_buying_cart_frame, text='Eur', bg='red').grid(row=0, column=2)

        # === v nakupnom voziku ===
        self.nak_vozik_premenna = tk.StringVar(value="Nakupny_kosik_je_prazdny")
        self.listbox_nak_vozik = tk.Listbox(self.ram_vonkajsi, height=28, width=40,
                                            listvariable=self.nak_vozik_premenna)
        self.listbox_nak_vozik.grid(row=0, column=3, sticky="nsew")

        # =====next window button=====
        customer_win_button = tk.Button(self.ram_vonkajsi, text='Next step', command=self.next_window)
        customer_win_button.grid(row=2, column=3, sticky='e')

    def vloz_tov_do_listbox(self, parameter):   # nahra veci z listu do listboxu
        parameter.updated_list_of_gadgets()
        for item, price, _id in parameter.data_gadgets_list:
            self.listbox_tovar.insert(tk.END, (_id, item, price, "€"))
        return self.listbox_tovar

    def handle_selection(self):
        self.nakup_v_kosiku = [self.listbox_tovar.get(i) for i in self.listbox_tovar.curselection()]
        print("zvolene", self.nakup_v_kosiku)
        self.nak_vozik_premenna.set(value=self.nakup_v_kosiku)
        self.sum_buying_cart.set(sum([i[2] for i in self.nakup_v_kosiku]))
        return self.nakup_v_kosiku

    def next_window(self):
        self.destroy()


if __name__ == '__main__':
    ruzinov = DatabazaElektro()
    nakupny_zoznam_window = FirstWindow()
    nahrany_tovar = nakupny_zoznam_window.vloz_tov_do_listbox(ruzinov)
    nakupny_zoznam_window.mainloop()
    ruzinov.new_db.close()
    print("na konci potvrdene", nakupny_zoznam_window.nakup_v_kosiku)


# ruzinov = DatabazaElektro()
# nakupny_zoznam_window = FirstWindow()
# nahrany_tovar = nakupny_zoznam_window.vloz_tov_do_listbox(ruzinov)
# nakupny_zoznam_window.mainloop()
# ruzinov.new_db.close()
# print("na konci potvrdene", nakupny_zoznam_window.nakup_v_kosiku)
