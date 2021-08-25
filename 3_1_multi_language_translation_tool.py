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
        self.geometry('500x300')

        self.notebook = Notebook(self)

        # notebook has two frames
        english_tab = tk.Frame(self.notebook)
        croatian_tab = tk.Frame(self.notebook)

        # english frame has butt and text entry
        self.translate_button = tk.Button(english_tab, text='Translate', command=self.translate)
        self.translate_button.pack(side=tk.BOTTOM, fill=tk.X)

        self.english_entry = tk.Text(english_tab, bg='white', fg='black')
        self.english_entry.pack(side=tk.TOP, expand=1)


        self.croatian_copy_button = tk.Button(croatian_tab, text='Copy to clipboard', command=self.copy_to_clipboard)
        self.croatian_copy_button.pack(side=tk.BOTTOM, fill=tk.X)

        # StringVar used to update label containing croatian translation and to grab the text back to put into clipboard
        self.croatian_translation = tk.StringVar(croatian_tab)
        self.croatian_translation.set('')

        self.croatian_label = tk.Label(croatian_tab, textvar=self.croatian_translation, bg='lightgrey', fg='black')
        self.croatian_label.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.notebook.add(english_tab, text='English')
        self.notebook.add(croatian_tab, text='Croatian')

        self.notebook.pack(fill=tk.BOTH, expand=1)

    def translate(self, target_language='hr', text=None):
        if not text:
            text = self.english_entry.get(1.0, tk.END)

        url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl={}&tl={}&dt=t&q={}'\
            .format('en', target_language, text)

        try:
            r = requests.get(url)
            r.raise_for_status()
            translation = r.json()[0][0][0]
            self.croatian_translation.set(translation)
            msg.showinfo('Translation successful', 'Text successfully translated')
        except Exception as e:
            msg.showerror('Translation failed', str(e))

    def copy_to_clipboard(self, text=None):
        if not text:
            text = self.croatian_translation.get()

        self.clipboard_clear()
        self.clipboard_append(text)
        msg.showinfo('Copied successfully', 'Text copied to clipboard')


if __name__ == '__main__':
    translatebook = TranslateBook()
    translatebook.mainloop()

