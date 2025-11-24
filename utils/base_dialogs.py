# utils/base_dialogs.py

import customtkinter as ctk

class BaseDialogMedium(ctk.CTkToplevel):
    """
    Dialog base tipo Medium: altura máxima 450px, largura 500px.
    Scroll surge se overflow.
    Usage: herda esta classe e cria os widgets em self.main_frame.
    """
    def __init__(self, parent, title="Dialog", width=500, height=450):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.minsize(width, 320)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.main_frame = ctk.CTkScrollableFrame(self, width=width-40, height=height)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

class BaseDialogLarge(ctk.CTkToplevel):
    """
    Dialog base tipo Large: altura máxima 720px, largura 630px.
    Scroll surge se overflow.
    Usage: herda esta classe e cria os widgets em self.main_frame.
    """
    def __init__(self, parent, title="Dialog", width=630, height=720):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.minsize(width, 450)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.main_frame = ctk.CTkScrollableFrame(self, width=width-40, height=height)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
