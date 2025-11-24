# -*- coding: utf-8 -*-
"""
Tela de Formulário de Boletim - Screen dedicado para criar/editar boletins
Segue mesmo padrão de ui/screens/projeto_form.py
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, time
import tkinter.messagebox as messagebox
from typing import Optional

from logic.boletins import BoletinsManager
from logic.boletim_linhas import BoletimLinhasManager
from logic.valores_referencia import ValoresReferenciaManager
from logic.projetos import ProjetosManager
from database.models.boletim import Socio
from database.models.boletim_linha import TipoDeslocacao
from ui.components.data_table_v2 import DataTableV2
from ui.components.date_picker_dropdown import DatePickerDropdown
from utils.base_dialogs import BaseDialogLarge


class BoletimFormScreen(ctk.CTkFrame):
    """
    Screen para criar/editar boletins

    Navegação via MainWindow.show_screen("boletim_form", boletim_id=None/ID)
    """

    def __init__(self, parent, db_session: Session, boletim_id: Optional[int] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.boletim_id = boletim_id

        self.boletins_manager = BoletinsManager(db_session)
        self.linhas_manager = BoletimLinhasManager(db_session)
        self.valores_manager = ValoresReferenciaManager(db_session)
        self.projetos_manager = ProjetosManager(db_session)

        # Estado
        self.boletim = None

        # Configure
        self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.create_widgets()

        # Load data se edição
        if boletim_id:
            self.carregar_boletim()
        else:
            # New boletim - suggest default values
            self.sugerir_valores_referencia()

    def create_widgets(self):
        """Cria widgets da screen"""
        # Container principal com scroll
        main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_container.grid_columnconfigure(0, weight=1)

        # ========================================
        # 1. HEADER
        # ========================================
        self.create_header(main_container)

        # ========================================
        # 2. CAMPOS DO BOLETIM
        # ========================================
        self.create_fields(main_container)

        # ========================================
        # 3. SECÇÃO DE LINHAS (deslocações)
        # ========================================
        self.create_linhas_section(main_container)

        # ========================================
        # 4. FOOTER COM BOTÕES
        # ========================================
        self.create_footer(main_container)

    def create_header(self, parent):
        """Cria header com botão voltar e título"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        header_frame.grid_columnconfigure(1, weight=1)

        # Botão voltar
        voltar_btn = ctk.CTkButton(
            header_frame,
            text="⬅️ Voltar",
            command=self.voltar,
            width=100,
            height=35,
            fg_color="gray",
            hover_color="#5a5a5a"
        )
        voltar_btn.grid(row=0, column=0, sticky="w", padx=(0, 20))

        # Título
        titulo = "Novo Boletim" if not self.boletim_id else "Editar Boletim"
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=titulo,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=1, sticky="w")

    def create_fields(self, parent):
        """Cria campos do formulário"""
        fields_frame = ctk.CTkFrame(parent, fg_color="transparent")
        fields_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        fields_frame.grid_columnconfigure(0, weight=1)

        # Row 1: Sócio + Mês + Ano
        row1 = ctk.CTkFrame(fields_frame, fg_color="transparent")
        row1.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        row1.grid_columnconfigure((0, 1, 2), weight=1)

        # Sócio
        ctk.CTkLabel(row1, text="Sócio *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 10))
        self.socio_dropdown = ctk.CTkOptionMenu(
            row1,
            values=[socio.value for socio in Socio],
            height=35,
            command=self.socio_mudou
        )
        self.socio_dropdown.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(8, 0))

        # Mês
        ctk.CTkLabel(row1, text="Mês *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=1, sticky="w", padx=(0, 10))
        self.mes_dropdown = ctk.CTkOptionMenu(
            row1,
            values=[str(i) for i in range(1, 13)],
            height=35
        )
        self.mes_dropdown.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(8, 0))
        self.mes_dropdown.set(str(date.today().month))

        # Ano
        ctk.CTkLabel(row1, text="Ano *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=2, sticky="w")
        self.ano_entry = ctk.CTkEntry(row1, height=35)
        self.ano_entry.grid(row=1, column=2, sticky="ew", pady=(8, 0))
        self.ano_entry.insert(0, str(date.today().year))
        self.ano_entry.bind("<FocusOut>", lambda e: self.ano_mudou())

        # Data Emissão
        ctk.CTkLabel(fields_frame, text="Data de Emissão *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 8))
        self.data_emissao_picker = DatePickerDropdown(fields_frame, default_date=date.today())
        self.data_emissao_picker.grid(row=3, column=0, sticky="ew", pady=(0, 18))

        # Valores de Referência (read-only display)
        valores_label_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        valores_label_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))

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
        totais_label_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        totais_label_frame.grid(row=5, column=0, sticky="ew", pady=(0, 18))

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
        ctk.CTkLabel(fields_frame, text="Descrição", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=6, column=0, sticky="w", pady=(0, 8))
        self.descricao_entry = ctk.CTkTextbox(fields_frame, height=60)
        self.descricao_entry.grid(row=7, column=0, sticky="ew", pady=(0, 18))

        # Nota
        ctk.CTkLabel(fields_frame, text="Nota", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=8, column=0, sticky="w", pady=(0, 8))
        self.nota_entry = ctk.CTkTextbox(fields_frame, height=60)
        self.nota_entry.grid(row=9, column=0, sticky="ew", pady=(0, 10))

    def create_linhas_section(self, parent):
        """Cria secção de linhas (deslocações)"""
        linhas_frame = ctk.CTkFrame(parent, fg_color="transparent")
        linhas_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 20))
        linhas_frame.grid_columnconfigure(0, weight=1)

        # Header com título e botão adicionar
        linhas_header = ctk.CTkFrame(linhas_frame, fg_color="transparent")
        linhas_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(
            linhas_header,
            text="🗺️ Deslocações",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")

        add_linha_btn = ctk.CTkButton(
            linhas_header,
            text="➕ Adicionar Deslocação",
            command=self.adicionar_linha,
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
            linhas_frame,
            columns=columns,
            on_row_double_click=self.editar_linha,
            height=200
        )
        self.linhas_table.grid(row=1, column=0, sticky="ew")

        # Botão apagar linha
        self.delete_linha_btn = ctk.CTkButton(
            linhas_frame,
            text="🗑️ Apagar Linha Selecionada",
            command=self.apagar_linha,
            width=220,
            height=35,
            fg_color=("#F44336", "#C62828"),
            hover_color=("#E57373", "#B71C1C")
        )
        self.delete_linha_btn.grid(row=2, column=0, sticky="e", pady=(10, 0))

    def create_footer(self, parent):
        """Cria footer com botões"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(10, 30))

        # Botão Guardar
        save_btn = ctk.CTkButton(
            footer_frame,
            text="💾 Guardar",
            command=self.guardar,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        save_btn.pack(side="left", padx=(0, 10))

        # Botão Cancelar
        cancel_btn = ctk.CTkButton(
            footer_frame,
            text="Cancelar",
            command=self.voltar,
            width=130,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=("#757575", "#616161"),
            hover_color=("#616161", "#424242")
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        # Botão Duplicar (só quando edita)
        if self.boletim_id:
            duplicate_btn = ctk.CTkButton(
                footer_frame,
                text="📋 Duplicar",
                command=self.duplicar_boletim,
                width=140,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color=("#2196F3", "#1976D2"),
                hover_color=("#64B5F6", "#1565C0")
            )
            duplicate_btn.pack(side="left")

    def carregar_boletim(self):
        """Carrega dados do boletim para edição"""
        self.boletim = self.boletins_manager.obter_por_id(self.boletim_id)
        if not self.boletim:
            messagebox.showerror("Erro", "Boletim não encontrado!")
            self.voltar()
            return

        # Atualizar título
        self.title_label.configure(text=f"Editar Boletim {self.boletim.numero}")

        b = self.boletim

        # Socio
        self.socio_dropdown.set(b.socio.value)

        # Mês/Ano
        if b.mes:
            self.mes_dropdown.set(str(b.mes))
        if b.ano:
            self.ano_entry.delete(0, "end")
            self.ano_entry.insert(0, str(b.ano))

        # Data emissão
        if b.data_emissao:
            self.data_emissao_picker.set_date(b.data_emissao)

        # Valores de referência
        if b.val_dia_nacional:
            self.val_nacional_label.configure(text=f"Dia Nacional: €{float(b.val_dia_nacional):.2f}")
        if b.val_dia_estrangeiro:
            self.val_estrangeiro_label.configure(text=f"Dia Estrangeiro: €{float(b.val_dia_estrangeiro):.2f}")
        if b.val_km:
            self.val_km_label.configure(text=f"Km: €{float(b.val_km):.2f}")

        # Totais
        self.atualizar_totais_display()

        # Descrição/Nota
        if b.descricao:
            self.descricao_entry.insert("1.0", b.descricao)
        if b.nota:
            self.nota_entry.insert("1.0", b.nota)

        # Carregar linhas
        self.carregar_linhas()

    def carregar_linhas(self):
        """Load boletim linhas into table"""
        if not self.boletim:
            self.linhas_table.set_data([])
            return

        linhas = self.linhas_manager.listar_por_boletim(self.boletim.id)
        data = [self.linha_to_dict(linha) for linha in linhas]
        self.linhas_table.set_data(data)

    def linha_to_dict(self, linha) -> dict:
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

    def socio_mudou(self, *args):
        """Handle socio change - update valores de referência"""
        self.sugerir_valores_referencia()

    def ano_mudou(self):
        """Handle ano change - update valores de referência"""
        self.sugerir_valores_referencia()

    def sugerir_valores_referencia(self):
        """Fetch and display valores de referência based on ano"""
        try:
            ano_str = self.ano_entry.get().strip()
            if not ano_str:
                return

            ano = int(ano_str)
            val_nacional, val_estrangeiro, val_km = self.valores_manager.obter_ou_default(ano)

            self.val_nacional_label.configure(text=f"Dia Nacional: €{float(val_nacional):.2f}")
            self.val_estrangeiro_label.configure(text=f"Dia Estrangeiro: €{float(val_estrangeiro):.2f}")
            self.val_km_label.configure(text=f"Km: €{float(val_km):.2f}")

        except ValueError:
            pass

    def atualizar_totais_display(self):
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

    def adicionar_linha(self):
        """Open dialog to add new linha"""
        if not self.boletim:
            messagebox.showerror("Erro", "Grave o boletim primeiro antes de adicionar deslocações.")
            return

        dialog = LinhaDialog(self, self.db_session, self.boletim.id)
        dialog.wait_window()

        # Reload
        self.carregar_linhas()
        self.refresh_boletim()

    def editar_linha(self, row_data):
        """Edit linha (double-click handler)"""
        linha = row_data.get('_linha')
        if not linha:
            return

        dialog = LinhaDialog(self, self.db_session, self.boletim.id, linha=linha)
        dialog.wait_window()

        # Reload
        self.carregar_linhas()
        self.refresh_boletim()

    def apagar_linha(self):
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
                self.carregar_linhas()
                self.refresh_boletim()
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar linha")

    def refresh_boletim(self):
        """Refresh boletim from database and update totais display"""
        if self.boletim:
            self.db_session.refresh(self.boletim)
            self.atualizar_totais_display()

    def guardar(self):
        """Guarda o boletim"""
        try:
            # Get values
            socio_str = self.socio_dropdown.get()
            mes = int(self.mes_dropdown.get())
            ano_str = self.ano_entry.get().strip()
            data_emissao = self.data_emissao_picker.get_date()
            descricao = self.descricao_entry.get("1.0", "end-1c").strip() or None
            nota = self.nota_entry.get("1.0", "end-1c").strip() or None

            # Validations
            if not ano_str:
                messagebox.showerror("Erro", "Ano é obrigatório")
                return

            ano = int(ano_str)

            if not data_emissao:
                messagebox.showerror("Erro", "Data de emissão é obrigatória")
                return

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

                self.voltar()

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
                    nota=nota
                )

                if sucesso:
                    # Switch to edit mode
                    self.boletim = novo_boletim
                    self.boletim_id = novo_boletim.id
                    self.title_label.configure(text=f"Editar Boletim {novo_boletim.numero}")

                    messagebox.showinfo("Sucesso", f"Boletim {novo_boletim.numero} criado! Agora pode adicionar deslocações.")

                else:
                    messagebox.showerror("Erro", erro or "Erro ao criar boletim")

        except ValueError as e:
            messagebox.showerror("Erro", f"Valores inválidos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def duplicar_boletim(self):
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

    def voltar(self):
        """Volta para a lista de boletins"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("boletins")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")


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
