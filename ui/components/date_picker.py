# -*- coding: utf-8 -*-
"""
DatePicker - Entry com calendário visual
"""
import customtkinter as ctk
from datetime import datetime, date
import calendar


class DatePickerEntry(ctk.CTkFrame):
    """
    Entry com calendário visual para seleção de data
    """

    def __init__(
        self,
        parent,
        default_date: date = None,
        placeholder: str = "Selecionar data...",
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.selected_date = default_date or date.today()
        self.calendar_window = None

        # Frame principal
        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(fill="x")

        # Entry para mostrar data
        self.entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text=placeholder,
            height=35
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry.bind("<Button-1>", lambda e: self.show_calendar())
        self.entry.bind("<FocusIn>", lambda e: self.show_calendar())

        # Botão calendário
        self.cal_button = ctk.CTkButton(
            entry_frame,
            text="📅",
            width=40,
            height=35,
            command=self.show_calendar,
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#36719F", "#144870")
        )
        self.cal_button.pack(side="right")

        # Preencher com data padrão
        if default_date:
            self.set_date(default_date)

    def show_calendar(self):
        """Mostra janela de calendário"""
        if self.calendar_window and self.calendar_window.winfo_exists():
            return

        # Criar janela de calendário
        self.calendar_window = ctk.CTkToplevel(self)
        self.calendar_window.title("Selecionar Data")
        self.calendar_window.geometry("320x380")
        self.calendar_window.resizable(False, False)

        # Tornar modal
        self.calendar_window.transient(self.winfo_toplevel())
        self.calendar_window.grab_set()

        # Centrar na tela
        self.calendar_window.update_idletasks()
        x = (self.calendar_window.winfo_screenwidth() // 2) - (320 // 2)
        y = (self.calendar_window.winfo_screenheight() // 2) - (380 // 2)
        self.calendar_window.geometry(f"320x380+{x}+{y}")

        # Data atual para navegação
        self.current_year = self.selected_date.year
        self.current_month = self.selected_date.month

        # Criar widgets do calendário
        self.create_calendar_widgets()

    def create_calendar_widgets(self):
        """Cria widgets do calendário"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.calendar_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header com navegação
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        # Botão mês anterior
        prev_btn = ctk.CTkButton(
            header_frame,
            text="◀",
            width=40,
            command=self.prev_month
        )
        prev_btn.pack(side="left")

        # Label mês/ano
        self.month_year_label = ctk.CTkLabel(
            header_frame,
            text=f"{calendar.month_name[self.current_month]} {self.current_year}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.month_year_label.pack(side="left", expand=True)

        # Botão próximo mês
        next_btn = ctk.CTkButton(
            header_frame,
            text="▶",
            width=40,
            command=self.next_month
        )
        next_btn.pack(side="left")

        # Frame do calendário
        self.calendar_frame = ctk.CTkFrame(main_frame)
        self.calendar_frame.pack(fill="both", expand=True)

        # Criar grid do calendário
        self.create_calendar_grid()

        # Botões inferiores
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        today_btn = ctk.CTkButton(
            button_frame,
            text="Hoje",
            command=self.select_today,
            width=80
        )
        today_btn.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(
            button_frame,
            text="Limpar",
            command=self.clear_date,
            width=80,
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.calendar_window.destroy,
            width=80,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="right", padx=5)

    def create_calendar_grid(self):
        """Cria grid de dias do mês"""
        # Limpar frame
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Headers dos dias da semana
        days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for col, day in enumerate(days):
            label = ctk.CTkLabel(
                self.calendar_frame,
                text=day,
                font=ctk.CTkFont(size=11, weight="bold"),
                width=40
            )
            label.grid(row=0, column=col, padx=2, pady=2)

        # Obter dias do mês
        cal = calendar.monthcalendar(self.current_year, self.current_month)

        # Criar botões para cada dia
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Dia vazio
                    label = ctk.CTkLabel(
                        self.calendar_frame,
                        text="",
                        width=40,
                        height=35
                    )
                    label.grid(row=week_num + 1, column=day_num, padx=2, pady=2)
                else:
                    # Verificar se é o dia selecionado
                    is_selected = (
                        self.selected_date.year == self.current_year and
                        self.selected_date.month == self.current_month and
                        self.selected_date.day == day
                    )

                    # Verificar se é hoje
                    today = date.today()
                    is_today = (
                        today.year == self.current_year and
                        today.month == self.current_month and
                        today.day == day
                    )

                    # Cor do botão
                    if is_selected:
                        fg_color = ("#4CAF50", "#2e7d32")
                    elif is_today:
                        fg_color = ("#2196F3", "#1976D2")
                    else:
                        fg_color = "transparent"

                    btn = ctk.CTkButton(
                        self.calendar_frame,
                        text=str(day),
                        width=40,
                        height=35,
                        fg_color=fg_color,
                        hover_color=("#e0e0e0", "#3a3a3a"),
                        command=lambda d=day: self.select_day(d)
                    )
                    btn.grid(row=week_num + 1, column=day_num, padx=2, pady=2)

    def prev_month(self):
        """Navega para mês anterior"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1

        self.month_year_label.configure(
            text=f"{calendar.month_name[self.current_month]} {self.current_year}"
        )
        self.create_calendar_grid()

    def next_month(self):
        """Navega para próximo mês"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

        self.month_year_label.configure(
            text=f"{calendar.month_name[self.current_month]} {self.current_year}"
        )
        self.create_calendar_grid()

    def select_day(self, day: int):
        """Seleciona um dia"""
        self.selected_date = date(self.current_year, self.current_month, day)
        self.entry.delete(0, "end")
        self.entry.insert(0, self.selected_date.strftime("%Y-%m-%d"))
        self.calendar_window.destroy()

    def select_today(self):
        """Seleciona hoje"""
        today = date.today()
        self.selected_date = today
        self.current_year = today.year
        self.current_month = today.month
        self.entry.delete(0, "end")
        self.entry.insert(0, today.strftime("%Y-%m-%d"))
        self.calendar_window.destroy()

    def clear_date(self):
        """Limpa data"""
        self.entry.delete(0, "end")
        self.selected_date = date.today()
        self.calendar_window.destroy()

    def get(self) -> str:
        """Retorna data no formato YYYY-MM-DD"""
        return self.entry.get()

    def get_date(self) -> date:
        """Retorna objeto date"""
        text = self.entry.get().strip()
        if not text:
            return None
        try:
            return datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            return None

    def set_date(self, value: date):
        """Define data"""
        if value:
            self.selected_date = value
            self.entry.delete(0, "end")
            self.entry.insert(0, value.strftime("%Y-%m-%d"))

    def clear(self):
        """Limpa entry"""
        self.entry.delete(0, "end")
        self.selected_date = date.today()
