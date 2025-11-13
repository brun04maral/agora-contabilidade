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
from ui.components.data_table_v2 import DataTableV2
from assets.resources import get_icon, BOLETINS


class BoletinsScreen(ctk.CTkFrame):
    """
    Tela de gestão de Boletins (listar + emitir + marcar pago)
    """

    def __init__(self, parent, db_session: Session, filtro_estado=None, filtro_socio=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = BoletinsManager(db_session)
        self.filtro_inicial_estado = filtro_estado
        self.filtro_inicial_socio = filtro_socio

        self.configure(fg_color="transparent")
        self.create_widgets()

        # Apply initial filter if provided
        if self.filtro_inicial_estado or self.filtro_inicial_socio:
            if self.filtro_inicial_estado:
                self.estado_filter.set(self.filtro_inicial_estado)
            if self.filtro_inicial_socio:
                self.socio_filter.set(self.filtro_inicial_socio)
            self.aplicar_filtros()
        else:
            self.carregar_boletins()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(BOLETINS, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Boletins",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
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
            values=["Todos", "BA", "RR"],
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

        # Selection actions bar (created but NOT packed - will be shown on selection)
        self.selection_frame = ctk.CTkFrame(self, fg_color="transparent")

        # Clear selection button
        self.cancel_btn = ctk.CTkButton(
            self.selection_frame,
            text="🗑️ Limpar Seleção",
            command=self.cancelar_selecao,
            width=150, height=35
        )

        # Selection count label
        self.count_label = ctk.CTkLabel(
            self.selection_frame,
            text="0 selecionados",
            font=ctk.CTkFont(size=13)
        )

        # Mark as paid button
        self.marcar_pago_btn = ctk.CTkButton(
            self.selection_frame,
            text="✅ Marcar como Pago",
            command=self.marcar_como_pago_batch,
            width=180, height=35,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )

        # Report button
        self.report_btn = ctk.CTkButton(
            self.selection_frame,
            text="📊 Criar Relatório",
            command=self.criar_relatorio,
            width=160, height=35
        )

        # Total label
        self.total_label = ctk.CTkLabel(
            self.selection_frame,
            text="Total: €0,00",
            font=ctk.CTkFont(size=14, weight="bold")
        )

        # Table
        columns = [
            {'key': 'numero', 'label': 'ID', 'width': 80, 'sortable': True},
            {'key': 'socio', 'label': 'Sócio', 'width': 120, 'sortable': True},
            {'key': 'data_emissao', 'label': 'Data Emissão', 'width': 120, 'sortable': True},
            {'key': 'valor_fmt', 'label': 'Valor', 'width': 110, 'sortable': True},
            {'key': 'descricao', 'label': 'Descrição', 'width': 260, 'sortable': False},
            {'key': 'estado', 'label': 'Estado', 'width': 100, 'sortable': True},
            {'key': 'data_pagamento', 'label': 'Data Pagamento', 'width': 130, 'sortable': True},
        ]

        self.table = DataTableV2(
            self,
            columns=columns,
            on_row_double_click=self.editar_boletim,
            on_selection_change=self.on_selection_change,
            height=400
        )
        self.table.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    def carregar_boletins(self):
        """Load and display boletins"""
        boletins = self.manager.listar_todos()
        data = [self.boletim_to_dict(b) for b in boletins]
        self.table.set_data(data)

    def boletim_to_dict(self, boletim) -> dict:
        """Convert boletim to dict for table"""
        # Determine color based on estado
        color = self.get_estado_color(boletim.estado)

        return {
            'id': boletim.id,
            'numero': boletim.numero,
            'socio': "BA" if boletim.socio == Socio.BRUNO else "RR",
            'data_emissao': boletim.data_emissao.strftime("%Y-%m-%d") if boletim.data_emissao else '-',
            'valor': float(boletim.valor),
            'valor_fmt': f"€{float(boletim.valor):,.2f}",
            'descricao': boletim.descricao or '-',
            'estado': "Pendente" if boletim.estado == EstadoBoletim.PENDENTE else "Pago",
            'data_pagamento': boletim.data_pagamento.strftime("%Y-%m-%d") if boletim.data_pagamento else '-',
            '_bg_color': color,
            '_boletim': boletim
        }

    def get_estado_color(self, estado: EstadoBoletim) -> tuple:
        """Get color for estado (returns tuple: light, dark mode) - Opção 3 Agora Inspired"""
        color_map = {
            EstadoBoletim.PENDENTE: ("#FFE5D0", "#8B4513"),  # Laranja pastel - atenção
            EstadoBoletim.PAGO: ("#E8F5E0", "#4A7028")        # Verde pastel - positivo
        }
        return color_map.get(estado, ("#E0E0E0", "#4A4A4A"))

    def aplicar_filtros(self, *args):
        """Apply filters"""
        socio = self.socio_filter.get()
        estado = self.estado_filter.get()

        boletins = self.manager.listar_todos()

        # Filter by socio
        if socio != "Todos":
            socio_enum = Socio.BRUNO if socio == "BA" else Socio.RAFAEL
            boletins = [b for b in boletins if b.socio == socio_enum]

        # Filter by estado
        if estado != "Todos":
            estado_enum = EstadoBoletim.PENDENTE if estado == "Pendente" else EstadoBoletim.PAGO
            boletins = [b for b in boletins if b.estado == estado_enum]

        data = [self.boletim_to_dict(b) for b in boletins]
        self.table.set_data(data)

        # Clear selection when filters change
        self.table.clear_selection()

    def after_save_callback(self):
        """Callback after saving - reload data and clear selection"""
        self.carregar_boletins()
        self.table.clear_selection()

    def abrir_formulario(self, boletim=None):
        """Open form dialog"""
        FormularioBoletimDialog(self, self.manager, boletim, self.after_save_callback)

    def editar_boletim(self, data: dict):
        """Edit boletim (triggered by double-click)"""
        boletim = data.get('_boletim')
        if boletim:
            self.abrir_formulario(boletim)

    def on_selection_change(self, selected_data: list):
        """Handle selection change in table"""
        num_selected = len(selected_data)

        if num_selected > 0:
            # Show selection frame
            self.selection_frame.pack(fill="x", padx=30, pady=(0, 10))

            # Show selection bar
            self.cancel_btn.pack(side="left", padx=5)

            # Show count
            count_text = f"{num_selected} selecionado" if num_selected == 1 else f"{num_selected} selecionados"
            self.count_label.configure(text=count_text)
            self.count_label.pack(side="left", padx=15)

            # Show "Marcar como Pago" only if there are unpaid boletins
            has_unpaid = any(
                item.get('_boletim') and item.get('_boletim').estado != EstadoBoletim.PAGO
                for item in selected_data
            )
            if has_unpaid:
                self.marcar_pago_btn.pack(side="left", padx=5)

            self.report_btn.pack(side="left", padx=5)

            # Calculate and show total
            total = sum(item.get('valor', 0) for item in selected_data)
            self.total_label.configure(text=f"Total: €{total:,.2f}")
            self.total_label.pack(side="left", padx=20)
        else:
            # Hide entire selection frame when nothing is selected
            self.selection_frame.pack_forget()

    def cancelar_selecao(self):
        """Cancel selection"""
        self.table.clear_selection()

    def marcar_como_pago_batch(self):
        """Mark selected boletins as paid"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) == 0:
            return

        # Filter only unpaid boletins
        unpaid_boletins = [
            item.get('_boletim') for item in selected_data
            if item.get('_boletim') and item.get('_boletim').estado != EstadoBoletim.PAGO
        ]

        if len(unpaid_boletins) == 0:
            messagebox.showinfo("Info", "Todos os boletins selecionados já estão pagos.")
            return

        # Confirm action
        resposta = messagebox.askyesno(
            "Confirmar",
            f"Marcar {len(unpaid_boletins)} boletim(ns) como pago(s)?\n\n"
            f"Data de pagamento será definida como hoje ({date.today().strftime('%Y-%m-%d')})."
        )

        if resposta:
            hoje = date.today()
            erros = []

            for boletim in unpaid_boletins:
                sucesso, erro = self.manager.marcar_como_pago(boletim.id)
                if not sucesso:
                    erros.append(f"{boletim.numero}: {erro}")

            if len(erros) == 0:
                messagebox.showinfo("Sucesso", f"{len(unpaid_boletins)} boletim(ns) marcado(s) como pago(s)!")
                self.carregar_boletins()
                self.table.clear_selection()
            else:
                messagebox.showerror("Erro", f"Erros ao marcar boletins:\n" + "\n".join(erros))
                self.carregar_boletins()

    def criar_relatorio(self):
        """Create report for selected boletins and navigate to Relatorios tab"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) > 0:
            # Extract boletim IDs from selected data
            boletim_ids = [item.get('id') for item in selected_data if item.get('id')]

            # Navigate to Relatorios tab with selected boletim IDs
            main_window = self.master.master
            if hasattr(main_window, 'show_relatorios'):
                main_window.show_relatorios(boletim_ids=boletim_ids)
            else:
                messagebox.showerror("Erro", "Não foi possível navegar para a aba de Relatórios")


class FormularioBoletimDialog(ctk.CTkToplevel):
    """
    Dialog para emitir/editar boletim
    """

    def __init__(self, parent, manager: BoletinsManager, boletim=None, callback=None):
        super().__init__(parent)

        self.manager = manager
        self.boletim = boletim
        self.callback = callback
        self.parent = parent

        self.title("Emitir Boletim" if not boletim else f"Editar Boletim {boletim.numero}")
        self.geometry("500x500")

        self.transient(parent)
        self.grab_set()

        # Create form (needs to be created first to have scroll reference)
        self.create_form()

        # Setup scroll event capture
        self._setup_scroll_capture()

        if boletim:
            self.carregar_dados()
        else:
            # Sugerir valores para novo boletim
            self.sugerir_valores()

        # Handle window close to clear selection
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def create_form(self):
        """Create form fields"""

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        scroll = self.scroll

        # Sócio
        ctk.CTkLabel(scroll, text="Sócio *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.socio_var = ctk.StringVar(value="BRUNO")
        socio_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        socio_frame.pack(fill="x", pady=(0, 10))

        self.socio_bruno_radio = ctk.CTkRadioButton(
            socio_frame,
            text="BA",
            variable=self.socio_var,
            value="BRUNO",
            command=self.socio_mudou
        )
        self.socio_bruno_radio.pack(side="left", padx=(0, 20))

        self.socio_rafael_radio = ctk.CTkRadioButton(
            socio_frame,
            text="RR",
            variable=self.socio_var,
            value="RAFAEL",
            command=self.socio_mudou
        )
        self.socio_rafael_radio.pack(side="left")

        # Data emissão
        ctk.CTkLabel(scroll, text="Data de Emissão *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        from ui.components.date_picker_dropdown import DatePickerDropdown
        self.data_emissao_picker = DatePickerDropdown(scroll, default_date=date.today(), placeholder="Selecionar data de emissão...")
        self.data_emissao_picker.pack(fill="x", pady=(0, 10))

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
            command=self._on_close,
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
        self.data_emissao_picker.set_date(b.data_emissao)
        self.valor_entry.insert(0, str(b.valor))

        if b.descricao:
            self.descricao_entry.insert("1.0", b.descricao)
        if b.nota:
            self.nota_entry.insert("1.0", b.nota)

    def guardar(self):
        """Save boletim"""
        try:
            socio = Socio.BRUNO if self.socio_var.get() == "BRUNO" else Socio.RAFAEL

            if not self.data_emissao_picker.get():
                messagebox.showerror("Erro", "Data de emissão é obrigatória")
                return
            data_emissao = self.data_emissao_picker.get_date()

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

    def _setup_scroll_capture(self):
        """Capture scroll events on this dialog and redirect only to internal scrollable frame"""
        # Get the internal canvas from CTkScrollableFrame
        if hasattr(self.scroll, '_parent_canvas'):
            canvas = self.scroll._parent_canvas

            def handle_scroll(event):
                """Handle scroll event - redirect to internal canvas and stop propagation"""
                # Scroll the internal canvas
                if event.num == 4 or event.delta > 0:
                    # Scroll up
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5 or event.delta < 0:
                    # Scroll down
                    canvas.yview_scroll(1, "units")

                # Return "break" to stop event propagation
                return "break"

            # Bind with add=True to not remove existing bindings
            # Windows and MacOS
            self.bind_all("<MouseWheel>", handle_scroll, add=True)
            # Linux
            self.bind_all("<Button-4>", handle_scroll, add=True)
            self.bind_all("<Button-5>", handle_scroll, add=True)

    def _on_close(self):
        """Handle window close - clear selection"""
        # No need to unbind - tkinter cleans up when dialog destroys
        if hasattr(self.parent, 'table'):
            self.parent.table.clear_selection()
        self.destroy()
