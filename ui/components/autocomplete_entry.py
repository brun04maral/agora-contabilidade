# -*- coding: utf-8 -*-
"""
AutocompleteEntry - Entry com autocomplete/filtro em tempo real
"""
import customtkinter as ctk
from typing import List, Optional, Callable


class AutocompleteEntry(ctk.CTkFrame):
    """
    Entry com autocomplete dropdown
    Filtra lista de opções conforme o utilizador digita
    """

    def __init__(
        self,
        parent,
        options: List[str],
        on_select: Optional[Callable] = None,
        placeholder: str = "Começar a escrever...",
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.options = options
        self.filtered_options = options.copy()
        self.on_select_callback = on_select
        self.selected_value = None

        # Entry principal
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            height=35
        )
        self.entry.pack(fill="x")
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Down>", self._on_arrow_down)
        self.entry.bind("<Return>", self._on_return)

        # Dropdown frame (inicialmente oculto)
        self.dropdown_frame = None
        self.dropdown_visible = False
        self.suggestion_buttons = []
        self.selected_index = -1

    def _on_key_release(self, event):
        """Filtra opções quando utilizador digita"""
        if event.keysym in ["Down", "Up", "Return", "Escape"]:
            return

        text = self.entry.get().strip().lower()

        if not text:
            # Mostrar todas as opções
            self.filtered_options = self.options.copy()
        else:
            # Filtrar opções
            self.filtered_options = [
                opt for opt in self.options
                if text in opt.lower()
            ]

        self._update_dropdown()

    def _on_focus_in(self, event):
        """Mostrar dropdown quando ganha foco"""
        self._update_dropdown()

    def _on_focus_out(self, event):
        """Ocultar dropdown quando perde foco (com delay)"""
        # Delay para permitir clique no dropdown
        self.after(200, self._hide_dropdown)

    def _on_arrow_down(self, event):
        """Navegar para baixo no dropdown"""
        if self.dropdown_visible and self.filtered_options:
            self.selected_index = min(
                self.selected_index + 1,
                len(self.filtered_options) - 1
            )
            self._highlight_selected()

    def _on_return(self, event):
        """Selecionar item destacado ao pressionar Enter"""
        if self.dropdown_visible and 0 <= self.selected_index < len(self.filtered_options):
            self._select_option(self.filtered_options[self.selected_index])

    def _update_dropdown(self):
        """Atualiza ou cria dropdown com opções filtradas"""
        if not self.filtered_options:
            self._hide_dropdown()
            return

        # Criar dropdown se não existir
        if not self.dropdown_frame:
            self.dropdown_frame = ctk.CTkScrollableFrame(
                self,
                height=min(200, len(self.filtered_options) * 35),
                fg_color=("#ffffff", "#2b2b2b"),
                border_width=1,
                border_color=("gray", "gray")
            )

        # Limpar botões antigos
        for btn in self.suggestion_buttons:
            btn.destroy()
        self.suggestion_buttons.clear()
        self.selected_index = -1

        # Criar botões para opções filtradas
        for idx, option in enumerate(self.filtered_options[:10]):  # Máximo 10 sugestões
            btn = ctk.CTkButton(
                self.dropdown_frame,
                text=option,
                anchor="w",
                height=32,
                fg_color="transparent",
                hover_color=("#e0e0e0", "#3a3a3a"),
                text_color=("black", "white"),
                command=lambda opt=option: self._select_option(opt)
            )
            btn.pack(fill="x", pady=1, padx=2)
            self.suggestion_buttons.append(btn)

        # Mostrar dropdown
        if not self.dropdown_visible:
            self.dropdown_frame.pack(fill="x", pady=(2, 0))
            self.dropdown_visible = True

    def _hide_dropdown(self):
        """Oculta dropdown"""
        if self.dropdown_frame and self.dropdown_visible:
            self.dropdown_frame.pack_forget()
            self.dropdown_visible = False

    def _highlight_selected(self):
        """Destaca opção selecionada"""
        for idx, btn in enumerate(self.suggestion_buttons):
            if idx == self.selected_index:
                btn.configure(fg_color=("#4CAF50", "#2e7d32"))
            else:
                btn.configure(fg_color="transparent")

    def _select_option(self, option: str):
        """Seleciona uma opção"""
        self.selected_value = option
        self.entry.delete(0, "end")
        self.entry.insert(0, option)
        self._hide_dropdown()

        # Callback
        if self.on_select_callback:
            self.on_select_callback(option)

    def get(self) -> str:
        """Retorna valor atual do entry"""
        return self.entry.get()

    def set(self, value: str):
        """Define valor do entry"""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
        self.selected_value = value

    def clear(self):
        """Limpa entry"""
        self.entry.delete(0, "end")
        self.selected_value = None

    def update_options(self, new_options: List[str]):
        """Atualiza lista de opções"""
        self.options = new_options
        self.filtered_options = new_options.copy()
        if self.dropdown_visible:
            self._update_dropdown()
