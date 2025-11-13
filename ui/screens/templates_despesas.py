# -*- coding: utf-8 -*-
"""
Screen de Templates de Despesas Recorrentes
Gestão de templates para gerar despesas automáticas mensais
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from decimal import Decimal
import tkinter.messagebox as messagebox

from logic.despesa_templates import DespesaTemplatesManager
from database.models import TipoDespesa
from ui.components.data_table_v2 import DataTableV2


class TemplatesDespesasScreen(ctk.CTkFrame):
    """
    Tela de gestão de Templates de Despesas Recorrentes (CRUD completo)
    """

    def __init__(self, parent, db_session: Session, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = DespesaTemplatesManager(db_session)

        self.create_layout()
        self.carregar_templates()

    def create_layout(self):
        """Create screen layout"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        ctk.CTkLabel(
            header_frame,
            text="📝 Templates de Despesas Recorrentes",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")

        # Buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Atualizar",
            command=self.carregar_templates,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=5)

        nova_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Novo Template",
            command=self.abrir_formulario,
            width=150,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#64B5F6", "#1565C0")
        )
        nova_btn.pack(side="left", padx=5)

        # Info text
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(
            info_frame,
            text="💡 Templates não são despesas reais. São moldes para gerar despesas automáticas mensais.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(anchor="w")

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

        # Delete button
        self.delete_btn = ctk.CTkButton(
            self.selection_frame,
            text="🗑️ Apagar Selecionados",
            command=self.apagar_selecionados,
            width=180, height=35,
            fg_color=("#F44336", "#C62828"),
            hover_color=("#E57373", "#B71C1C")
        )

        # Table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Data table
        columns = [
            {"key": "numero", "label": "Número", "width": 120},
            {"key": "tipo", "label": "Tipo", "width": 120},
            {"key": "descricao", "label": "Descrição", "width": 250},
            {"key": "valor_display", "label": "Valor", "width": 100},
            {"key": "dia_mes", "label": "Dia", "width": 60},
            {"key": "credor_nome", "label": "Credor", "width": 150},
        ]

        self.table = DataTableV2(
            table_frame,
            columns=columns,
            on_row_double_click=self.editar_template,
            on_selection_change=self.on_selection_change
        )
        self.table.pack(fill="both", expand=True)

    def carregar_templates(self):
        """Load templates into table"""
        templates = self.manager.listar_todos()
        data = [self.template_to_dict(t) for t in templates]
        self.table.set_data(data)

    def template_to_dict(self, template) -> dict:
        """Convert template to dict for table display"""
        d = template.to_dict()
        d['_template'] = template  # Store original object
        d['tipo'] = self.format_tipo(template.tipo)
        d['valor_display'] = f"€{float(template.valor_com_iva):.2f}"
        d['credor_nome'] = template.credor.nome if template.credor else "-"
        return d

    def format_tipo(self, tipo: TipoDespesa) -> str:
        """Format tipo for display"""
        tipo_map = {
            TipoDespesa.FIXA_MENSAL: "Fixa Mensal",
            TipoDespesa.PESSOAL_BRUNO: "Pessoal BA",
            TipoDespesa.PESSOAL_RAFAEL: "Pessoal RR",
            TipoDespesa.EQUIPAMENTO: "Equipamento",
            TipoDespesa.PROJETO: "Projeto"
        }
        return tipo_map.get(tipo, tipo.value)

    def abrir_formulario(self, template=None):
        """Open form dialog"""
        FormularioTemplateDialog(self, self.manager, template, self.carregar_templates)

    def editar_template(self, data: dict):
        """Edit template (triggered by double-click)"""
        template = data.get('_template')
        if template:
            self.abrir_formulario(template)

    def apagar_template(self, data: dict):
        """Delete template"""
        template = data.get('_template')
        if not template:
            return

        resposta = messagebox.askyesno(
            "Confirmar",
            f"Apagar template {template.numero}?\n\n"
            f"As despesas já geradas mantêm-se, mas não serão geradas novas."
        )

        if resposta:
            sucesso, erro = self.manager.apagar(template.id)
            if sucesso:
                messagebox.showinfo("Sucesso", "Template apagado com sucesso!")
                self.carregar_templates()
            else:
                messagebox.showerror("Erro", f"Erro ao apagar: {erro}")

    def apagar_selecionados(self):
        """Apagar templates selecionados"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) == 0:
            return

        # Confirmar ação
        resposta = messagebox.askyesno(
            "Confirmar",
            f"Apagar {len(selected_data)} template(s) selecionado(s)?\n\n"
            f"As despesas já geradas mantêm-se, mas não serão geradas novas."
        )

        if resposta:
            sucesso_count = 0
            erros = []

            for item in selected_data:
                template = item.get('_template')
                if template:
                    sucesso, erro = self.manager.apagar(template.id)
                    if sucesso:
                        sucesso_count += 1
                    else:
                        erros.append(f"{template.numero}: {erro}")

            # Mostrar resultado
            if sucesso_count > 0:
                msg = f"✅ {sucesso_count} template(s) apagado(s) com sucesso!"
                if erros:
                    msg += f"\n\n⚠️ {len(erros)} erro(s):\n" + "\n".join(erros[:3])
                messagebox.showinfo("Resultado", msg)
            else:
                messagebox.showerror("Erro", "Nenhum template foi apagado:\n" + "\n".join(erros[:5]))

            self.carregar_templates()
            self.table.clear_selection()

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

            # Show delete button
            self.delete_btn.pack(side="left", padx=5)
        else:
            # Hide entire selection frame when nothing is selected
            self.selection_frame.pack_forget()

    def cancelar_selecao(self):
        """Cancel selection"""
        self.table.clear_selection()


class FormularioTemplateDialog(ctk.CTkToplevel):
    """
    Dialog para criar/editar templates de despesas recorrentes
    """

    def __init__(self, parent, manager: DespesaTemplatesManager, template=None, callback=None):
        super().__init__(parent)

        self.manager = manager
        self.template = template
        self.callback = callback
        self.parent = parent

        self.title("Novo Template" if not template else f"Editar Template {template.numero}")
        self.geometry("600x700")

        self.transient(parent)
        self.grab_set()

        self.create_form()

        if template:
            self.carregar_dados()

    def create_form(self):
        """Create form fields"""

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

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

        for label, value in tipos:
            ctk.CTkRadioButton(
                tipo_frame,
                text=label,
                variable=self.tipo_var,
                value=value
            ).pack(side="left", padx=(0, 15))

        # Dia do Mês
        ctk.CTkLabel(scroll, text="Dia do Mês (1-31) *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        dia_container = ctk.CTkFrame(scroll, fg_color="transparent")
        dia_container.pack(fill="x", pady=(0, 10))

        self.dia_mes_entry = ctk.CTkEntry(dia_container, width=80, placeholder_text="27")
        self.dia_mes_entry.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            dia_container,
            text="(Ex: 27 para gerar sempre no dia 27 do mês)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(side="left")

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
            text="Guardar",
            command=self.guardar,
            width=120,
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#64B5F6", "#1565C0")
        )
        save_btn.pack(side="right", padx=5)

    def carregar_dados(self):
        """Load template data into form"""
        t = self.template

        self.tipo_var.set(t.tipo.value)
        self.dia_mes_entry.insert(0, str(t.dia_mes))

        if t.credor:
            credor_str = f"{t.credor.numero} - {t.credor.nome}"
            self.credor_dropdown.set(credor_str)

        if t.projeto:
            projeto_str = f"{t.projeto.numero} - {t.projeto.descricao[:30]}"
            self.projeto_dropdown.set(projeto_str)

        self.descricao_entry.insert("1.0", t.descricao)
        self.valor_sem_iva_entry.insert(0, str(t.valor_sem_iva))
        self.valor_com_iva_entry.insert(0, str(t.valor_com_iva))

        if t.nota:
            self.nota_entry.insert("1.0", t.nota)

    def guardar(self):
        """Save template"""
        try:
            # Get values
            tipo_str = self.tipo_var.get()
            tipo = TipoDespesa[tipo_str]

            dia_mes_str = self.dia_mes_entry.get().strip()
            if not dia_mes_str:
                messagebox.showerror("Erro", "Dia do mês é obrigatório")
                return
            try:
                dia_mes = int(dia_mes_str)
                if dia_mes < 1 or dia_mes > 31:
                    messagebox.showerror("Erro", "Dia do mês deve estar entre 1 e 31")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Dia do mês deve ser um número")
                return

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

            nota = self.nota_entry.get("1.0", "end-1c").strip() or None

            # Create or update
            if self.template:
                sucesso, erro = self.manager.atualizar(
                    self.template.id,
                    tipo=tipo,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    dia_mes=dia_mes,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    nota=nota
                )
                msg = "Template atualizado com sucesso!"
            else:
                sucesso, template, erro = self.manager.criar(
                    tipo=tipo,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    dia_mes=dia_mes,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    nota=nota
                )
                msg = f"Template {template.numero} criado com sucesso!"

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
