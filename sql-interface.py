import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import requests
import os
import csv
from dotenv import load_dotenv

load_dotenv()

class QueryInputFrame(tk.Frame):
    def __init__(self, root=None, tree_view_frame=None):
        super().__init__(root)
        self.tree_view_frame = tree_view_frame
        self.grid(column=0, row=0, padx=10, pady=10, sticky="NSEW")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.query_input = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.query_input.grid(column=0, row=0, sticky="NSEW")
        tk.Button(self, text="Post", command=self.post_query, width=20).grid(column=0, row=1, pady=10)  

    def post_query(self):
        sql_code = self.query_input.get("1.0", "end-1c")
        headers = {'Content-type': 'text/plain'}
        response = requests.post(os.environ.get("url"), data=sql_code, headers=headers, auth=(os.environ.get("usr"), os.environ.get("pw") ))
        response_data = response.json()['Results']
        self.tree_view_frame.set_data(response_data)  # Pass response_data to display_data
        self.tree_view_frame.display_data() # Display the data on button press

class TreeViewFrame(tk.Frame):
    def __init__(self, root=None):
        super().__init__(root)
        self.response_data = None
        self.grid(column=0, row=2, padx=10, pady=10, sticky="NSEW")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(self, columns=(), show="headings")
        self.tree.grid(column=0, row=0, sticky="NSEW")

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        yscroll.grid(column=1, row=0, sticky="ns")
        self.tree.configure(yscrollcommand=yscroll.set)

        xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        xscroll.grid(column=0, row=1, sticky="ew")
        self.tree.configure(xscrollcommand=xscroll.set)

        tk.Button(self, text="Download", command=self.download_data, width=20).grid(column=0, row=2, pady=10) 
    
    def set_data(self, response_data):
        self.response_data = response_data

    def display_data(self):
        print(self.response_data)
        for item in self.tree.get_children():
            self.tree.delete(item)

        keys = list(self.response_data[0].keys())
        self.tree["columns"] = keys
        for key in keys:
            self.tree.heading(key, text=key)
            self.tree.column(key, anchor="center")

        for row_data in self.response_data:
            values = [row_data[key] for key in keys]
            self.tree.insert("", "end", values=values)

    def download_data(self):
        with open("out.csv", "w", newline='') as my_csv:
            csvwriter = csv.writer(my_csv, delimiter=',')
            csvwriter.writerow(self.tree["columns"])
            for row_id in self.tree.get_children():
                row = self.tree.item(row_id)['values']
                csvwriter.writerow(row)

class MainApp:
    def __init__(self, root=None):
        self.root = root
        root.title("OTM Interface")
        width = root.winfo_screenwidth()//2
        height = root.winfo_screenheight()//2
        root.geometry(f'{width}x{height}')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)
        self.tree_view_frame = TreeViewFrame(root)
        self.query_frame = QueryInputFrame(root, self.tree_view_frame)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    app.run()

