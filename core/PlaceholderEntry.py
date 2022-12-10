from tkinter import ttk


class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        style = ttk.Style(self)
        style.configure("Placeholder.TEntry", foreground="#d5d5d5")
        style.configure("Normal.TEntry", foreground="#000")

        self.placeholder = placeholder

        self.field_style = kwargs.pop("style", "Normal.TEntry")
        self.placeholder_style = kwargs.pop("placeholder_style", "Placeholder.TEntry")
        self["style"] = self.placeholder_style

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self.get() != self.placeholder:
            return
        if self["style"] == self.placeholder_style:
            self.delete("0", "end")
            self["style"] = self.field_style

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            self["style"] = self.placeholder_style