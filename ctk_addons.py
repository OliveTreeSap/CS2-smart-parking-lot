from customtkinter import *
from PIL import Image

class IconEntry(CTkFrame):
    """A modified version of the entry widget to include an icon on the left of the entry box"""
    def __init__(self, *args, icon, placeholder_text="", **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(cursor="xterm")
        self.icon = CTkLabel(master=self, text="", image=icon, cursor="xterm")
        self.icon.pack(pady=(5, 5), padx=10, side="left")
        self.entry = CTkEntry(master=self, placeholder_text=placeholder_text, corner_radius=0, border_width=0, 
                                fg_color=super().cget("fg_color"), width=600, height=75,
                                font=CTkFont(size=24))
        self.entry.pack(expand=True, fill="x", padx=(0, 10), side="left")
        self.icon.bind("<Button-1>", lambda e: self.entry.focus_set())
        self.bind("<Button-1>", lambda e: self.entry.focus_set())

    def get(self):
        return self.entry.get()

    def insert(self, index, string):
        self.entry.insert(index, string)

    def delete(self, first_index, last_index):
        self.entry.delete(first_index, last_index)

    def configure(self, require_redraw=False, **kwargs):
        if "icon" in kwargs:
            icon_image = kwargs.pop("icon")
            self.icon.configure(image=icon_image)

        if "placeholder_text" in kwargs:
            self.entry.configure(placeholder_text=kwargs.pop("placeholder_text"))

        if "fg_color" in kwargs:
            self.entry.configure(fg_color=kwargs["fg_color"])

        super().configure(**kwargs, require_redraw=require_redraw)
