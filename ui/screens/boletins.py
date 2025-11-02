# -*- coding: utf-8 -*-
"""
Tela de gestão de Boletins
"""
import customtkinter as ctk
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
import tkinter.messagebox as messagebox

from logic.boletins import BoletinsManager
from database.models import Socio, EstadoBoletim
from ui.components.data_table import DataTable


class BoletinsScreen(ctk.CTkFrame):
    """
    Tela de gestão de Boletins (listar + emitir + marcar pago)
    """

    def __init__(self, parent, db_session: Session, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = BoletinsManager(db_session)

        self.configure(fg_color="transparent")
        self.create_widgets()
        self.carregar_boletins()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📄 Boletins",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(side="left")

        # Buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Atualizar",
            command=self.carregar_boletins,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=5)

        emitir_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Emitir Boletim",
            command=self.abrir_formulario,
            width=150,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#FF9800", "#F57C00"),
            hover_color=("#FFB74D", "#E65100")
        )
        emitir_btn.pack(side="left", padx=5)

        # Filters
        filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        filters_frame.pack(fill="x", padx=30, pady=(0, 20))

        # Sócio filter
        ctk.CTkLabel(
            filters_frame,
            text="Sócio:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.socio_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "Bruno", "Rafael"],
            command=self.aplicar_filtros,
            width=150
        )
        self.socio_filter.pack(side="left", padx=(0, 20))

        # Estado filter
        ctk.CTkLabel(
            filters_frame,
            text="Estado:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.estado_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "Pendente", "Pago"],
            command=self.aplicar_filtros,
            width=120
        )
        self.estado_filter.pack(side="left")

        # Table
        columns = [
            {'key': 'numero', 'label': 'Nº', 'width': 80},
            {'key': 'socio', 'label': 'Sócio', 'width': 120},
            {'key': 'data_emissao', 'label': 'Data Emissão', 'width': 110},
            {'key': 'valor', 'label': 'Valor', 'width': 100,
             'formatter': lambda v: f"€{v:,.2f}" if v else "€0,00"},
            {'key': 'descricao', 'label': 'Descrição', 'width': 280},
            {'key': 'estado', 'label': 'Estado', 'width': 100},
            {'key': 'data_pagamento', 'label': 'Data Pagamento', 'width': 130},
        ]

        # Custom table with special actions
        self.table_frame = ctk.CTkScrollableFrame(self, height=400)
        self.table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        self.create_custom_table(columns)

    def create_custom_table(self, columns):
        """Create custom table with conditional actions"""
        self.columns = columns
        self.boletins_data = []

        # Header
        header_frame = ctk.CTkFrame(self.table_frame, fg_color=("#E0E0E0", "#2a2a2a"))
        header_frame.pack(fill="x", padx=5, pady=(5, 0))

        col_index = 0
        for col in columns:
            label = ctk.CTkLabel(
                header_frame,
                text=col['label'],
                font=ctk.CTkFont(size=12, weight="bold"),
                width=col.get('width', 100),
                anchor="w"
            )
            label.grid(row=0, column=col_index, padx=10, pady=10, sticky="w")
            col_index += 1

        # Actions
        label = ctk.CTkLabel(
            header_frame,
            text="Ações",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=200,
            anchor="center"
        )
        label.grid(row=0, column=col_index, padx=10, pady=10)

    def carregar_boletins(self):
        """Load and display boletins"""
        boletins = self.manager.listar_todos()
        self.display_boletins(boletins)

    def display_boletins(self, boletins):
        """Display boletins in table"""
        # Clear existing rows (except header)
        for widget in self.table_frame.winfo_children()[1:]:
            widget.destroy()

        # Add rows
        for boletim in boletins:
            self.add_boletim_row(boletim)

    def add_boletim_row(self, boletim):
        """Add a boletim row with conditional actions"""
        row_frame = ctk.CTkFrame(
            self.table_frame,
            fg_color=("white", "#1e1e1e"),
            corner_radius=5
        )
        row_frame.pack(fill="x", padx=5, pady=2)

        data = self.boletim_to_dict(boletim)

        col_index = 0
        for col in self.columns:
            value = data.get(col['key'], '')

            if 'formatter' in col:
                value = col['formatter'](value)

            label = ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=ctk.CTkFont(size=12),
                width=col.get('width', 100),
                anchor="w"
            )
            label.grid(row=0, column=col_index, padx=10, pady=10, sticky="w")
            col_index += 1

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=col_index, padx=10, pady=5)

        # Marcar como Pago (só se PENDENTE)
        if boletim.estado == EstadoBoletim.PENDENTE:
            pagar_btn = ctk.CTkButton(
                actions_frame,
                text="✅ Pagar",
                command=lambda: self.marcar_como_pago(boletim.id),
                width=80,
                height=30,
                font=ctk.CTkFont(size=12),
                fg_color=("#4CAF50", "#388E3C"),
                hover_color=("#66BB6A", "#2E7D32")
            )
            pagar_btn.pack(side="left", padx=2)
        else:
            # Já pago - botão para desfazer
            despagar_btn = ctk.CTkButton(
                actions_frame,
                text="↩️ Pendente",
                command=lambda: self.marcar_como_pendente(boletim.id),
                width=80,
                height=30,
                font=ctk.CTkFont(size=12),
                fg_color=("#FF9800", "#F57C00"),
                hover_color=("#FFB74D", "#E65100")
            )
            despagar_btn.pack(side="left", padx=2)

        # Edit
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            command=lambda: self.editar_boletim(boletim),
            width=40,
            height=30,
            font=ctk.CTkFont(size=14)
        )
        edit_btn.pack(side="left", padx=2)

        # Delete
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            command=lambda: self.apagar_boletim(boletim),
            width=40,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color=("#F44336", "#C62828"),
            hover_color=("#E53935", "#B71C1C")
        )
        delete_btn.pack(side="left", padx=2)

    def boletim_to_dict(self, boletim) -> dict:
        """Convert boletim to dict"""
        return {
            'numero': boletim.numero,
            'socio': "Bruno" if boletim.socio == Socio.BRUNO else "Rafael",
            'data_emissao': boletim.data_emissao.strftime("%Y-%m-%d") if boletim.data_emissao else '-',
            'valor': float(boletim.valor),
            'descricao': boletim.descricao[:50] + '...' if boletim.descricao and len(boletim.descricao) > 50 else (boletim.descricao or '-'),
            'estado': "Pendente" if boletim.estado == EstadoBoletim.PENDENTE else "Pago",
            'data_pagamento': boletim.data_pagamento.strftime("%Y-%m-%d") if boletim.data_pagamento else '-',
        }

    def aplicar_filtros(self, *args):
        """Apply filters"""
        socio = self.socio_filter.get()
        estado = self.estado_filter.get()

        boletins = self.manager.listar_todos()

        # Filter by socio
        if socio != "Todos":
            socio_enum = Socio.BRUNO if socio == "Bruno" else Socio.RAFAEL
            boletins = [b for b in boletins if b.socio == socio_enum]

        # Filter by estado
        if estado != "Todos":
            estado_enum = EstadoBoletim.PENDENTE if estado == "Pendente" else EstadoBoletim.PAGO
            boletins = [b for b in boletins if b.estado == estado_enum]

        self.display_boletins(boletins)

    def abrir_formulario(self, boletim=None):
        """Open form dialog"""
        FormularioBoletimDialog(self, self.manager, boletim, self.carregar_boletins)

    def editar_boletim(self, boletim):
        """Edit boletim"""
        self.abrir_formulario(boletim)

    def marcar_como_pago(self, boletim_id: int):
        """Marcar boletim como pago"""
        sucesso, erro = self.manager.marcar_como_pago(boletim_id)
        if sucesso:
            messagebox.showinfo("Sucesso", "Boletim marcado como pago!")
            self.carregar_boletins()
        else:
            messagebox.showerror("Erro", f"Erro: {erro}")

    def marcar_como_pendente(self, boletim_id: int):
        """Marcar boletim como pendente"""
        sucesso, erro = self.manager.marcar_como_pendente(boletim_id)
        if sucesso:
            messagebox.showinfo("Sucesso", "Boletim marcado como pendente!")
            self.carregar_boletins()
        else:
            messagebox.showerror("Erro", f"Erro: {erro}")

    def apagar_boletim(self, boletim):
        """Delete boletim"""
        resposta = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja apagar o boletim {boletim.numero}?\n\n"
            f"⚠️ ATENÇÃO: Isto vai afetar os cálculos de Saldos Pessoais!",
            icon='warning'
        )

        if resposta:
            sucesso, erro = self.manager.apagar(boletim.id)
            if sucesso:
                messagebox.showinfo("Sucesso", "Boletim apagado!")
                self.carregar_boletins()
            else:
                messagebox.showerror("Erro", f"Erro: {erro}")


class FormularioBoletimDialog(ctk.CTkToplevel):
    """
    Dialog para emitir/editar boletim
    """

    def __init__(self, parent, manager: BoletinsManager, boletim=None, callback=None):
        super().__init__(parent)

        self.manager = manager
        self.boletim = boletim
        self.callback = callback

        self.title("Emitir Boletim" if not boletim else f"Editar Boletim {boletim.numero}")
        self.geometry("500x500")

        self.transient(parent)
        self.grab_set()

        self.create_form()

        if boletim:
            self.carregar_dados()
        else:
            # Sugerir valores para novo boletim
            self.sugerir_valores()

    def create_form(self):
        """Create form fields"""

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Sócio
        ctk.CTkLabel(scroll, text="Sócio *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.socio_var = ctk.StringVar(value="BRUNO")
        socio_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        socio_frame.pack(fill="x", pady=(0, 10))

        self.socio_bruno_radio = ctk.CTkRadioButton(
            socio_frame,
            text="Bruno",
            variable=self.socio_var,
            value="BRUNO",
            command=self.socio_mudou
        )
        self.socio_bruno_radio.pack(side="left", padx=(0, 20))

        self.socio_rafael_radio = ctk.CTkRadioButton(
            socio_frame,
            text="Rafael",
            variable=self.socio_var,
            value="RAFAEL",
            command=self.socio_mudou
        )
        self.socio_rafael_radio.pack(side="left")

        # Data emissão
        ctk.CTkLabel(scroll, text="Data de Emissão *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.data_emissao_entry = ctk.CTkEntry(scroll, placeholder_text="AAAA-MM-DD")
        self.data_emissao_entry.pack(fill="x", pady=(0, 10))
        # Preencher com hoje
        self.data_emissao_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        # Valor (com sugestão)
        valor_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        valor_frame.pack(fill="x", pady=(10, 10))

        ctk.CTkLabel(valor_frame, text="Valor *", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))

        self.sugestao_label = ctk.CTkLabel(
            valor_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.sugestao_label.pack(side="left")

        self.valor_entry = ctk.CTkEntry(scroll, placeholder_text="0.00")
        self.valor_entry.pack(fill="x", pady=(0, 10))

        # Descrição
        ctk.CTkLabel(scroll, text="Descrição", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.descricao_entry = ctk.CTkTextbox(scroll, height=80)
        self.descricao_entry.pack(fill="x", pady=(0, 10))

        # Nota
        ctk.CTkLabel(scroll, text="Nota", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.nota_entry = ctk.CTkTextbox(scroll, height=60)
        self.nota_entry.pack(fill="x", pady=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            width=120,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="right", padx=5)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Emitir" if not self.boletim else "Guardar",
            command=self.guardar,
            width=120,
            fg_color=("#FF9800", "#F57C00"),
            hover_color=("#FFB74D", "#E65100")
        )
        save_btn.pack(side="right", padx=5)

    def socio_mudou(self):
        """Atualizar sugestão quando sócio muda"""
        if not self.boletim:  # Só em novo boletim
            self.sugerir_valores()

    def sugerir_valores(self):
        """Sugerir valor baseado no saldo"""
        socio = Socio.BRUNO if self.socio_var.get() == "BRUNO" else Socio.RAFAEL
        valor_sugerido = self.manager.sugerir_valor(socio)

        self.sugestao_label.configure(text=f"(Sugestão: €{float(valor_sugerido):,.2f})")

        # Preencher valor se vazio
        if not self.valor_entry.get():
            self.valor_entry.delete(0, "end")
            self.valor_entry.insert(0, str(valor_sugerido))

    def carregar_dados(self):
        """Load boletim data"""
        b = self.boletim

        self.socio_var.set(b.socio.value)
        self.data_emissao_entry.delete(0, "end")
        self.data_emissao_entry.insert(0, b.data_emissao.strftime("%Y-%m-%d"))
        self.valor_entry.insert(0, str(b.valor))

        if b.descricao:
            self.descricao_entry.insert("1.0", b.descricao)
        if b.nota:
            self.nota_entry.insert("1.0", b.nota)

    def guardar(self):
        """Save boletim"""
        try:
            socio = Socio.BRUNO if self.socio_var.get() == "BRUNO" else Socio.RAFAEL

            data_emissao_str = self.data_emissao_entry.get().strip()
            if not data_emissao_str:
                messagebox.showerror("Erro", "Data de emissão é obrigatória")
                return
            data_emissao = date.fromisoformat(data_emissao_str)

            valor_str = self.valor_entry.get().strip()
            if not valor_str:
                messagebox.showerror("Erro", "Valor é obrigatório")
                return
            valor = Decimal(valor_str.replace(',', '.'))

            descricao = self.descricao_entry.get("1.0", "end-1c").strip() or None
            nota = self.nota_entry.get("1.0", "end-1c").strip() or None

            if self.boletim:
                # Update
                sucesso, erro = self.manager.atualizar(
                    self.boletim.id,
                    socio=socio,
                    data_emissao=data_emissao,
                    valor=valor,
                    descricao=descricao,
                    nota=nota
                )
                msg = "Boletim atualizado!"
            else:
                # Create
                sucesso, boletim, erro = self.manager.emitir(
                    socio=socio,
                    data_emissao=data_emissao,
                    valor=valor,
                    descricao=descricao,
                    nota=nota
                )
                msg = f"Boletim {boletim.numero} emitido com sucesso!"

            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro: {erro}")

        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
