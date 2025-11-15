# -*- coding: utf-8 -*-
"""
DatePickerDropdown - Entry com calendário dropdown inline
"""
import customtkinter as ctk
from datetime import datetime, date
import calendar


class DatePickerDropdown(ctk.CTkFrame):
    """
    Entry com calendário dropdown inline (não abre janela modal)
    """

    def __init__(
        self,
        parent,
        default_date: date = None,
        placeholder: str = "Selecionar data...",
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.selected_date = default_date if default_date is not None else None
        self.dropdown_frame = None
        self.is_dropdown_open = False

        # Entry para mostrar data
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            height=35
        )
        self.entry.pack(fill="x", expand=True)
        self.entry.bind("<Button-1>", self._toggle_dropdown)
        self.entry.bind("<FocusIn>", self._show_dropdown)

        # Preencher com data padrão
        if default_date:
            self.set_date(default_date)

    def _toggle_dropdown(self, event=None):
        """Toggle dropdown visibility"""
        if self.is_dropdown_open:
            self._hide_dropdown()
        else:
            self._show_dropdown()

    def _show_dropdown(self, event=None):
        """Mostra dropdown com calendário"""
        if self.is_dropdown_open:
            return

        # Criar dropdown frame
        self.dropdown_frame = ctk.CTkFrame(
            self.winfo_toplevel(),
            width=320,
            height=300,
            fg_color=("#f0f0f0", "#2b2b2b"),
            border_width=2,
            border_color=("gray70", "gray30")
        )

        # Posicionar dropdown abaixo do entry
        self.update_idletasks()
        x = self.entry.winfo_rootx() - self.winfo_toplevel().winfo_rootx()
        y = self.entry.winfo_rooty() - self.winfo_toplevel().winfo_rooty() + self.entry.winfo_height() + 2

        # No CustomTkinter, width/height devem estar no construtor, não no place()
        self.dropdown_frame.place(x=x, y=y)
        self.dropdown_frame.lift()

        # Criar calendário (usar data selecionada ou hoje como referência)
        ref_date = self.selected_date if self.selected_date else date.today()
        self._create_calendar(ref_date.year, ref_date.month)

        self.is_dropdown_open = True

        # Bind click fora para fechar
        self.winfo_toplevel().bind("<Button-1>", self._check_click_outside, add="+")

    def _hide_dropdown(self, event=None):
        """Esconde dropdown"""
        if self.dropdown_frame:
            self.dropdown_frame.destroy()
            self.dropdown_frame = None
        self.is_dropdown_open = False

        # Unbind click outside
        try:
            self.winfo_toplevel().unbind("<Button-1>")
        except:
            pass

    def _check_click_outside(self, event):
        """Verifica se clique foi fora do dropdown"""
        if not self.dropdown_frame:
            return

        # Verificar se clique foi dentro do dropdown ou entry
        widget = event.widget

        # Se widget for string (path), ignorar
        if isinstance(widget, str):
            return

        # Check if click is in entry
        try:
            if widget == self.entry:
                return
            if hasattr(widget, 'winfo_children') and self.entry in widget.winfo_children():
                return
        except:
            pass

        # Check if click is in dropdown
        try:
            if widget == self.dropdown_frame or widget.master == self.dropdown_frame:
                return
            # Check parents
            parent = widget.master
            while parent:
                if parent == self.dropdown_frame:
                    return
                parent = parent.master if hasattr(parent, 'master') else None
        except:
            pass

        # Click foi fora, fechar dropdown
        self._hide_dropdown()

    def _create_calendar(self, year, month):
        """Cria calendário no dropdown"""
        if not self.dropdown_frame:
            return

        # Limpar dropdown
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()

        # Container
        container = ctk.CTkFrame(self.dropdown_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header com navegação
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        prev_btn = ctk.CTkButton(
            header_frame,
            text="◀",
            width=30,
            height=30,
            command=lambda: self._change_month(year, month, -1),
            fg_color="gray",
            hover_color="darkgray"
        )
        prev_btn.pack(side="left")

        month_label = ctk.CTkLabel(
            header_frame,
            text=f"{calendar.month_name[month]} {year}",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        month_label.pack(side="left", expand=True)

        next_btn = ctk.CTkButton(
            header_frame,
            text="▶",
            width=30,
            height=30,
            command=lambda: self._change_month(year, month, 1),
            fg_color="gray",
            hover_color="darkgray"
        )
        next_btn.pack(side="right")

        # Grid de dias
        days_frame = ctk.CTkFrame(container, fg_color="transparent")
        days_frame.pack(fill="both", expand=True)

        # Headers dos dias da semana
        days_of_week = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for col, day in enumerate(days_of_week):
            label = ctk.CTkLabel(
                days_frame,
                text=day,
                font=ctk.CTkFont(size=9, weight="bold"),
                width=40,
                height=20
            )
            label.grid(row=0, column=col, padx=1, pady=1)

        # Dias do mês
        cal = calendar.monthcalendar(year, month)
        today = date.today()

        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    # Dia vazio
                    label = ctk.CTkLabel(
                        days_frame,
                        text="",
                        width=40,
                        height=30
                    )
                    label.grid(row=row_idx + 1, column=col_idx, padx=1, pady=1)
                else:
                    # Dia válido
                    day_date = date(year, month, day)
                    is_today = day_date == today
                    is_selected = day_date == self.selected_date

                    # Cores
                    if is_selected:
                        fg_color = "#4CAF50"
                        hover_color = "#45a049"
                    elif is_today:
                        fg_color = "#2196F3"
                        hover_color = "#1976D2"
                    else:
                        fg_color = "gray"
                        hover_color = "darkgray"

                    btn = ctk.CTkButton(
                        days_frame,
                        text=str(day),
                        width=40,
                        height=30,
                        font=ctk.CTkFont(size=11),
                        fg_color=fg_color,
                        hover_color=hover_color,
                        command=lambda d=day_date: self._select_date(d)
                    )
                    btn.grid(row=row_idx + 1, column=col_idx, padx=1, pady=1)

    def _change_month(self, year, month, delta):
        """Muda mês do calendário"""
        month += delta
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1

        self._create_calendar(year, month)

    def _select_date(self, selected_date):
        """Seleciona data"""
        self.selected_date = selected_date
        self._update_entry()
        self._hide_dropdown()

    def _update_entry(self):
        """Atualiza texto do entry"""
        self.entry.delete(0, "end")
        if self.selected_date:
            self.entry.insert(0, self.selected_date.strftime('%d/%m/%Y'))

    def get(self):
        """Retorna texto do entry"""
        return self.entry.get()

    def get_date(self):
        """Retorna data selecionada"""
        return self.selected_date

    def set_date(self, new_date):
        """Define data e atualiza visualmente"""
        self.selected_date = new_date
        self._update_entry()
        # Forçar atualização visual imediata
        self.entry.update_idletasks()

    def clear(self):
        """Limpa entry"""
        self.selected_date = None
        self.entry.delete(0, "end")
