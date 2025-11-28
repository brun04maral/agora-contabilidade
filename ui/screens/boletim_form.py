# -*- coding: utf-8 -*-
"""
Tela de Formulário de Boletim - Migrado para BaseForm com tabs

Usa BaseForm template com layout customizado de tabs:
- Tab 1: Dados Gerais (campos principais do boletim)
- Tab 2: Deslocações (tabela de linhas com add/edit/delete)

Migrado para BaseForm em 2025-11-28.
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, time
import tkinter.messagebox as messagebox
from typing import Optional, List, Dict, Any

from logic.boletins import BoletinsManager
from logic.boletim_linhas import BoletimLinhasManager
from logic.valores_referencia import ValoresReferenciaManager
from logic.projetos import ProjetosManager
from database.models.boletim import Socio
from database.models.boletim_linha import TipoDeslocacao
from ui.components.base_form import BaseForm
from ui.components.data_table_v2 import DataTableV2
from ui.components.date_picker_dropdown import DatePickerDropdown
from utils.base_dialogs import BaseDialogLarge
from assets.resources import BOLETINS, get_icon


class BoletimFormScreen(BaseForm):
    """
    Screen para criar/editar boletins
    Herda de BaseForm para layout consistente com tabs customizadas.

    Navegação via MainWindow.show_screen("boletim_form", boletim_id=None/ID)
    """

    def __init__(self, parent, db_session: Session, boletim_id: Optional[int] = None, **kwargs):
        self.db_session = db_session
        self.boletim_id = boletim_id
        self.is_create = (boletim_id is None)

        # Managers
        self.boletins_manager = BoletinsManager(db_session)
        self.linhas_manager = BoletimLinhasManager(db_session)
        self.valores_manager = ValoresReferenciaManager(db_session)
        self.projetos_manager = ProjetosManager(db_session)

        # Estado
        self.boletim = None

        # Load data if editing
        initial_data = {}
        if boletim_id:
            self.boletim = self.boletins_manager.obter_por_id(boletim_id)
            if self.boletim:
                b = self.boletim
                initial_data = {
                    'socio': b.socio.value,
                    'mes': str(b.mes) if b.mes else str(date.today().month),
                    'ano': str(b.ano) if b.ano else str(date.today().year),
                    'data_emissao': b.data_emissao if b.data_emissao else date.today(),
                    'descricao': b.descricao or '',
                    'nota': b.nota or '',
                }
        else:
            # Defaults for CREATE mode
            initial_data = {
                'socio': Socio.BRUNO.value,
                'mes': str(date.today().month),
                'ano': str(date.today().year),
                'data_emissao': date.today(),
                'descricao': '',
                'nota': '',
            }

        # Initialize BaseForm (NO columns - we'll use tabs)
        super().__init__(
            parent,
            db_session=db_session,
            initial_data=initial_data,
            on_cancel_callback=self._voltar_para_lista,
            **kwargs
        )

        # Create tabs AFTER super().__init__()
        self._create_tabs()

        # Load linhas if editing
        if self.boletim:
            self._carregar_linhas()
            self._atualizar_valores_referencia_display()
            self._atualizar_totais_display()
        else:
            self._sugerir_valores_referencia()

    # ========== BaseForm REQUIRED methods ==========

    def get_form_title(self) -> str:
        if self.is_create:
            return "Novo Boletim"
        elif self.boletim:
            return f"Editar Boletim {self.boletim.numero}"
        else:
            return "Editar Boletim"

    def get_form_icon(self):
        return get_icon(BOLETINS, size=(28, 28))

    def get_fields_config(self) -> List[Dict[str, Any]]:
        """
        NOTA: Este form usa tabs customizadas, não fields padrão.
        Retornamos lista vazia porque sobrescrevemos a criação de widgets.
        """
        return []

    def on_save(self, data: dict) -> bool:
        """
        Guarda o boletim (campos principais apenas).
        As linhas são geridas separadamente via LinhaDialog.
        """
        try:
            # Get values from widgets (não podemos usar 'data' porque não temos fields padrão)
            socio_str = self.socio_dropdown.get()
            mes = int(self.mes_dropdown.get())
            ano_str = self.ano_entry.get().strip()
            data_emissao = self.data_emissao_picker.get_date()
            descricao = self.descricao_entry.get("1.0", "end-1c").strip() or None
            nota = self.nota_entry.get("1.0", "end-1c").strip() or None

            # Validations
            if not ano_str:
                messagebox.showerror("Erro", "Ano é obrigatório")
                return False

            ano = int(ano_str)

            if not data_emissao:
                messagebox.showerror("Erro", "Data de emissão é obrigatória")
                return False

            socio = Socio(socio_str)

            # Get valores de referência
            val_nacional, val_estrangeiro, val_km = self.valores_manager.obter_ou_default(ano)

            if self.boletim:
                # Update existing
                b = self.boletim
                b.socio = socio
                b.mes = mes
                b.ano = ano
                b.data_emissao = data_emissao
                b.descricao = descricao
                b.nota = nota

                # Update valores de referência
                b.val_dia_nacional = val_nacional
                b.val_dia_estrangeiro = val_estrangeiro
                b.val_km = val_km

                # Recalculate totals
                self.linhas_manager.recalcular_totais_boletim(b.id)

                self.db_session.commit()
                self.db_session.refresh(b)

                messagebox.showinfo("Sucesso", f"Boletim {b.numero} atualizado com sucesso!")
                return True

            else:
                # Create new
                sucesso, novo_boletim, erro = self.boletins_manager.criar(
                    socio=socio,
                    mes=mes,
                    ano=ano,
                    data_emissao=data_emissao,
                    val_dia_nacional=val_nacional,
                    val_dia_estrangeiro=val_estrangeiro,
                    val_km=val_km,
                    descricao=descricao,
                    nota=nota
                )

                if sucesso:
                    # Switch to edit mode
                    self.boletim = novo_boletim
                    self.boletim_id = novo_boletim.id
                    self.is_create = False

                    # Update title
                    self.title_label.configure(text=f"Editar Boletim {novo_boletim.numero}")

                    messagebox.showinfo("Sucesso", f"Boletim {novo_boletim.numero} criado! Agora pode adicionar deslocações.")
                    return False  # Don't close form, allow adding linhas

                else:
                    messagebox.showerror("Erro", erro or "Erro ao criar boletim")
                    return False

        except ValueError as e:
            messagebox.showerror("Erro", f"Valores inválidos: {str(e)}")
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
            return False

    # ========== CUSTOM LAYOUT ==========

    def _create_tabs(self):
        """Cria estrutura de tabs customizada (sobrescreve layout padrão do BaseForm)"""
        # Create tabview
        self.tabview = ctk.CTkTabview(self, height=600)
        self.tabview.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Create tabs
        self.tab_dados_gerais = self.tabview.add("Dados Gerais")
        self.tab_deslocacoes = self.tabview.add("Deslocações")

        # Populate tabs
        self._create_tab_dados_gerais()
        self._create_tab_deslocacoes()

    def _create_tab_dados_gerais(self):
        """Cria conteúdo da tab Dados Gerais"""
        parent = self.tab_dados_gerais

        # Container com scroll
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Row 1: Sócio + Mês + Ano
        row1 = ctk.CTkFrame(scroll, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 15))
        row1.grid_columnconfigure((0, 1, 2), weight=1)

        # Sócio
        ctk.CTkLabel(row1, text="Sócio *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 10))
        self.socio_dropdown = ctk.CTkOptionMenu(
            row1,
            values=[socio.value for socio in Socio],
            height=35,
            command=self._socio_mudou
        )
        self.socio_dropdown.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(8, 0))
        self.socio_dropdown.set(self.initial_data.get('socio', Socio.BRUNO.value))

        # Mês
        ctk.CTkLabel(row1, text="Mês *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=1, sticky="w", padx=(0, 10))
        self.mes_dropdown = ctk.CTkOptionMenu(
            row1,
            values=[str(i) for i in range(1, 13)],
            height=35
        )
        self.mes_dropdown.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(8, 0))
        self.mes_dropdown.set(self.initial_data.get('mes', str(date.today().month)))

        # Ano
        ctk.CTkLabel(row1, text="Ano *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=2, sticky="w")
        self.ano_entry = ctk.CTkEntry(row1, height=35)
        self.ano_entry.grid(row=1, column=2, sticky="ew", pady=(8, 0))
        self.ano_entry.insert(0, self.initial_data.get('ano', str(date.today().year)))
        self.ano_entry.bind("<FocusOut>", lambda e: self._ano_mudou())

        # Data Emissão
        ctk.CTkLabel(scroll, text="Data de Emissão *", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(15, 8))
        self.data_emissao_picker = DatePickerDropdown(
            scroll,
            default_date=self.initial_data.get('data_emissao', date.today())
        )
        self.data_emissao_picker.pack(fill="x", pady=(0, 18))

        # Valores de Referência (read-only display)
        valores_label_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        valores_label_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            valores_label_frame,
            text="📊 Valores de Referência:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        valores_frame = ctk.CTkFrame(valores_label_frame, fg_color="transparent")
        valores_frame.pack(fill="x")

        self.val_nacional_label = ctk.CTkLabel(
            valores_frame, text="Dia Nacional: €0.00",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.val_nacional_label.pack(side="left", padx=(0, 20))

        self.val_estrangeiro_label = ctk.CTkLabel(
            valores_frame, text="Dia Estrangeiro: €0.00",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.val_estrangeiro_label.pack(side="left", padx=(0, 20))

        self.val_km_label = ctk.CTkLabel(
            valores_frame, text="Km: €0.00",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.val_km_label.pack(side="left")

        # Totais Calculados (read-only display)
        totais_label_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        totais_label_frame.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(
            totais_label_frame,
            text="💰 Totais Calculados:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        totais_frame = ctk.CTkFrame(totais_label_frame, fg_color="transparent")
        totais_frame.pack(fill="x")

        self.total_nacional_label = ctk.CTkLabel(
            totais_frame, text="Ajudas Nacionais: €0.00",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.total_nacional_label.pack(side="left", padx=(0, 15))

        self.total_estrangeiro_label = ctk.CTkLabel(
            totais_frame, text="Ajudas Estrangeiro: €0.00",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.total_estrangeiro_label.pack(side="left", padx=(0, 15))

        self.total_kms_label = ctk.CTkLabel(
            totais_frame, text="Kms: €0.00",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.total_kms_label.pack(side="left", padx=(0, 15))

        self.valor_total_label = ctk.CTkLabel(
            totais_frame, text="TOTAL: €0.00",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#2196F3", "#64B5F6")
        )
        self.valor_total_label.pack(side="left")

        # Descrição
        ctk.CTkLabel(scroll, text="Descrição", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(15, 8))
        self.descricao_entry = ctk.CTkTextbox(scroll, height=60)
        self.descricao_entry.pack(fill="x", pady=(0, 18))
        if self.initial_data.get('descricao'):
            self.descricao_entry.insert("1.0", self.initial_data['descricao'])

        # Nota
        ctk.CTkLabel(scroll, text="Nota", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(0, 8))
        self.nota_entry = ctk.CTkTextbox(scroll, height=60)
        self.nota_entry.pack(fill="x", pady=(0, 10))
        if self.initial_data.get('nota'):
            self.nota_entry.insert("1.0", self.initial_data['nota'])

    def _create_tab_deslocacoes(self):
        """Cria conteúdo da tab Deslocações"""
        parent = self.tab_deslocacoes

        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header com botão adicionar
        linhas_header = ctk.CTkFrame(container, fg_color="transparent")
        linhas_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            linhas_header,
            text="🗺️ Deslocações",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")

        add_linha_btn = ctk.CTkButton(
            linhas_header,
            text="➕ Adicionar Deslocação",
            command=self._adicionar_linha,
            width=180,
            height=35,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        add_linha_btn.pack(side="right")

        # Tabela de linhas
        columns = [
            {"key": "ordem", "label": "#", "width": 50},
            {"key": "projeto", "label": "Projeto", "width": 120},
            {"key": "servico", "label": "Serviço", "width": 200},
            {"key": "localidade", "label": "Localidade", "width": 120},
            {"key": "tipo", "label": "Tipo", "width": 100},
            {"key": "dias", "label": "Dias", "width": 80},
            {"key": "kms", "label": "Kms", "width": 80},
        ]

        self.linhas_table = DataTableV2(
            container,
            columns=columns,
            on_row_double_click=self._editar_linha,
            height=300
        )
        self.linhas_table.pack(fill="both", expand=True)

        # Botão apagar linha
        delete_linha_btn = ctk.CTkButton(
            container,
            text="🗑️ Apagar Linha Selecionada",
            command=self._apagar_linha,
            width=220,
            height=35,
            fg_color=("#F44336", "#C62828"),
            hover_color=("#E57373", "#B71C1C")
        )
        delete_linha_btn.pack(side="right", pady=(10, 0))

        # Botão duplicar (só quando edita)
        if self.boletim_id:
            duplicate_btn = ctk.CTkButton(
                container,
                text="📋 Duplicar Boletim",
                command=self._duplicar_boletim,
                width=180,
                height=35,
                fg_color=("#2196F3", "#1976D2"),
                hover_color=("#64B5F6", "#1565C0")
            )
            duplicate_btn.pack(side="right", padx=(0, 10), pady=(10, 0))

    # ========== EVENT HANDLERS ==========

    def _socio_mudou(self, *args):
        """Handle socio change - update valores de referência"""
        self._sugerir_valores_referencia()

    def _ano_mudou(self):
        """Handle ano change - update valores de referência"""
        self._sugerir_valores_referencia()

    def _sugerir_valores_referencia(self):
        """Fetch and display valores de referência based on ano"""
        try:
            ano_str = self.ano_entry.get().strip()
            if not ano_str:
                return

            ano = int(ano_str)
            val_nacional, val_estrangeiro, val_km = self.valores_manager.obter_ou_default(ano)

            self._atualizar_valores_referencia_display(val_nacional, val_estrangeiro, val_km)

        except ValueError:
            pass

    def _atualizar_valores_referencia_display(self, val_nacional=None, val_estrangeiro=None, val_km=None):
        """Update valores de referência display"""
        if val_nacional is None and self.boletim:
            val_nacional = self.boletim.val_dia_nacional
            val_estrangeiro = self.boletim.val_dia_estrangeiro
            val_km = self.boletim.val_km

        if val_nacional:
            self.val_nacional_label.configure(text=f"Dia Nacional: €{float(val_nacional):.2f}")
        if val_estrangeiro:
            self.val_estrangeiro_label.configure(text=f"Dia Estrangeiro: €{float(val_estrangeiro):.2f}")
        if val_km:
            self.val_km_label.configure(text=f"Km: €{float(val_km):.2f}")

    def _atualizar_totais_display(self):
        """Update totais display from boletim"""
        if not self.boletim:
            return

        b = self.boletim

        self.total_nacional_label.configure(
            text=f"Ajudas Nacionais: €{float(b.total_ajudas_nacionais):.2f}"
        )
        self.total_estrangeiro_label.configure(
            text=f"Ajudas Estrangeiro: €{float(b.total_ajudas_estrangeiro):.2f}"
        )
        self.total_kms_label.configure(
            text=f"Kms: €{float(b.total_kms):.2f}"
        )
        self.valor_total_label.configure(
            text=f"TOTAL: €{float(b.valor_total):.2f}"
        )

    def _adicionar_linha(self):
        """Open dialog to add new linha"""
        if not self.boletim:
            messagebox.showerror("Erro", "Grave o boletim primeiro antes de adicionar deslocações.")
            return

        dialog = LinhaDialog(self, self.db_session, self.boletim.id)
        dialog.wait_window()

        # Reload
        self._carregar_linhas()
        self._refresh_boletim()

    def _editar_linha(self, row_data):
        """Edit linha (double-click handler)"""
        linha = row_data.get('_linha')
        if not linha:
            return

        dialog = LinhaDialog(self, self.db_session, self.boletim.id, linha=linha)
        dialog.wait_window()

        # Reload
        self._carregar_linhas()
        self._refresh_boletim()

    def _apagar_linha(self):
        """Delete selected linha"""
        selected_data = self.linhas_table.get_selected_data()
        if len(selected_data) == 0:
            messagebox.showinfo("Info", "Selecione uma deslocação para apagar.")
            return

        linha = selected_data[0].get('_linha')
        if not linha:
            return

        resposta = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja apagar a deslocação #{linha.ordem}?"
        )

        if resposta:
            sucesso, erro = self.linhas_manager.eliminar(linha.id)
            if sucesso:
                self._carregar_linhas()
                self._refresh_boletim()
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar linha")

    def _refresh_boletim(self):
        """Refresh boletim from database and update totais display"""
        if self.boletim:
            self.db_session.refresh(self.boletim)
            self._atualizar_totais_display()

    def _carregar_linhas(self):
        """Load boletim linhas into table"""
        if not self.boletim:
            self.linhas_table.set_data([])
            return

        linhas = self.linhas_manager.listar_por_boletim(self.boletim.id)
        data = [self._linha_to_dict(linha) for linha in linhas]
        self.linhas_table.set_data(data)

    def _linha_to_dict(self, linha) -> dict:
        """Convert linha to dict for table display"""
        projeto_str = "-"
        if linha.projeto_id and linha.projeto:
            projeto_str = linha.projeto.numero

        return {
            'id': linha.id,
            'ordem': str(linha.ordem),
            'projeto': projeto_str,
            'servico': linha.servico[:30] + "..." if len(linha.servico) > 30 else linha.servico,
            'localidade': linha.localidade or "-",
            'tipo': linha.tipo.value,
            'dias': f"{float(linha.dias):.1f}",
            'kms': str(linha.kms),
            '_linha': linha
        }

    def _duplicar_boletim(self):
        """Duplica o boletim atual"""
        try:
            if not self.boletim:
                messagebox.showerror("Erro", "Nenhum boletim para duplicar")
                return

            resposta = messagebox.askyesno(
                "Duplicar Boletim",
                f"Duplicar boletim {self.boletim.numero}?\n\n"
                f"Todas as deslocações serão copiadas."
            )

            if not resposta:
                return

            sucesso, novo_boletim, erro = self.boletins_manager.duplicar_boletim(self.boletim.id)

            if sucesso:
                # Navigate to the new boletim
                main_window = self.master.master
                if hasattr(main_window, 'show_screen'):
                    main_window.show_screen("boletim_form", boletim_id=novo_boletim.id)
            else:
                messagebox.showerror("Erro", erro or "Erro ao duplicar boletim")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao duplicar boletim: {str(e)}")

    def _voltar_para_lista(self):
        """Navega de volta para lista de boletins"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("boletins")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")


# ========== DIALOG FOR LINHA ADD/EDIT ==========

class LinhaDialog(BaseDialogLarge):
    """
    Dialog para adicionar/editar linha de deslocação
    """

    def __init__(self, parent, db_session: Session, boletim_id: int, linha=None):
        self.db_session = db_session
        self.boletim_id = boletim_id
        self.linha = linha
        self.linhas_manager = BoletimLinhasManager(db_session)
        self.projetos_manager = ProjetosManager(db_session)

        title = "Editar Deslocação" if linha else "Nova Deslocação"
        super().__init__(parent, title=title)

        self.create_layout()

        if linha:
            self.preencher_dados(linha)

    def create_layout(self):
        """Create dialog layout"""
        scroll = self.main_frame

        # Title
        ctk.CTkLabel(
            scroll,
            text="✏️ Editar Deslocação" if self.linha else "➕ Nova Deslocação",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 20))

        # Projeto
        ctk.CTkLabel(scroll, text="Projeto (opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))

        projetos = self.projetos_manager.listar_todos()
        projeto_options = ["- Nenhum -"] + [f"{p.numero} - {p.descricao[:50]}" for p in projetos]

        self.projeto_dropdown = ctk.CTkOptionMenu(
            scroll,
            values=projeto_options,
            height=35,
            command=self.projeto_selecionado
        )
        self.projeto_dropdown.pack(fill="x", pady=(0, 10))

        self.projeto_map = {f"{p.numero} - {p.descricao[:50]}": p.id for p in projetos}
        self.projetos_dict = {p.id: p for p in projetos}

        # Serviço
        ctk.CTkLabel(scroll, text="Serviço/Descrição *:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.servico_entry = ctk.CTkTextbox(scroll, height=80)
        self.servico_entry.pack(fill="x", pady=(0, 10))

        # Localidade
        ctk.CTkLabel(scroll, text="Localidade:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.localidade_entry = ctk.CTkEntry(scroll, height=35)
        self.localidade_entry.pack(fill="x", pady=(0, 10))

        # Tipo
        ctk.CTkLabel(scroll, text="Tipo de Deslocação *:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.tipo_dropdown = ctk.CTkOptionMenu(
            scroll,
            values=[tipo.value for tipo in TipoDeslocacao],
            height=35
        )
        self.tipo_dropdown.pack(fill="x", pady=(0, 10))

        # Dias
        ctk.CTkLabel(scroll, text="Dias *:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.dias_entry = ctk.CTkEntry(scroll, height=35)
        self.dias_entry.pack(fill="x", pady=(0, 10))
        self.dias_entry.insert(0, "0")

        # Kms
        ctk.CTkLabel(scroll, text="Quilómetros *:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.kms_entry = ctk.CTkEntry(scroll, height=35)
        self.kms_entry.pack(fill="x", pady=(0, 10))
        self.kms_entry.insert(0, "0")

        # Data Início
        ctk.CTkLabel(scroll, text="Data Início (opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.data_inicio_picker = DatePickerDropdown(scroll, default_date=None, placeholder="Selecionar data...")
        self.data_inicio_picker.pack(fill="x", pady=(0, 10))

        # Hora Início
        ctk.CTkLabel(scroll, text="Hora Início (HH:MM, opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.hora_inicio_entry = ctk.CTkEntry(scroll, height=35, placeholder_text="09:00")
        self.hora_inicio_entry.pack(fill="x", pady=(0, 10))

        # Data Fim
        ctk.CTkLabel(scroll, text="Data Fim (opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.data_fim_picker = DatePickerDropdown(scroll, default_date=None, placeholder="Selecionar data...")
        self.data_fim_picker.pack(fill="x", pady=(0, 10))

        # Hora Fim
        ctk.CTkLabel(scroll, text="Hora Fim (HH:MM, opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.hora_fim_entry = ctk.CTkEntry(scroll, height=35, placeholder_text="18:00")
        self.hora_fim_entry.pack(fill="x", pady=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=self.destroy,
            width=140,
            height=40,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Gravar",
            command=self.gravar,
            width=140,
            height=40,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        save_btn.pack(side="left")

    def projeto_selecionado(self, projeto_str: str):
        """Auto-preenche quando projeto é selecionado"""
        if projeto_str == "- Nenhum -":
            return

        projeto_id = self.projeto_map.get(projeto_str)
        if not projeto_id:
            return

        projeto = self.projetos_dict.get(projeto_id)
        if not projeto:
            return

        # Auto-preencher serviço se vazio
        conteudo_atual = self.servico_entry.get("1.0", "end-1c").strip()
        if not conteudo_atual:
            self.servico_entry.delete("1.0", "end")
            self.servico_entry.insert("1.0", projeto.descricao)

        # Auto-preencher datas se vazias
        if projeto.data_inicio and self.data_inicio_picker.get_date() is None:
            self.data_inicio_picker.set_date(projeto.data_inicio)

        if projeto.data_fim and self.data_fim_picker.get_date() is None:
            self.data_fim_picker.set_date(projeto.data_fim)

    def preencher_dados(self, linha):
        """Fill form with existing linha data"""
        if linha.projeto_id and linha.projeto:
            projeto_key = f"{linha.projeto.numero} - {linha.projeto.descricao[:50]}"
            self.projeto_dropdown.set(projeto_key)

        self.servico_entry.insert("1.0", linha.servico)

        if linha.localidade:
            self.localidade_entry.insert(0, linha.localidade)

        self.tipo_dropdown.set(linha.tipo.value)

        self.dias_entry.delete(0, "end")
        self.dias_entry.insert(0, str(float(linha.dias)))

        self.kms_entry.delete(0, "end")
        self.kms_entry.insert(0, str(linha.kms))

        if linha.data_inicio:
            self.data_inicio_picker.set_date(linha.data_inicio)
        if linha.hora_inicio:
            self.hora_inicio_entry.insert(0, linha.hora_inicio.strftime("%H:%M"))

        if linha.data_fim:
            self.data_fim_picker.set_date(linha.data_fim)
        if linha.hora_fim:
            self.hora_fim_entry.insert(0, linha.hora_fim.strftime("%H:%M"))

    def gravar(self):
        """Save linha"""
        try:
            servico = self.servico_entry.get("1.0", "end-1c").strip()
            localidade = self.localidade_entry.get().strip() or None
            tipo_str = self.tipo_dropdown.get()
            dias_str = self.dias_entry.get().strip()
            kms_str = self.kms_entry.get().strip()

            if not servico:
                messagebox.showerror("Erro", "Serviço é obrigatório")
                return

            if not dias_str or not kms_str:
                messagebox.showerror("Erro", "Dias e Kms são obrigatórios")
                return

            tipo = TipoDeslocacao(tipo_str)
            dias = Decimal(dias_str)
            kms = int(kms_str)

            projeto_id = None
            projeto_sel = self.projeto_dropdown.get()
            if projeto_sel != "- Nenhum -":
                projeto_id = self.projeto_map.get(projeto_sel)

            data_inicio = self.data_inicio_picker.get_date()
            data_fim = self.data_fim_picker.get_date()

            hora_inicio = None
            hora_fim = None

            hora_inicio_str = self.hora_inicio_entry.get().strip()
            if hora_inicio_str:
                try:
                    h, m = map(int, hora_inicio_str.split(":"))
                    hora_inicio = time(h, m)
                except:
                    messagebox.showerror("Erro", "Hora início inválida (use HH:MM)")
                    return

            hora_fim_str = self.hora_fim_entry.get().strip()
            if hora_fim_str:
                try:
                    h, m = map(int, hora_fim_str.split(":"))
                    hora_fim = time(h, m)
                except:
                    messagebox.showerror("Erro", "Hora fim inválida (use HH:MM)")
                    return

            if self.linha:
                sucesso, _, erro = self.linhas_manager.atualizar(
                    linha_id=self.linha.id,
                    servico=servico,
                    tipo=tipo,
                    dias=dias,
                    kms=kms,
                    projeto_id=projeto_id,
                    localidade=localidade,
                    data_inicio=data_inicio,
                    hora_inicio=hora_inicio,
                    data_fim=data_fim,
                    hora_fim=hora_fim
                )
            else:
                sucesso, _, erro = self.linhas_manager.criar(
                    boletim_id=self.boletim_id,
                    servico=servico,
                    tipo=tipo,
                    dias=dias,
                    kms=kms,
                    projeto_id=projeto_id,
                    localidade=localidade,
                    data_inicio=data_inicio,
                    hora_inicio=hora_inicio,
                    data_fim=data_fim,
                    hora_fim=hora_fim
                )

            if sucesso:
                self.destroy()
            else:
                messagebox.showerror("Erro", erro or "Erro ao gravar")

        except ValueError as e:
            messagebox.showerror("Erro", f"Valores inválidos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
