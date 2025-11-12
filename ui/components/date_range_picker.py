# -*- coding: utf-8 -*-
"""
DateRangePicker - Entry com seleção de range de datas
"""
import customtkinter as ctk
from datetime import datetime, date
import calendar


class DateRangePicker(ctk.CTkFrame):
    """
    Entry com seleção de range de datas (de... a...)
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
        self.calendar_window = None

        # Entry para mostrar range
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            height=35
        )
        self.entry.pack(fill="x", expand=True)
        self.entry.bind("<Button-1>", lambda e: self.show_calendar())
        self.entry.bind("<FocusIn>", lambda e: self.show_calendar())

    def show_calendar(self):
        """Mostra janela de seleção de range"""
        if self.calendar_window and self.calendar_window.winfo_exists():
            return

        # Criar janela de calendário
        self.calendar_window = ctk.CTkToplevel(self)
        self.calendar_window.title("Selecionar Período")
        self.calendar_window.geometry("700x450")
        self.calendar_window.resizable(False, False)

        # Tornar modal
        self.calendar_window.transient(self.winfo_toplevel())
        self.calendar_window.grab_set()

        # Centrar na tela
        self.calendar_window.update_idletasks()
        x = (self.calendar_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.calendar_window.winfo_screenheight() // 2) - (450 // 2)
        self.calendar_window.geometry(f"700x450+{x}+{y}")

        # Container principal
        main_frame = ctk.CTkFrame(self.calendar_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Selecionar Período do Evento",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # Info label
        self.info_label = ctk.CTkLabel(
            main_frame,
            text="Clique na data de início e depois na data de fim",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.info_label.pack(pady=(0, 10))

        # Frame para dois calendários lado a lado
        calendars_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        calendars_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Estado temporário para seleção
        self.temp_start = self.start_date
        self.temp_end = self.end_date

        # Calendário 1 (mês atual)
        today = date.today()
        self.create_calendar_view(calendars_frame, today.year, today.month, side="left")

        # Calendário 2 (próximo mês)
        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year

        self.create_calendar_view(calendars_frame, next_year, next_month, side="right")

        # Botões
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))

        # Botão Limpar
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="Limpar",
            command=self.clear_range,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_btn.pack(side="left")

        # Botão Hoje
        today_btn = ctk.CTkButton(
            buttons_frame,
            text="Hoje",
            command=self.select_today,
            width=100,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        today_btn.pack(side="left", padx=(5, 0))

        # Botão Cancelar
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            command=self.calendar_window.destroy,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="right")

        # Botão Confirmar
        confirm_btn = ctk.CTkButton(
            buttons_frame,
            text="Confirmar",
            command=self.confirm_range,
            width=100,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        confirm_btn.pack(side="right", padx=(0, 5))

    def create_calendar_view(self, parent, year, month, side="left"):
        """Cria visualização de um mês"""
        # Container do calendário
        cal_container = ctk.CTkFrame(parent)
        cal_container.pack(side=side, fill="both", expand=True, padx=5)

        # Header com navegação
        header_frame = ctk.CTkFrame(cal_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        # Navegação anterior (só no calendário esquerdo)
        if side == "left":
            prev_btn = ctk.CTkButton(
                header_frame,
                text="◀",
                width=30,
                command=lambda: self.change_month(cal_container, year, month, -1, side)
            )
            prev_btn.pack(side="left")

        # Mês/Ano
        month_label = ctk.CTkLabel(
            header_frame,
            text=f"{calendar.month_name[month]} {year}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        month_label.pack(side="left", expand=True)

        # Navegação seguinte (só no calendário direito)
        if side == "right":
            next_btn = ctk.CTkButton(
                header_frame,
                text="▶",
                width=30,
                command=lambda: self.change_month(cal_container, year, month, 1, side)
            )
            next_btn.pack(side="right")

        # Grid de dias
        days_frame = ctk.CTkFrame(cal_container)
        days_frame.pack(fill="both", expand=True)

        # Headers dos dias da semana
        days_of_week = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for col, day in enumerate(days_of_week):
            label = ctk.CTkLabel(
                days_frame,
                text=day,
                font=ctk.CTkFont(size=10, weight="bold"),
                width=40,
                height=25
            )
            label.grid(row=0, column=col, padx=2, pady=2)

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
                    label.grid(row=row_idx + 1, column=col_idx, padx=2, pady=2)
                else:
                    # Dia válido
                    day_date = date(year, month, day)
                    is_today = day_date == today
                    is_selected = self._is_in_range(day_date)

                    # Cores
                    if is_selected:
                        fg_color = "#4CAF50"  # Verde para selecionado
                        hover_color = "#45a049"
                    elif is_today:
                        fg_color = "#2196F3"  # Azul para hoje
                        hover_color = "#1976D2"
                    else:
                        fg_color = "gray"
                        hover_color = "darkgray"

                    btn = ctk.CTkButton(
                        days_frame,
                        text=str(day),
                        width=40,
                        height=30,
                        fg_color=fg_color,
                        hover_color=hover_color,
                        command=lambda d=day_date: self.select_date(d)
                    )
                    btn.grid(row=row_idx + 1, column=col_idx, padx=2, pady=2)

    def _is_in_range(self, check_date):
        """Verifica se data está no range selecionado"""
        if not self.temp_start:
            return False
        if not self.temp_end:
            return check_date == self.temp_start
        return self.temp_start <= check_date <= self.temp_end

    def select_date(self, selected_date):
        """Seleciona uma data no range"""
        if not self.temp_start or (self.temp_start and self.temp_end):
            # Primeira seleção ou reset
            self.temp_start = selected_date
            self.temp_end = None
            self.info_label.configure(
                text=f"Início: {selected_date.strftime('%d/%m/%Y')} - Clique na data de fim"
            )
        else:
            # Segunda seleção
            if selected_date >= self.temp_start:
                self.temp_end = selected_date
                self.info_label.configure(
                    text=f"Período: {self.temp_start.strftime('%d/%m/%Y')} a {self.temp_end.strftime('%d/%m/%Y')}"
                )
            else:
                # Se clicar numa data anterior, inverte
                self.temp_end = self.temp_start
                self.temp_start = selected_date
                self.info_label.configure(
                    text=f"Período: {self.temp_start.strftime('%d/%m/%Y')} a {self.temp_end.strftime('%d/%m/%Y')}"
                )

        # Refresh calendários
        self.refresh_calendars()

    def refresh_calendars(self):
        """Atualiza visualização dos calendários"""
        if self.calendar_window and self.calendar_window.winfo_exists():
            # Destruir e recriar seria complexo, apenas fechamos e reabrimos
            # Para simplificar, não fazemos refresh automático
            pass

    def change_month(self, container, year, month, delta, side):
        """Muda mês do calendário"""
        month += delta
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1

        # Limpar container
        for widget in container.winfo_children():
            widget.destroy()

        # Recriar calendário
        self.create_calendar_view(container.master, year, month, side)

    def confirm_range(self):
        """Confirma seleção do range"""
        if self.temp_start:
            self.start_date = self.temp_start
            self.end_date = self.temp_end
            self._update_entry()
            self.calendar_window.destroy()

    def select_today(self):
        """Seleciona hoje"""
        today = date.today()
        self.start_date = today
        self.end_date = None
        self._update_entry()
        self.calendar_window.destroy()

    def clear_range(self):
        """Limpa seleção"""
        self.start_date = None
        self.end_date = None
        self.temp_start = None
        self.temp_end = None
        self._update_entry()
        self.info_label.configure(
            text="Clique na data de início e depois na data de fim"
        )
        self.refresh_calendars()

    def _update_entry(self):
        """Atualiza texto do entry"""
        self.entry.delete(0, "end")
        if self.start_date:
            if self.end_date and self.end_date != self.start_date:
                # Range
                text = f"{self.start_date.strftime('%d/%m/%Y')} - {self.end_date.strftime('%d/%m/%Y')}"
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
