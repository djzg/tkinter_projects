'''
Allowing the user to enter text
Binding functions to keypresses
Dynamically generating widgets
Scrolling an area
Storing data (with sqlite)
'''

import tkinter as tk
import tkinter.messagebox as msg
import os
import sqlite3

class Todo(tk.Tk):
    # init with an empty list of tasks
    # make a default argument to None as unexpected behavior can occur if you try to pass an empty list in
    def __init__(self, tasks=None):
        super().__init__()

        if not tasks:
            self.tasks = []
        else:
            self.tasks = tasks

        # creating canvas widget for scrolling capabilities
        self.tasks_canvas = tk.Canvas(self)

        # creating two frames for tasks and text
        self.tasks_frame = tk.Frame(self.tasks_canvas)
        self.text_frame = tk.Frame(self)

        # creating vertical scrollbar using canvas
        # command it to scroll in y-direction
        self.scrollbar = tk.Scrollbar(self.tasks_canvas, orient='vertical', command=self.tasks_canvas.yview)

        # configuring canvas to accept scrollbar values
        self.tasks_canvas.configure(yscrollcommand=self.scrollbar.set)

        # set title and window size
        self.title('To-Do App v2')
        self.geometry('300x400')

        # creating text box and parent it to text_frame that will go on bottom
        self.task_create = tk.Text(self.text_frame, height=3, bg='white', fg='black')

        # packing task canvas to top and fill all available space
        self.tasks_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # packing scrollbar to the right in y-direction
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # using tasks_canvas to create a window inside tasks_frame, anchor it to the north
        self.canvas_frame = self.tasks_canvas.create_window((0, 0), window=self.tasks_frame, anchor='n')

        # packing to bottom, in x-direction and setting a cursor focus
        self.task_create.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.task_create.focus_set()

        # default task added to fill the space
        todo1 = tk.Label(self, text='--- Add items here ---', bg='lightgrey', fg='black', pady=10)
        todo1.bind("<Button-1>", self.remove_task)

        self.tasks.append(todo1)

        # packed to the TOP of the window and filled in x-direction (horizontally)
        for task in self.tasks:
            task.pack(side=tk.TOP, fill=tk.X)

        # binding keys
        # No invoking the function, we only pass the function itself
        # Configure event is fired when widgets change size and will provide new width and height
        self.bind("<Return>", self.add_task)
        self.bind("<Configure>", self.on_frame_configure)
        # scroll binding keys
        self.bind_all("<MouseWheel>", self.mouse_scroll)
        self.bind_all("<Button-4>", self.mouse_scroll)
        self.bind_all("<Button-5>", self.mouse_scroll)
        self.tasks_canvas.bind("<Configure>", self.task_width)

        # setting up color schemes
        self.colour_schemes = [{'bg': 'lightgrey', 'fg': 'black'}, {'bg': 'grey', 'fg': 'white'}]

        # loads tasks from database
        current_tasks = self.load_tasks()
        for task in current_tasks:
            task_text = task[0]
            self.add_task(None, task_text, True)

    def add_task(self, event=None, task_text=None, from_db=False):
        # grab text from task_create and start at first character looking till the end of the box
        # stripping newline characters as well as any trailing space characters
        if not task_text:
            task_text = self.task_create.get(1.0, tk.END).strip()

        # to avoid adding blank items, check if it's greater than 0
        if len(task_text) > 0:
            # creating a new label with the text entered by the user
            new_task = tk.Label(self.tasks_frame, text=task_text, pady=10)

            self.set_task_colour(len(self.tasks), new_task)

            new_task.bind("<Button-1>", self.remove_task)
            new_task.pack(side=tk.TOP, fill=tk.X)
            # counting number of tasks
            self.tasks.append(new_task)

            # packing new task at top in x-direction
            new_task.pack(side=tk.TOP, fill=tk.X)

            if not from_db:
                self.save_task(task_text)

        # clearing task_create text box
        self.task_create.delete(1.0, tk.END)

    # handling task removing that was accessed by Button-1 (left click)
    def remove_task(self, event):
        task = event.widget
        # confirmation message before task delete
        if msg.askyesno('Really delete?', 'Delete ' + task.cget('text') + '?'):
            self.tasks.remove(event.widget)
            delete_task_query = 'DELETE FROM tasks WHERE task=?'
            delete_task_data = (task.cget('text'), )
            self.runQuery(delete_task_query, delete_task_data)
            event.widget.destroy()
            self.recolour_tasks()

    # saving data into database
    def save_task(self, task):
        insert_task_query = 'INSERT INTO tasks VALUES (?)'
        insert_task_data = (task, )
        self.runQuery(insert_task_query, insert_task_data)

    # loading from database when program starts, gets called in __init__ method
    def load_tasks(self):
        load_tasks_query = 'SELECT task FROM tasks'
        my_tasks = self.runQuery(load_tasks_query, receive=True)
        return my_tasks

    # static method so that it can be called by firstTimeDB method that needs to be called before __init__
    @staticmethod
    def runQuery(sql, data=None, receive=False):
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        if data:
            cursor.execute(sql, data)
        else:
            cursor.execute(sql)

        if receive:
            return cursor.fetchall()
        else:
            conn.commit()

        conn.close()

    @staticmethod
    def firstTimeDB():
        create_tables = 'CREATE TABLE tasks (task TEXT)'
        Todo.runQuery(create_tables)

        default_task_query = 'INSERT INTO tasks VALUES (?)'
        default_task_data = ('--- Add items here ---', )
        Todo.runQuery(default_task_query, default_task_data)

    def recolour_tasks(self):
        for index, task in enumerate(self.tasks):
            self.set_task_colour(index, task)

    def set_task_colour(self, position, task):
        # determining whether we are on odd or even number of total task using divmod function
        _, task_style_choice = divmod(position, 2)

        # divmod remainder is used as index to determine the color scheme
        my_scheme_choice = self.colour_schemes[task_style_choice]

        # adding alternating color schemes to new task
        task.configure(bg=my_scheme_choice['bg'])
        task.configure(fg=my_scheme_choice['fg'])

    # method will be called whenever the window is resized
    def on_frame_configure(self, event=None):
        # uses bounding box to specify that we want the entire canvas to be scrollable
        self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox('all'))

    # task width method is responsible for ensuring the task labels stay at the full width of the canvase
    def task_width(self, event):
        canvas_width = event.width
        self.tasks_canvas.itemconfig(self.canvas_frame, width=canvas_width)

    # binding scrolling to the mouse wheel
    def mouse_scroll(self, event):
        if event.delta:
            # calling yview_scroll based on delta received (between 120 and -120) and dividing to get precise scrolling
            self.tasks_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        else:
            if event.num == 5:
                move = 1
            else:
                move = -1

            self.tasks_canvas.yview_scroll(move, 'units')


if __name__ == '__main__':
    if not os.path.isfile('tasks.db'):
        Todo.firstTimeDB()
    todo = Todo()
    todo.mainloop()


####### FURTHER DEVELOPMENT
# Prevent duplicate tasks by using a database look-up before adding a new task.
# •Give each task a "Delete" button instead of the on-click event on the Label itself (Buttons will be
# covered next chapter).
# •Instead of destroying tasks, mark them as "finished" using a column in the database and display them
# as "greyed out".
# Add a "category" for each task and colour the task based on the category instead of using the pattern
# (maybe separate them with a border).
#######