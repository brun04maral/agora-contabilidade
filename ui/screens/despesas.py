# -*- coding: utf-8 -*-
"""
Tela de gestão de Despesas
"""
import customtkinter as ctk
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
import tkinter.messagebox as messagebox

from logic.despesas import DespesasManager
from database.models import TipoDespesa, EstadoDespesa
from ui.components.data_table_v2 import DataTableV2
from assets.resources import get_icon, DESPESAS


class DespesasScreen(ctk.CTkFrame):
    """
    Tela de gestão de Despesas (CRUD completo)
    """

    def __init__(self, parent, db_session: Session, filtro_estado=None, filtro_tipo=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = DespesasManager(db_session)
        self.filtro_inicial_estado = filtro_estado
        self.filtro_inicial_tipo = filtro_tipo

        self.configure(fg_color="transparent")
        self.create_widgets()

        # Apply initial filter if provided
        if self.filtro_inicial_estado or self.filtro_inicial_tipo:
            if self.filtro_inicial_estado:
                self.estado_filter.set(self.filtro_inicial_estado)
            if self.filtro_inicial_tipo:
                self.tipo_filter.set(self.filtro_inicial_tipo)
            self.aplicar_filtros()
        else:
            self.carregar_despesas()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(DESPESAS, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Despesas",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text="💸 Despesas",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

        # Buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Atualizar",
            command=self.carregar_despesas,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=5)

        gerar_recorrentes_btn = ctk.CTkButton(
            btn_frame,
            text="🔁 Gerar Recorrentes",
            command=self.gerar_despesas_recorrentes,
            width=170,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#64B5F6", "#1565C0")
        )
        gerar_recorrentes_btn.pack(side="left", padx=5)

        editar_templates_btn = ctk.CTkButton(
            btn_frame,
            text="📝 Editar Recorrentes",
            command=self.abrir_templates,
            width=170,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#9C27B0", "#7B1FA2"),
            hover_color=("#BA68C8", "#6A1B9A")
        )
        editar_templates_btn.pack(side="left", padx=5)

        nova_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Nova Despesa",
            command=self.abrir_formulario,
            width=140,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#F44336", "#C62828"),
            hover_color=("#E57373", "#B71C1C")
        )
        nova_btn.pack(side="left", padx=5)

        # Filters
        filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        filters_frame.pack(fill="x", padx=30, pady=(0, 20))

        # Tipo filter
        ctk.CTkLabel(
            filters_frame,
            text="Tipo:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.tipo_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "Fixa Mensal", "Pessoal BA", "Pessoal RR", "Equipamento", "Projeto"],
            command=self.aplicar_filtros,
            width=180
        )
        self.tipo_filter.pack(side="left", padx=(0, 20))

        # Estado filter
        ctk.CTkLabel(
            filters_frame,
            text="Estado:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.estado_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "Pendente", "Vencido", "Pago"],
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
            command=self.marcar_como_pago,
            width=160, height=35,
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
            {'key': 'numero', 'label': 'ID', 'width': 100, 'sortable': True},
            {'key': 'data', 'label': 'Data', 'width': 120, 'sortable': True},
            {'key': 'tipo', 'label': 'Tipo', 'width': 140, 'sortable': False},
            {'key': 'credor_nome', 'label': 'Credor', 'width': 160, 'sortable': True},
            {'key': 'descricao', 'label': 'Descrição', 'width': 280, 'sortable': False},
            {'key': 'valor_com_iva_fmt', 'label': 'Valor c/ IVA', 'width': 120, 'sortable': True},
            {'key': 'estado', 'label': 'Estado', 'width': 110, 'sortable': True},
        ]

        self.table = DataTableV2(
            self,
            columns=columns,
            show_actions=True,
            on_edit=self.editar_despesa,
            on_delete=self.apagar_despesa,
            on_row_double_click=self.editar_despesa,
            on_selection_change=self.on_selection_change,
            height=400
        )
        self.table.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    def carregar_despesas(self):
        """Load and display despesas"""
        despesas = self.manager.listar_todas()
        data = [self.despesa_to_dict(d) for d in despesas]
        self.table.set_data(data)

    def despesa_to_dict(self, despesa) -> dict:
        """Convert despesa to dict for table"""
        # Determine color based on estado
        color = self.get_estado_color(despesa.estado)

        # Add asterisk to tipo if generated from template
        tipo_label = self.tipo_to_label(despesa.tipo)
        if despesa.despesa_template_id:
            tipo_label += "*"

        return {
            'id': despesa.id,
            'numero': despesa.numero,
            'data': despesa.data.strftime("%Y-%m-%d") if despesa.data else '-',
            'tipo': tipo_label,
            'credor_nome': despesa.credor.nome if despesa.credor else '-',
            'descricao': despesa.descricao,
            'valor_com_iva': float(despesa.valor_com_iva),
            'valor_com_iva_fmt': f"€{float(despesa.valor_com_iva):,.2f}",
            'estado': self.estado_to_label(despesa.estado),
            '_bg_color': color,
            '_despesa': despesa
        }

    def get_estado_color(self, estado: EstadoDespesa) -> tuple:
        """Get color for estado (returns tuple: light, dark mode) - Opção 3 Agora Inspired"""
        color_map = {
            EstadoDespesa.PAGO: ("#E8F5E0", "#4A7028"),        # Verde pastel - positivo
            EstadoDespesa.PENDENTE: ("#FFF4CC", "#806020"),    # Dourado pastel - harmoniza com BA
            EstadoDespesa.VENCIDO: ("#FFE5D0", "#8B4513")      # Laranja pastel - atenção urgente
        }
        return color_map.get(estado, ("#E0E0E0", "#4A4A4A"))

    def tipo_to_label(self, tipo: TipoDespesa) -> str:
        """Convert tipo enum to label"""
        mapping = {
            TipoDespesa.FIXA_MENSAL: "Fixa Mensal",
            TipoDespesa.PESSOAL_BRUNO: "Pessoal BA",
            TipoDespesa.PESSOAL_RAFAEL: "Pessoal RR",
            TipoDespesa.EQUIPAMENTO: "Equipamento",
            TipoDespesa.PROJETO: "Projeto"
        }
        return mapping.get(tipo, str(tipo))

    def estado_to_label(self, estado: EstadoDespesa) -> str:
        """Convert estado enum to label"""
        mapping = {
            EstadoDespesa.PENDENTE: "Pendente",
            EstadoDespesa.VENCIDO: "Vencido",
            EstadoDespesa.PAGO: "Pago"
        }
        return mapping.get(estado, str(estado))

    def aplicar_filtros(self, *args):
        """Apply filters"""
        tipo = self.tipo_filter.get()
        estado = self.estado_filter.get()

        despesas = self.manager.listar_todas()

        # Filter by tipo
        if tipo != "Todos":
            tipo_map = {
                "Fixa Mensal": TipoDespesa.FIXA_MENSAL,
                "Pessoal BA": TipoDespesa.PESSOAL_BRUNO,
                "Pessoal RR": TipoDespesa.PESSOAL_RAFAEL,
                "Equipamento": TipoDespesa.EQUIPAMENTO,
                "Projeto": TipoDespesa.PROJETO
            }
            tipo_enum = tipo_map[tipo]
            despesas = [d for d in despesas if d.tipo == tipo_enum]

        # Filter by estado
        if estado != "Todos":
            estado_map = {
                "Pendente": EstadoDespesa.PENDENTE,
                "Vencido": EstadoDespesa.VENCIDO,
                "Pago": EstadoDespesa.PAGO
            }
            estado_enum = estado_map[estado]
            despesas = [d for d in despesas if d.estado == estado_enum]

        data = [self.despesa_to_dict(d) for d in despesas]
        self.table.set_data(data)

        # Clear selection when filters change
        self.table.clear_selection()

    def after_save_callback(self):
        """Callback after saving - reload data and clear selection"""
        self.carregar_despesas()
        self.table.clear_selection()

    def abrir_formulario(self, despesa=None):
        """Open form dialog"""
        FormularioDespesaDialog(self, self.manager, despesa, self.after_save_callback)

    def gerar_despesas_recorrentes(self):
        """Gera despesas recorrentes para o mês atual"""
        from datetime import date
        hoje = date.today()
        mes_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][hoje.month - 1]

        # Confirmar com o usuário
        resposta = messagebox.askyesno(
            "Gerar Despesas Recorrentes",
            f"Gerar despesas recorrentes para {mes_nome} de {hoje.year}?\n\n"
            f"Serão criadas automaticamente as despesas fixas mensais configuradas como recorrentes."
        )

        if not resposta:
            return

        # Gerar despesas
        geradas, erros = self.manager.verificar_e_gerar_recorrentes_pendentes()

        # Mostrar resultado
        if geradas > 0:
            msg = f"✅ {geradas} despesa(s) recorrente(s) gerada(s) com sucesso!"
            if erros:
                msg += f"\n\n⚠️ {len(erros)} erro(s):\n" + "\n".join(erros[:3])
                if len(erros) > 3:
                    msg += f"\n... e mais {len(erros) - 3} erro(s)"
            messagebox.showinfo("Sucesso", msg)
            self.carregar_despesas()  # Recarregar lista
        elif erros:
            msg = f"❌ Nenhuma despesa gerada.\n\nErros:\n" + "\n".join(erros[:5])
            if len(erros) > 5:
                msg += f"\n... e mais {len(erros) - 5} erro(s)"
            messagebox.showerror("Erro", msg)
        else:
            messagebox.showinfo(
                "Sem Novas Despesas",
                f"Nenhuma despesa recorrente para gerar em {mes_nome}.\n\n"
                f"As despesas deste mês já foram geradas ou não há templates configurados."
            )

    def abrir_templates(self):
        """Abre janela de gestão de templates de despesas recorrentes"""
        from ui.screens.templates_despesas import TemplatesDespesasScreen

        # Criar janela modal
        dialog = ctk.CTkToplevel(self)
        dialog.title("Templates de Despesas Recorrentes")
        dialog.geometry("1000x700")
        dialog.transient(self)
        dialog.grab_set()

        # Adicionar screen de templates
        templates_screen = TemplatesDespesasScreen(dialog, self.db_session)
        templates_screen.pack(fill="both", expand=True)

        # Ao fechar, atualizar lista de despesas
        def on_close():
            dialog.destroy()
            self.carregar_despesas()

        dialog.protocol("WM_DELETE_WINDOW", on_close)

    def editar_despesa(self, data: dict):
        """Edit despesa (triggered by double-click)"""
        despesa = data.get('_despesa')
        if despesa:
            self.abrir_formulario(despesa)

    def apagar_despesa(self, data: dict):
        """Apagar despesa individual"""
        despesa = data.get('_despesa')
        if not despesa:
            return

        # Mostrar informação se foi gerada de template
        msg = f"Apagar despesa {despesa.numero}?"
        if despesa.despesa_template_id:
            msg += f"\n\n⚠️ Esta despesa foi gerada automaticamente do template {despesa.despesa_template.numero}."
            msg += "\nAo apagar, ela não será recriada automaticamente."

        resposta = messagebox.askyesno("Confirmar", msg)

        if resposta:
            sucesso, erro = self.manager.apagar(despesa.id)
            if sucesso:
                messagebox.showinfo("Sucesso", "Despesa apagada com sucesso!")
                self.carregar_despesas()
            else:
                messagebox.showerror("Erro", f"Erro ao apagar: {erro}")

    def on_selection_change(self, selected_data: list):
        """Handle selection change in table"""
        num_selected = len(selected_data)

        if num_selected > 0:
            # Show selection frame
            self.selection_frame.pack(fill="x", padx=30, pady=(0, 10))

            # Show selection bar
            self.cancel_btn.pack(side="left", padx=5)

            # Show count
            count_text = f"{num_selected} selecionada" if num_selected == 1 else f"{num_selected} selecionadas"
            self.count_label.configure(text=count_text)
            self.count_label.pack(side="left", padx=15)

            # Show "Marcar como Pago" only if there are unpaid despesas
            has_unpaid = any(
                item.get('_despesa') and item.get('_despesa').estado != EstadoDespesa.PAGO
                for item in selected_data
            )
            if has_unpaid:
                self.marcar_pago_btn.pack(side="left", padx=5)

            self.report_btn.pack(side="left", padx=5)

            # Calculate and show total
            total = sum(item.get('valor_com_iva', 0) for item in selected_data)
            self.total_label.configure(text=f"Total: €{total:,.2f}")
            self.total_label.pack(side="left", padx=20)
        else:
            # Hide entire selection frame when nothing is selected
            self.selection_frame.pack_forget()

    def cancelar_selecao(self):
        """Cancel selection"""
        self.table.clear_selection()

    def marcar_como_pago(self):
        """Mark selected despesas as paid"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) == 0:
            return

        # Filter only unpaid despesas
        unpaid_despesas = [
            item.get('_despesa') for item in selected_data
            if item.get('_despesa') and item.get('_despesa').estado != EstadoDespesa.PAGO
        ]

        if len(unpaid_despesas) == 0:
            messagebox.showinfo("Info", "Todas as despesas selecionadas já estão pagas.")
            return

        # Confirm action
        resposta = messagebox.askyesno(
            "Confirmar",
            f"Marcar {len(unpaid_despesas)} despesa(s) como pagas?\n\n"
            f"Data de pagamento será definida como hoje ({date.today().strftime('%Y-%m-%d')})."
        )

        if resposta:
            hoje = date.today()
            erros = []

            for despesa in unpaid_despesas:
                sucesso, erro = self.manager.atualizar(
                    despesa.id,
                    estado=EstadoDespesa.PAGO,
                    data_pagamento=hoje
                )
                if not sucesso:
                    erros.append(f"{despesa.numero}: {erro}")

            if len(erros) == 0:
                messagebox.showinfo("Sucesso", f"{len(unpaid_despesas)} despesa(s) marcada(s) como paga(s)!")
                self.carregar_despesas()
                self.table.clear_selection()
            else:
                messagebox.showerror("Erro", f"Erros ao marcar despesas:\n" + "\n".join(erros))
                self.carregar_despesas()

    def criar_relatorio(self):
        """Create report for selected despesas and navigate to Relatorios tab"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) > 0:
            # Extract despesa IDs from selected data
            despesa_ids = [item.get('id') for item in selected_data if item.get('id')]

            # Navigate to Relatorios tab
            # Hierarchy: self (DespesasScreen) -> master (content_frame) -> master (MainWindow)
            main_window = self.master.master
            if hasattr(main_window, 'show_relatorios'):
                main_window.show_relatorios(despesa_ids=despesa_ids)
            else:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível navegar para a aba de Relatórios"
                )


class FormularioDespesaDialog(ctk.CTkToplevel):
    """
    Dialog para criar/editar despesas
    """

    def __init__(self, parent, manager: DespesasManager, despesa=None, callback=None):
        super().__init__(parent)

        self.manager = manager
        self.despesa = despesa
        self.callback = callback
        self.parent = parent

        self.title("Nova Despesa" if not despesa else f"Editar Despesa {despesa.numero}")
        self.geometry("600x750")

        self.transient(parent)
        self.grab_set()

        # Create form (needs to be created first to have scroll reference)
        self.create_form()

        # Setup scroll event capture
        self._setup_scroll_capture()

        if despesa:
            self.carregar_dados()

        # Handle window close to clear selection
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def create_form(self):
        """Create form fields"""

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        scroll = self.scroll

        # Tipo
        ctk.CTkLabel(scroll, text="Tipo *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.tipo_var = ctk.StringVar(value="FIXA_MENSAL")
        tipo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        tipo_frame.pack(fill="x", pady=(0, 10))

        tipos = [
            ("Fixa Mensal", "FIXA_MENSAL"),
            ("Pessoal BA", "PESSOAL_BRUNO"),
            ("Pessoal RR", "PESSOAL_RAFAEL"),
            ("Equipamento", "EQUIPAMENTO"),
            ("Projeto", "PROJETO")
        ]

        for i, (label, value) in enumerate(tipos):
            ctk.CTkRadioButton(
                tipo_frame,
                text=label,
                variable=self.tipo_var,
                value=value
            ).pack(side="left", padx=(0, 15))

        # Data
        ctk.CTkLabel(scroll, text="Data *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        from ui.components.date_picker_dropdown import DatePickerDropdown
        self.data_picker = DatePickerDropdown(scroll, placeholder="Selecionar data...")
        self.data_picker.pack(fill="x", pady=(0, 10))

        # Credor/Fornecedor
        ctk.CTkLabel(scroll, text="Credor/Fornecedor", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        fornecedores = self.manager.obter_fornecedores()
        fornecedor_options = ["(Nenhum)"] + [f"{f.numero} - {f.nome}" for f in fornecedores]
        self.credor_dropdown = ctk.CTkOptionMenu(scroll, values=fornecedor_options, width=400)
        self.credor_dropdown.pack(anchor="w", pady=(0, 10))
        self.fornecedores_map = {f"{f.numero} - {f.nome}": f.id for f in fornecedores}

        # Projeto associado
        ctk.CTkLabel(scroll, text="Projeto Associado", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        projetos = self.manager.obter_projetos()
        projeto_options = ["(Nenhum)"] + [f"{p.numero} - {p.descricao[:30]}" for p in projetos]
        self.projeto_dropdown = ctk.CTkOptionMenu(scroll, values=projeto_options, width=400)
        self.projeto_dropdown.pack(anchor="w", pady=(0, 10))
        self.projetos_map = {f"{p.numero} - {p.descricao[:30]}": p.id for p in projetos}

        # Descrição
        ctk.CTkLabel(scroll, text="Descrição *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.descricao_entry = ctk.CTkTextbox(scroll, height=80)
        self.descricao_entry.pack(fill="x", pady=(0, 10))

        # Valores
        valores_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        valores_frame.pack(fill="x", pady=(10, 10))
        valores_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(valores_frame, text="Valor sem IVA *", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.valor_sem_iva_entry = ctk.CTkEntry(valores_frame, placeholder_text="0.00")
        self.valor_sem_iva_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(5, 10))

        ctk.CTkLabel(valores_frame, text="Valor com IVA *", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, sticky="w")
        self.valor_com_iva_entry = ctk.CTkEntry(valores_frame, placeholder_text="0.00")
        self.valor_com_iva_entry.grid(row=1, column=1, sticky="ew", pady=(5, 10))

        # Estado
        ctk.CTkLabel(scroll, text="Estado *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.estado_dropdown = ctk.CTkOptionMenu(scroll, values=["Pendente", "Vencido", "Pago"])
        self.estado_dropdown.pack(anchor="w", pady=(0, 10))

        # Data pagamento
        ctk.CTkLabel(scroll, text="Data Pagamento (se pago)", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.data_pagamento_picker = DatePickerDropdown(scroll, placeholder="Selecionar data de pagamento...")
        self.data_pagamento_picker.pack(fill="x", pady=(0, 10))

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
            text="Guardar",
            command=self.guardar,
            width=120,
            fg_color=("#F44336", "#C62828"),
            hover_color=("#E57373", "#B71C1C")
        )
        save_btn.pack(side="right", padx=5)

    def carregar_dados(self):
        """Load despesa data into form"""
        d = self.despesa

        self.tipo_var.set(d.tipo.value)

        if d.data:
            self.data_picker.set_date(d.data)

        if d.credor:
            credor_str = f"{d.credor.numero} - {d.credor.nome}"
            self.credor_dropdown.set(credor_str)

        if d.projeto:
            projeto_str = f"{d.projeto.numero} - {d.projeto.descricao[:30]}"
            self.projeto_dropdown.set(projeto_str)

        self.descricao_entry.insert("1.0", d.descricao)

        self.valor_sem_iva_entry.insert(0, str(d.valor_sem_iva))
        self.valor_com_iva_entry.insert(0, str(d.valor_com_iva))

        estado_map = {
            EstadoDespesa.PENDENTE: "Pendente",
            EstadoDespesa.VENCIDO: "Vencido",
            EstadoDespesa.PAGO: "Pago"
        }
        self.estado_dropdown.set(estado_map[d.estado])

        if d.data_pagamento:
            self.data_pagamento_picker.set_date(d.data_pagamento)

        if d.nota:
            self.nota_entry.insert("1.0", d.nota)

    def guardar(self):
        """Save despesa"""
        try:
            # Get values
            tipo_str = self.tipo_var.get()
            tipo = TipoDespesa[tipo_str]

            if not self.data_picker.get():
                messagebox.showerror("Erro", "Data é obrigatória")
                return
            data_despesa = self.data_picker.get_date()

            credor_str = self.credor_dropdown.get()
            credor_id = self.fornecedores_map.get(credor_str) if credor_str != "(Nenhum)" else None

            projeto_str = self.projeto_dropdown.get()
            projeto_id = self.projetos_map.get(projeto_str) if projeto_str != "(Nenhum)" else None

            descricao = self.descricao_entry.get("1.0", "end-1c").strip()
            if not descricao:
                messagebox.showerror("Erro", "Descrição é obrigatória")
                return

            valor_sem_iva_str = self.valor_sem_iva_entry.get().strip()
            if not valor_sem_iva_str:
                messagebox.showerror("Erro", "Valor sem IVA é obrigatório")
                return
            valor_sem_iva = Decimal(valor_sem_iva_str.replace(',', '.'))

            valor_com_iva_str = self.valor_com_iva_entry.get().strip()
            if not valor_com_iva_str:
                messagebox.showerror("Erro", "Valor com IVA é obrigatório")
                return
            valor_com_iva = Decimal(valor_com_iva_str.replace(',', '.'))

            estado_map = {
                "Pendente": EstadoDespesa.PENDENTE,
                "Vencido": EstadoDespesa.VENCIDO,
                "Pago": EstadoDespesa.PAGO
            }
            estado = estado_map[self.estado_dropdown.get()]

            data_pagamento = None
            if self.data_pagamento_picker.get():
                data_pagamento = self.data_pagamento_picker.get_date()

            nota = self.nota_entry.get("1.0", "end-1c").strip() or None

            # Create or update
            if self.despesa:
                sucesso, erro = self.manager.atualizar(
                    self.despesa.id,
                    tipo=tipo,
                    data=data_despesa,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    estado=estado,
                    data_pagamento=data_pagamento,
                    nota=nota
                )
                msg = "Despesa atualizada com sucesso!"
            else:
                sucesso, despesa, erro = self.manager.criar(
                    tipo=tipo,
                    data=data_despesa,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    estado=estado,
                    data_pagamento=data_pagamento,
                    nota=nota
                )
                msg = f"Despesa {despesa.numero} criada com sucesso!"

            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro ao guardar: {erro}")

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
