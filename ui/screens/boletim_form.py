# -*- coding: utf-8 -*-
"""
Screen de Edição de Boletim Itinerário (Header + Linhas)
Editor completo para boletins com deslocações
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, time
import tkinter.messagebox as messagebox

from logic.boletins import BoletinsManager
from logic.boletim_linhas import BoletimLinhasManager
from logic.valores_referencia import ValoresReferenciaManager
from logic.projetos import ProjetosManager
from database.models.boletim import Socio
from database.models.boletim_linha import TipoDeslocacao
from ui.components.data_table_v2 import DataTableV2
from utils.base_dialogs import BaseDialogLarge


class BoletimFormScreen(ctk.CTkToplevel):
    """
    Tela de edição completa de boletim itinerário
    Permite editar header + adicionar/editar/remover linhas de deslocação
    """

    def __init__(self, parent, db_session: Session, boletim=None, callback=None):
        super().__init__(parent)

        self.db_session = db_session
        self.boletim = boletim
        self.callback = callback

        self.boletins_manager = BoletinsManager(db_session)
        self.linhas_manager = BoletimLinhasManager(db_session)
        self.valores_manager = ValoresReferenciaManager(db_session)
        self.projetos_manager = ProjetosManager(db_session)

        # Window config
        self.title(f"Editar Boletim {boletim.numero}" if boletim else "Novo Boletim")
        self.geometry("1100x800")
        self.resizable(True, True)

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1100 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"+{x}+{y}")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_layout()

        if boletim:
            self.carregar_dados()
            self.carregar_linhas()
        else:
            # New boletim - suggest default values
            self.sugerir_valores_referencia()

    def create_layout(self):
        """Create screen layout"""
        # Main container with scroll
        main_container = ctk.CTkScrollableFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # ============ HEADER SECTION ============
        header_section = ctk.CTkFrame(main_container, fg_color="transparent")
        header_section.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_section,
            text="📋 Dados do Boletim",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        # Header form
        header_form = ctk.CTkFrame(header_section, fg_color="transparent")
        header_form.pack(fill="x")

        # Row 1: Sócio + Mês + Ano
        row1 = ctk.CTkFrame(header_form, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))

        # Sócio
        col1 = ctk.CTkFrame(row1, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(col1, text="Sócio:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.socio_dropdown = ctk.CTkOptionMenu(
            col1,
            values=[socio.value for socio in Socio],
            height=35,
            font=ctk.CTkFont(size=13),
            command=self.socio_mudou
        )
        self.socio_dropdown.pack(fill="x")

        # Mês
        col2 = ctk.CTkFrame(row1, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(col2, text="Mês:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.mes_dropdown = ctk.CTkOptionMenu(
            col2,
            values=[str(i) for i in range(1, 13)],
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.mes_dropdown.pack(fill="x")
        self.mes_dropdown.set(str(date.today().month))

        # Ano
        col3 = ctk.CTkFrame(row1, fg_color="transparent")
        col3.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(col3, text="Ano:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.ano_entry = ctk.CTkEntry(col3, height=35, font=ctk.CTkFont(size=13))
        self.ano_entry.pack(fill="x")
        self.ano_entry.insert(0, str(date.today().year))
        self.ano_entry.bind("<FocusOut>", lambda e: self.ano_mudou())

        # Row 2: Data Emissão
        row2 = ctk.CTkFrame(header_form, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(row2, text="Data de Emissão:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        from ui.components.date_picker_dropdown import DatePickerDropdown
        self.data_emissao_picker = DatePickerDropdown(row2, default_date=date.today())
        self.data_emissao_picker.pack(fill="x")

        # Row 3: Valores de Referência (read-only display)
        row3 = ctk.CTkFrame(header_form, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            row3,
            text="📊 Valores de Referência:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        valores_frame = ctk.CTkFrame(row3, fg_color="transparent")
        valores_frame.pack(fill="x")

        self.val_nacional_label = ctk.CTkLabel(
            valores_frame,
            text="Dia Nacional: €0.00",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.val_nacional_label.pack(side="left", padx=(0, 20))

        self.val_estrangeiro_label = ctk.CTkLabel(
            valores_frame,
            text="Dia Estrangeiro: €0.00",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.val_estrangeiro_label.pack(side="left", padx=(0, 20))

        self.val_km_label = ctk.CTkLabel(
            valores_frame,
            text="Km: €0.00",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.val_km_label.pack(side="left")

        # Row 4: Totais Calculados (read-only display)
        row4 = ctk.CTkFrame(header_form, fg_color="transparent")
        row4.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            row4,
            text="💰 Totais Calculados:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        totais_frame = ctk.CTkFrame(row4, fg_color="transparent")
        totais_frame.pack(fill="x")

        self.total_nacional_label = ctk.CTkLabel(
            totais_frame,
            text="Ajudas Nacionais: €0.00",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.total_nacional_label.pack(side="left", padx=(0, 15))

        self.total_estrangeiro_label = ctk.CTkLabel(
            totais_frame,
            text="Ajudas Estrangeiro: €0.00",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.total_estrangeiro_label.pack(side="left", padx=(0, 15))

        self.total_kms_label = ctk.CTkLabel(
            totais_frame,
            text="Kms: €0.00",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.total_kms_label.pack(side="left", padx=(0, 15))

        self.valor_total_label = ctk.CTkLabel(
            totais_frame,
            text="TOTAL: €0.00",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#2196F3", "#64B5F6")
        )
        self.valor_total_label.pack(side="left")

        # Row 5: Descrição
        row5 = ctk.CTkFrame(header_form, fg_color="transparent")
        row5.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(row5, text="Descrição (opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.descricao_entry = ctk.CTkTextbox(row5, height=60)
        self.descricao_entry.pack(fill="x")

        # Row 6: Nota
        row6 = ctk.CTkFrame(header_form, fg_color="transparent")
        row6.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(row6, text="Nota (opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.nota_entry = ctk.CTkTextbox(row6, height=60)
        self.nota_entry.pack(fill="x")

        # ============ LINHAS SECTION ============
        linhas_section = ctk.CTkFrame(main_container, fg_color="transparent")
        linhas_section.pack(fill="both", expand=True, pady=(20, 0))

        # Linhas header
        linhas_header = ctk.CTkFrame(linhas_section, fg_color="transparent")
        linhas_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            linhas_header,
            text="🗺️ Deslocações",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")

        # Add line button
        add_linha_btn = ctk.CTkButton(
            linhas_header,
            text="➕ Adicionar Deslocação",
            command=self.adicionar_linha,
            width=180,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        add_linha_btn.pack(side="right")

        # Linhas table
        table_frame = ctk.CTkFrame(linhas_section)
        table_frame.pack(fill="both", expand=True)

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
            table_frame,
            columns=columns,
            on_row_double_click=self.editar_linha,
            height=250
        )
        self.linhas_table.pack(fill="both", expand=True)

        # ============ BOTTOM BUTTONS ============
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=self.destroy,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
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
            font=ctk.CTkFont(size=14),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        save_btn.pack(side="left")

        # Duplicate button (only when editing existing boletim)
        if self.boletim:
            duplicate_btn = ctk.CTkButton(
                btn_frame,
                text="📋 Duplicar",
                command=self.duplicar_boletim,
                width=140,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color=("#2196F3", "#1976D2"),
                hover_color=("#64B5F6", "#1565C0")
            )
            duplicate_btn.pack(side="left", padx=(10, 0))

        # Delete button (only when editing)
        if self.boletim:
            delete_linha_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️ Apagar Linha Selecionada",
                command=self.apagar_linha,
                width=220,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color=("#F44336", "#C62828"),
                hover_color=("#E57373", "#B71C1C")
            )
            delete_linha_btn.pack(side="right")

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

    def carregar_dados(self):
        """Load boletim header data"""
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

        # Descrição/Nota
        if b.descricao:
            self.descricao_entry.insert("1.0", b.descricao)
        if b.nota:
            self.nota_entry.insert("1.0", b.nota)

        # Valores de referência
        if b.val_dia_nacional:
            self.val_nacional_label.configure(text=f"Dia Nacional: €{float(b.val_dia_nacional):.2f}")
        if b.val_dia_estrangeiro:
            self.val_estrangeiro_label.configure(text=f"Dia Estrangeiro: €{float(b.val_dia_estrangeiro):.2f}")
        if b.val_km:
            self.val_km_label.configure(text=f"Km: €{float(b.val_km):.2f}")

        # Totais
        self.atualizar_totais_display()

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
        # Get projeto numero if exists
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

    def gravar(self):
        """Save boletim header"""
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

                self.atualizar_totais_display()

                if self.callback:
                    self.callback()

                self.destroy()

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
                    self.title(f"Editar Boletim {novo_boletim.numero}")

                    if self.callback:
                        self.callback()

                    messagebox.showinfo("Sucesso", f"Boletim {novo_boletim.numero} criado! Agora pode adicionar deslocações.")

                else:
                    messagebox.showerror("Erro", erro or "Erro ao criar boletim")

        except ValueError as e:
            messagebox.showerror("Erro", f"Valores inválidos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def duplicar_boletim(self):
        """
        Duplica o boletim atual (header + todas as linhas)

        Conforme BUSINESS_LOGIC.md Secção 2.3:
        - Duplica boletim completo
        - Abre novo boletim em modo edição
        - Permite editar antes de gravar
        """
        try:
            if not self.boletim:
                messagebox.showerror("Erro", "Nenhum boletim para duplicar")
                return

            # Confirm duplication
            resposta = messagebox.askyesno(
                "Duplicar Boletim",
                f"Duplicar boletim {self.boletim.numero}?\n\n"
                f"Todas as deslocações serão copiadas.\n"
                f"Você poderá editar o novo boletim antes de gravar."
            )

            if not resposta:
                return

            # Duplicate using manager
            sucesso, novo_boletim, erro = self.boletins_manager.duplicar_boletim(self.boletim.id)

            if sucesso:
                # Close current window
                if self.callback:
                    self.callback()

                # Open new window with duplicated boletim
                from ui.screens.boletim_form import BoletimFormScreen
                novo_form = BoletimFormScreen(
                    self.master,
                    self.db_session,
                    boletim=novo_boletim,
                    callback=self.callback
                )

                # Update title to indicate it's a duplicate
                novo_form.title(f"Novo Boletim {novo_boletim.numero} (duplicado de {self.boletim.numero})")

                self.destroy()

            else:
                messagebox.showerror("Erro", erro or "Erro ao duplicar boletim")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao duplicar boletim: {str(e)}")


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
        # Use main_frame (already scrollable from BaseDialogLarge)
        scroll = self.main_frame

        # Title
        ctk.CTkLabel(
            scroll,
            text="✏️ Editar Deslocação" if self.linha else "➕ Nova Deslocação",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 20))

        # Projeto (optional dropdown)
        ctk.CTkLabel(scroll, text="Projeto (opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))

        # Get projetos
        projetos = self.projetos_manager.listar_todos()
        projeto_options = ["- Nenhum -"] + [f"{p.numero} - {p.descricao[:50]}" for p in projetos]

        self.projeto_dropdown = ctk.CTkOptionMenu(
            scroll,
            values=projeto_options,
            height=35,
            font=ctk.CTkFont(size=13),
            command=self.projeto_selecionado
        )
        self.projeto_dropdown.pack(fill="x", pady=(0, 10))

        # Store projeto mapping
        self.projeto_map = {f"{p.numero} - {p.descricao[:50]}": p.id for p in projetos}
        self.projetos_dict = {p.id: p for p in projetos}  # Para acesso rápido ao projeto completo

        # Serviço
        ctk.CTkLabel(scroll, text="Serviço/Descrição *:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.servico_entry = ctk.CTkTextbox(scroll, height=80)
        self.servico_entry.pack(fill="x", pady=(0, 10))

        # Localidade
        ctk.CTkLabel(scroll, text="Localidade:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.localidade_entry = ctk.CTkEntry(scroll, height=35, font=ctk.CTkFont(size=13))
        self.localidade_entry.pack(fill="x", pady=(0, 10))

        # Tipo
        ctk.CTkLabel(scroll, text="Tipo de Deslocação *:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.tipo_dropdown = ctk.CTkOptionMenu(
            scroll,
            values=[tipo.value for tipo in TipoDeslocacao],
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.tipo_dropdown.pack(fill="x", pady=(0, 10))

        # Dias
        ctk.CTkLabel(scroll, text="Dias *:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.dias_entry = ctk.CTkEntry(scroll, height=35, font=ctk.CTkFont(size=13))
        self.dias_entry.pack(fill="x", pady=(0, 10))
        self.dias_entry.insert(0, "0")

        # Kms
        ctk.CTkLabel(scroll, text="Quilómetros *:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.kms_entry = ctk.CTkEntry(scroll, height=35, font=ctk.CTkFont(size=13))
        self.kms_entry.pack(fill="x", pady=(0, 10))
        self.kms_entry.insert(0, "0")

        # Data Início (optional)
        ctk.CTkLabel(scroll, text="Data Início (opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        from ui.components.date_picker_dropdown import DatePickerDropdown
        self.data_inicio_picker = DatePickerDropdown(scroll, default_date=None, placeholder="Selecionar data...")
        self.data_inicio_picker.pack(fill="x", pady=(0, 10))

        # Hora Início (optional)
        ctk.CTkLabel(scroll, text="Hora Início (HH:MM, opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.hora_inicio_entry = ctk.CTkEntry(scroll, height=35, font=ctk.CTkFont(size=13), placeholder_text="09:00")
        self.hora_inicio_entry.pack(fill="x", pady=(0, 10))

        # Data Fim (optional)
        ctk.CTkLabel(scroll, text="Data Fim (opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.data_fim_picker = DatePickerDropdown(scroll, default_date=None, placeholder="Selecionar data...")
        self.data_fim_picker.pack(fill="x", pady=(0, 10))

        # Hora Fim (optional)
        ctk.CTkLabel(scroll, text="Hora Fim (HH:MM, opcional):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.hora_fim_entry = ctk.CTkEntry(scroll, height=35, font=ctk.CTkFont(size=13), placeholder_text="18:00")
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
            font=ctk.CTkFont(size=14),
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
            font=ctk.CTkFont(size=14),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        save_btn.pack(side="left")

    def projeto_selecionado(self, projeto_str: str):
        """
        Auto-preenche a descrição e datas quando um projeto é selecionado

        Args:
            projeto_str: String do projeto selecionado (ex: "#P0001 - Descrição")
        """
        # Verificar se é um projeto válido
        if projeto_str == "- Nenhum -":
            return

        # Obter projeto_id
        projeto_id = self.projeto_map.get(projeto_str)
        if not projeto_id:
            return

        # Buscar projeto completo
        projeto = self.projetos_dict.get(projeto_id)
        if not projeto:
            return

        # Auto-preencher serviço/descrição apenas se estiver vazio
        # (para não sobrescrever se o utilizador já escreveu algo)
        conteudo_atual = self.servico_entry.get("1.0", "end-1c").strip()
        if not conteudo_atual:
            # Preencher com a descrição completa do projeto
            self.servico_entry.delete("1.0", "end")
            self.servico_entry.insert("1.0", projeto.descricao)

        # Auto-preencher datas apenas se estiverem vazias
        # Data início
        if projeto.data_inicio and self.data_inicio_picker.get_date() is None:
            self.data_inicio_picker.set_date(projeto.data_inicio)

        # Data fim
        if projeto.data_fim and self.data_fim_picker.get_date() is None:
            self.data_fim_picker.set_date(projeto.data_fim)

    def preencher_dados(self, linha):
        """Fill form with existing linha data"""
        # Projeto
        if linha.projeto_id and linha.projeto:
            projeto_key = f"{linha.projeto.numero} - {linha.projeto.descricao[:50]}"
            self.projeto_dropdown.set(projeto_key)

        # Serviço
        self.servico_entry.insert("1.0", linha.servico)

        # Localidade
        if linha.localidade:
            self.localidade_entry.insert(0, linha.localidade)

        # Tipo
        self.tipo_dropdown.set(linha.tipo.value)

        # Dias
        self.dias_entry.delete(0, "end")
        self.dias_entry.insert(0, str(float(linha.dias)))

        # Kms
        self.kms_entry.delete(0, "end")
        self.kms_entry.insert(0, str(linha.kms))

        # Data/Hora início
        if linha.data_inicio:
            self.data_inicio_picker.set_date(linha.data_inicio)
        if linha.hora_inicio:
            self.hora_inicio_entry.insert(0, linha.hora_inicio.strftime("%H:%M"))

        # Data/Hora fim
        if linha.data_fim:
            self.data_fim_picker.set_date(linha.data_fim)
        if linha.hora_fim:
            self.hora_fim_entry.insert(0, linha.hora_fim.strftime("%H:%M"))

    def gravar(self):
        """Save linha"""
        try:
            # Get values
            servico = self.servico_entry.get("1.0", "end-1c").strip()
            localidade = self.localidade_entry.get().strip() or None
            tipo_str = self.tipo_dropdown.get()
            dias_str = self.dias_entry.get().strip()
            kms_str = self.kms_entry.get().strip()

            # Validations
            if not servico:
                messagebox.showerror("Erro", "Serviço é obrigatório")
                return

            if not dias_str or not kms_str:
                messagebox.showerror("Erro", "Dias e Kms são obrigatórios")
                return

            # Convert
            tipo = TipoDeslocacao(tipo_str)
            dias = Decimal(dias_str)
            kms = int(kms_str)

            # Projeto ID
            projeto_id = None
            projeto_sel = self.projeto_dropdown.get()
            if projeto_sel != "- Nenhum -":
                projeto_id = self.projeto_map.get(projeto_sel)

            # Optional data/hora
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

            # Save
            if self.linha:
                # Update
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
                # Create
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
