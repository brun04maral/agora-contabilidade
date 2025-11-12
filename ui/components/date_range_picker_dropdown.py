# -*- coding: utf-8 -*-
"""
DateRangePickerDropdown - Entry com seleção de range inline
"""
import customtkinter as ctk
from datetime import datetime, date
import calendar


class DateRangePickerDropdown(ctk.CTkFrame):
    """
    Entry com seleção de range de datas em dropdown inline
    Clica na data início, depois na data fim - range fica destacado
    """

    def __init__(
        self,
        parent,
        placeholder: str = "Selecionar período...",
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.start_date = None
        self.end_date = None
        self.dropdown_frame = None
        self.is_dropdown_open = False
        self.temp_start = None
        self.temp_end = None

        # Entry para mostrar range
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            height=35
        )
        self.entry.pack(fill="x", expand=True)
        self.entry.bind("<Button-1>", self._toggle_dropdown)
        self.entry.bind("<FocusIn>", self._show_dropdown)

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

        # Reset temp selection
        self.temp_start = self.start_date
        self.temp_end = self.end_date

        # Criar dropdown frame
        self.dropdown_frame = ctk.CTkFrame(
            self.winfo_toplevel(),
            fg_color=("#f0f0f0", "#2b2b2b"),
            border_width=2,
            border_color=("gray70", "gray30")
        )

        # Posicionar dropdown abaixo do entry
        self.update_idletasks()
        x = self.entry.winfo_rootx() - self.winfo_toplevel().winfo_rootx()
        y = self.entry.winfo_rooty() - self.winfo_toplevel().winfo_rooty() + self.entry.winfo_height() + 2

        self.dropdown_frame.place(x=x, y=y, width=350, height=380)
        self.dropdown_frame.lift()

        # Data para mostrar
        display_date = self.start_date or date.today()

        # Criar interface
        self._create_interface(display_date.year, display_date.month)

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

        widget = event.widget

        # Check if click is in entry
        if widget == self.entry or self.entry in widget.winfo_children():
            return

        # Check if click is in dropdown
        try:
            if widget == self.dropdown_frame or widget.master == self.dropdown_frame:
                return
            parent = widget.master
            while parent:
                if parent == self.dropdown_frame:
                    return
                parent = parent.master if hasattr(parent, 'master') else None
        except:
            pass

        # Click foi fora, fechar dropdown
        self._hide_dropdown()

    def _create_interface(self, year, month):
        """Cria interface do dropdown"""
        if not self.dropdown_frame:
            return

        # Limpar dropdown
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()

        # Container
        container = ctk.CTkFrame(self.dropdown_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Info label
        self.info_label = ctk.CTkLabel(
            container,
            text=self._get_info_text(),
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.info_label.pack(pady=(0, 5))

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

        # Calendário
        self._create_calendar(container, year, month)

        # Botões
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))

        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="Limpar",
            command=self._clear_selection,
            width=80,
            height=30,
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_btn.pack(side="left")

        confirm_btn = ctk.CTkButton(
            buttons_frame,
            text="Confirmar",
            command=self._confirm_selection,
            width=80,
            height=30,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        confirm_btn.pack(side="right")

    def _create_calendar(self, parent, year, month):
        """Cria calendário"""
        # Grid de dias
        days_frame = ctk.CTkFrame(parent, fg_color="transparent")
        days_frame.pack(fill="both", expand=True)

        # Headers dos dias da semana
        days_of_week = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for col, day in enumerate(days_of_week):
            label = ctk.CTkLabel(
                days_frame,
                text=day,
                font=ctk.CTkFont(size=9, weight="bold"),
                width=45,
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
                        width=45,
                        height=32
                    )
                    label.grid(row=row_idx + 1, column=col_idx, padx=1, pady=1)
                else:
                    # Dia válido
                    day_date = date(year, month, day)
                    is_today = day_date == today
                    in_range = self._is_in_range(day_date)
                    is_start = day_date == self.temp_start
                    is_end = day_date == self.temp_end

                    # Cores baseadas no estado
                    if is_start or is_end:
                        fg_color = "#4CAF50"  # Verde para início/fim
                        hover_color = "#45a049"
                        text_color = "white"
                    elif in_range:
                        fg_color = ("#c8e6c9", "#2d5a2f")  # Verde claro para range
                        hover_color = ("#a5d6a7", "#1b3d1f")
                        text_color = ("black", "white")
                    elif is_today:
                        fg_color = "#2196F3"  # Azul para hoje
                        hover_color = "#1976D2"
                        text_color = "white"
                    else:
                        fg_color = "gray"
                        hover_color = "darkgray"
                        text_color = ("black", "white")

                    btn = ctk.CTkButton(
                        days_frame,
                        text=str(day),
                        width=45,
                        height=32,
                        font=ctk.CTkFont(size=11),
                        fg_color=fg_color,
                        hover_color=hover_color,
                        text_color=text_color,
                        command=lambda d=day_date: self._select_date(d)
                    )
                    btn.grid(row=row_idx + 1, column=col_idx, padx=1, pady=1)

    def _is_in_range(self, check_date):
        """Verifica se data está no range selecionado"""
        if not self.temp_start:
            return False
        if not self.temp_end:
            return check_date == self.temp_start

        # Range entre start e end
        return self.temp_start <= check_date <= self.temp_end

    def _select_date(self, selected_date):
        """Seleciona data no range"""
        if not self.temp_start or (self.temp_start and self.temp_end):
            # Primeira seleção ou reset
            self.temp_start = selected_date
            self.temp_end = None
        else:
            # Segunda seleção
            if selected_date >= self.temp_start:
                self.temp_end = selected_date
            else:
                # Se clicar numa data anterior, inverte
                self.temp_end = self.temp_start
                self.temp_start = selected_date

        # Refresh calendário
        display_date = self.temp_start or date.today()
        self._create_interface(display_date.year, display_date.month)

    def _change_month(self, year, month, delta):
        """Muda mês do calendário"""
        month += delta
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1

        self._create_interface(year, month)

    def _get_info_text(self):
        """Retorna texto informativo baseado no estado"""
        if not self.temp_start:
            return "Clique na data de início"
        elif not self.temp_end:
            return f"Início: {self.temp_start.strftime('%d/%m/%Y')} - Clique na data de fim"
        else:
            return f"Período: {self.temp_start.strftime('%d/%m/%Y')} a {self.temp_end.strftime('%d/%m/%Y')}"

    def _confirm_selection(self):
        """Confirma seleção"""
        if self.temp_start:
            self.start_date = self.temp_start
            self.end_date = self.temp_end
            self._update_entry()
        self._hide_dropdown()

    def _clear_selection(self):
        """Limpa seleção"""
        self.temp_start = None
        self.temp_end = None
        display_date = date.today()
        self._create_interface(display_date.year, display_date.month)

    def _update_entry(self):
        """Atualiza texto do entry"""
        self.entry.delete(0, "end")
        if self.start_date:
            if self.end_date and self.end_date != self.start_date:
                # Range
                text = f"{self.start_date.strftime('%d/%m/%Y')} | {self.end_date.strftime('%d/%m/%Y')}"
            else:
                # Data única
                text = self.start_date.strftime('%d/%m/%Y')
            self.entry.insert(0, text)

    def get(self):
        """Retorna texto do entry"""
        return self.entry.get()

    def set_range(self, start_date, end_date=None):
        """Define range de datas"""
        self.start_date = start_date
        self.end_date = end_date
        self._update_entry()

    def clear(self):
        """Limpa entry"""
        self.start_date = None
        self.end_date = None
        self.entry.delete(0, "end")
