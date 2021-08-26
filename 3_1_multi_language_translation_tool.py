"""
Creating a tabbed interface
Creating a menu
Creating a pop-up window
Accessing the clipboard
Calling APIs with requests
"""

import tkinter as tk
from tkinter import messagebox as msg
from tkinter.ttk import Notebook

import requests


class TranslateBook(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Translation Book')
        self.geometry('768x480')

        self.notebook = Notebook(self)

        # notebook has two frames
        english_tab = tk.Frame(self.notebook)
        croatian_tab = tk.Frame(self.notebook)

        # menu setup
        self.menu = tk.Menu(self, bg='lightgrey', fg='black')
        # tearoff disables drag-and-drop the submenu
        self.languages_menu = tk.Menu(self.menu, tearoff=0, bg='lightgrey', fg='black')
        self.languages_menu.add_command(label='Add new', command=self.show_new_language_popup)
        self.languages_menu.add_command(label='Portuguese',
                                        command=lambda: self.add_new_tab(LanguageTab(self, 'Portuguese', 'pt')))
        # placing submenu into a main bar
        self.menu.add_cascade(label='Languages', menu=self.languages_menu)

        # calling self.configure to set the root window's menu to overall menu
        self.config(menu=self.menu)

        self.notebook = Notebook(self)

        self.language_tabs = []

        english_tab = tk.Frame(self.notebook)

        self.translate_button = tk.Button(english_tab, text='Translate', command=self.translate)
        self.translate_button.pack(side=tk.BOTTOM, fill=tk.X)

        self.english_entry = tk.Text(english_tab, bg='white', fg='black')
        self.english_entry.pack(side=tk.TOP, expand=1)

        self.notebook.add(english_tab, text='English')
        self.notebook.pack(fill=tk.BOTH, expand=1)

    def translate(self, text=None):
        if len(self.language_tabs) < 1:
            msg.showerror('No languages', 'No languages added. Please add some from the menu')
            return

        if not text:
            text = self.english_entry.get(1.0, tk.END).strip()

        url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl={}&tl={}&dt=t&q={}'

        try:
            # using zip to combine our lists of language codes and StringVar elements into the correct pairs
            for language in self.language_tabs:
                full_url = url.format('en', language.lang_code, text)
                r = requests.get(full_url)
                r.raise_for_status()
                translation = r.json()[0][0][0]
                language.translation_var.set(translation)
        except Exception as e:
            msg.showerror('Translation failed', str(e))
        # else runs only if there's no exception
        else:
            msg.showinfo('Translation successful', 'Text successfully translated')

    def add_new_tab(self, tab):
        self.language_tabs.append(tab)
        self.notebook.add(tab, text=tab.lang_name)

        try:
            self.languages_menu.entryconfig(tab.lang_name, state='disabled')
        except:
            # language isn't in the menu
            pass

    def show_new_language_popup(self):
        NewLanguageForm(self)


class LanguageTab(tk.Frame):
    def __init__(self, master, lang_name, lang_code):
        super().__init__(master)

        self.lang_name = lang_name
        self.lang_code = lang_code

        self.translation_var = tk.StringVar(self)
        self.translation_var.set('')

        self.translated_label = tk.Label(self, textvar=self.translation_var, bg='lightgrey', fg='black')

        self.copy_button = tk.Button(self, text='Copy to clipboard', command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.BOTTOM, fill=tk.X)
        self.translated_label.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def copy_to_clipboard(self):
        # copy to clipboard needs access to root window
        root = self.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(self.translated_var.get())
        msg.showinfo('Copied successfully', 'Text copied to clipboard')


class NewLanguageForm(tk.Toplevel):
    def __init__(self, master):
        super().__init__()

        self.master = master

        self.title('Add new language')
        self.geometry('300x150')

        self.name_label = tk.Label(self, text='Language name')
        self.name_entry = tk.Entry(self, bg='white', fg='black')
        self.code_label = tk.Label(self, text='Language code')
        self.code_entry = tk.Entry(self, bg='white', fg='black')
        self.submit_button = tk.Button(self, text='Submit', command=self.submit)

        self.name_label.pack(fill=tk.BOTH, expand=1)
        self.name_entry.pack(fill=tk.BOTH, expand=1)
        self.code_label.pack(fill=tk.BOTH, expand=1)
        self.code_entry.pack(fill=tk.BOTH, expand=1)
        self.submit_button.pack(fill=tk.X)

    def submit(self):
        lang_name = self.name_entry.get()
        lang_code = self.code_entry.get()

        if lang_name and lang_code:
            new_tab = LanguageTab(self.master, lang_name, lang_code)
            self.master.languages_menu.add_command(label=lang_name, command=lambda: self.master.add_new_tab(new_tab))
            msg.showinfo('Language option added', 'Language option ' + lang_name + ' added to menu')
            self.destroy()
        else:
            msg.showerror('Missing information', 'Please add both a name and code')


if __name__ == '__main__':
    translatebook = TranslateBook()
    translatebook.mainloop()

"""
- Further development
- Import ttk and adjust the app to use ttk’s widgets
- Bind the relevant Button functionality to the Return key.
- Before adding a new language validate that the short code added exists for the google translate api.
- Remember the app’s previous state with sqlite (i.e. which tabs were added and which languages
were available in the menu).
- Add a "Remove a Language" Menu which lists the enabled languages and lets the user remove one.
"""