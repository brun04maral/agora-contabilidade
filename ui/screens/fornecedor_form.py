# -*- coding: utf-8 -*-
"""
Tela de Formulário de Fornecedor - Screen dedicado para criar/editar fornecedores
Segue mesmo padrão de ui/screens/projeto_form.py
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from logic.fornecedores import FornecedoresManager
from database.models import EstatutoFornecedor
from ui.components.date_picker_dropdown import DatePickerDropdown
from typing import Optional
from datetime import datetime
from tkinter import messagebox
import webbrowser


class FornecedorFormScreen(ctk.CTkFrame):
    """
    Screen para criar/editar fornecedores

    Navegação via MainWindow.show_screen("fornecedor_form", fornecedor_id=None/ID)
    """

    def __init__(self, parent, db_session: Session, fornecedor_id: Optional[int] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.fornecedor_id = fornecedor_id
        self.manager = FornecedoresManager(db_session)

        # Estado
        self.fornecedor = None

        # Configure
        self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.create_widgets()

        # Load data se edição
        if fornecedor_id:
            self.carregar_fornecedor()

        # Set initial visibility of seguro field
        self._toggle_seguro_field()

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
        # 2. CAMPOS DO FORNECEDOR
        # ========================================
        self.create_fields(main_container)

        # ========================================
        # 3. FOOTER COM BOTÕES
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
        titulo = "Novo Fornecedor" if not self.fornecedor_id else "Editar Fornecedor"
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

        # Nome (required)
        ctk.CTkLabel(fields_frame, text="Nome *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8))
        self.nome_entry = ctk.CTkEntry(fields_frame, placeholder_text="Nome do fornecedor...", height=35)
        self.nome_entry.grid(row=1, column=0, sticky="ew", pady=(0, 18))

        # Estatuto (required)
        ctk.CTkLabel(fields_frame, text="Estatuto *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 8))
        self.estatuto_var = ctk.StringVar(value="FREELANCER")
        estatuto_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        estatuto_frame.grid(row=3, column=0, sticky="w", pady=(0, 18))
        for estatuto in ["EMPRESA", "FREELANCER", "ESTADO"]:
            ctk.CTkRadioButton(
                estatuto_frame, text=estatuto, variable=self.estatuto_var, value=estatuto,
                command=self._toggle_seguro_field
            ).pack(side="left", padx=(0, 20))

        # Área e Função (side by side)
        area_funcao_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        area_funcao_frame.grid(row=4, column=0, sticky="ew", pady=(0, 18))
        area_funcao_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(area_funcao_frame, text="Área", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 12))
        self.area_entry = ctk.CTkEntry(area_funcao_frame, placeholder_text="Ex: Produção, Som...", height=35)
        self.area_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(8, 0))

        ctk.CTkLabel(area_funcao_frame, text="Função", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=1, sticky="w")
        self.funcao_entry = ctk.CTkEntry(area_funcao_frame, placeholder_text="Ex: Editor, Realizador...", height=35)
        self.funcao_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))

        # Classificação
        ctk.CTkLabel(fields_frame, text="Classificação (1-5 estrelas)", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=5, column=0, sticky="w", pady=(0, 8))
        self.classificacao_var = ctk.StringVar(value="0")
        class_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        class_frame.grid(row=6, column=0, sticky="w", pady=(0, 18))
        for i in range(6):
            text = "Nenhuma" if i == 0 else "★" * i
            ctk.CTkRadioButton(class_frame, text=text, variable=self.classificacao_var, value=str(i)).pack(
                side="left", padx=(0, 15))

        # NIF e IBAN (side by side)
        nif_iban_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        nif_iban_frame.grid(row=7, column=0, sticky="ew", pady=(0, 18))
        nif_iban_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(nif_iban_frame, text="NIF / Tax ID", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 12))
        self.nif_entry = ctk.CTkEntry(nif_iban_frame, placeholder_text="Número fiscal...", height=35)
        self.nif_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(8, 0))

        ctk.CTkLabel(nif_iban_frame, text="IBAN", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=1, sticky="w")
        self.iban_entry = ctk.CTkEntry(nif_iban_frame, placeholder_text="PT50...", height=35)
        self.iban_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))

        # Morada
        ctk.CTkLabel(fields_frame, text="Morada", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=8, column=0, sticky="w", pady=(0, 8))
        self.morada_entry = ctk.CTkTextbox(fields_frame, height=60)
        self.morada_entry.grid(row=9, column=0, sticky="ew", pady=(0, 18))

        # Contacto e Email (side by side)
        contacto_email_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        contacto_email_frame.grid(row=10, column=0, sticky="ew", pady=(0, 18))
        contacto_email_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(contacto_email_frame, text="Contacto", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 12))
        self.contacto_entry = ctk.CTkEntry(contacto_email_frame, placeholder_text="Telefone...", height=35)
        self.contacto_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(8, 0))

        ctk.CTkLabel(contacto_email_frame, text="Email", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=1, sticky="w")
        self.email_entry = ctk.CTkEntry(contacto_email_frame, placeholder_text="email@exemplo.pt", height=35)
        self.email_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))

        # Website
        ctk.CTkLabel(fields_frame, text="Website", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=11, column=0, sticky="w", pady=(0, 8))
        website_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        website_frame.grid(row=12, column=0, sticky="ew", pady=(0, 18))
        website_frame.grid_columnconfigure(0, weight=1)
        self.website_entry = ctk.CTkEntry(website_frame, placeholder_text="https://exemplo.pt", height=35)
        self.website_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkButton(
            website_frame, text="🔗 Abrir", width=80, height=35, command=self._open_website,
            fg_color=("#2196F3", "#1565C0"), hover_color=("#1976D2", "#0D47A1")
        ).grid(row=0, column=1)

        # Seguro frame (only for FREELANCER)
        self.seguro_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        ctk.CTkLabel(self.seguro_frame, text="Validade Seguro Trabalho", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8))
        self.seguro_picker = DatePickerDropdown(self.seguro_frame, placeholder="Selecionar data de validade...")
        self.seguro_picker.grid(row=1, column=0, sticky="ew")
        self.seguro_frame.grid_columnconfigure(0, weight=1)

        # Nota
        ctk.CTkLabel(fields_frame, text="Nota", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=14, column=0, sticky="w", pady=(0, 8))
        self.nota_entry = ctk.CTkTextbox(fields_frame, height=80)
        self.nota_entry.grid(row=15, column=0, sticky="ew", pady=(0, 10))

    def create_footer(self, parent):
        """Cria footer com botões"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(10, 30))

        # Botão Guardar
        save_btn = ctk.CTkButton(
            footer_frame,
            text="💾 Guardar",
            command=self.guardar,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#2196F3", "#1565C0"),
            hover_color=("#1976D2", "#0D47A1")
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
        cancel_btn.pack(side="left")

    def _toggle_seguro_field(self):
        """Mostra/oculta campo de seguro baseado no estatuto"""
        estatuto = self.estatuto_var.get()
        if estatuto == "FREELANCER":
            self.seguro_frame.grid(row=13, column=0, sticky="ew", pady=(0, 18))
        else:
            self.seguro_frame.grid_forget()

    def _open_website(self):
        """Abre o website no browser padrão"""
        website = self.website_entry.get().strip()
        if website:
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            webbrowser.open(website)
        else:
            messagebox.showerror("Erro", "Nenhum website para abrir")

    def carregar_fornecedor(self):
        """Carrega dados do fornecedor para edição"""
        self.fornecedor = self.manager.buscar_por_id(self.fornecedor_id)
        if not self.fornecedor:
            messagebox.showerror("Erro", "Fornecedor não encontrado!")
            self.voltar()
            return

        # Atualizar título
        self.title_label.configure(text=f"Editar Fornecedor {self.fornecedor.numero}")

        f = self.fornecedor

        # Nome
        self.nome_entry.insert(0, f.nome)

        # Estatuto
        if f.estatuto:
            self.estatuto_var.set(f.estatuto.value)

        # Área
        if f.area:
            self.area_entry.insert(0, f.area)

        # Função
        if f.funcao:
            self.funcao_entry.insert(0, f.funcao)

        # Classificação
        if f.classificacao:
            self.classificacao_var.set(str(f.classificacao))

        # NIF
        if f.nif:
            self.nif_entry.insert(0, f.nif)

        # IBAN
        if f.iban:
            self.iban_entry.insert(0, f.iban)

        # Morada
        if f.morada:
            self.morada_entry.insert("1.0", f.morada)

        # Contacto
        if f.contacto:
            self.contacto_entry.insert(0, f.contacto)

        # Email
        if f.email:
            self.email_entry.insert(0, f.email)

        # Website
        if f.website:
            self.website_entry.insert(0, f.website)

        # Validade seguro
        if f.validade_seguro_trabalho:
            if hasattr(f.validade_seguro_trabalho, 'date'):
                self.seguro_picker.set_date(f.validade_seguro_trabalho.date())
            else:
                self.seguro_picker.set_date(f.validade_seguro_trabalho)

        # Nota
        if f.nota:
            self.nota_entry.insert("1.0", f.nota)

        # Update seguro visibility
        self._toggle_seguro_field()

    def guardar(self):
        """Guarda o fornecedor"""
        try:
            # Get values
            nome = self.nome_entry.get().strip()
            estatuto_str = self.estatuto_var.get()
            area = self.area_entry.get().strip()
            funcao = self.funcao_entry.get().strip()
            classificacao = int(self.classificacao_var.get())
            nif = self.nif_entry.get().strip()
            iban = self.iban_entry.get().strip()
            morada = self.morada_entry.get("1.0", "end-1c").strip()
            contacto = self.contacto_entry.get().strip()
            email = self.email_entry.get().strip()
            website = self.website_entry.get().strip()
            nota = self.nota_entry.get("1.0", "end-1c").strip()

            # Validate
            if not nome:
                messagebox.showerror("Erro", "Nome é obrigatório")
                return

            # Parse estatuto
            try:
                estatuto = EstatutoFornecedor[estatuto_str]
            except:
                messagebox.showerror("Erro", "Estatuto inválido")
                return

            # Parse seguro date
            validade_seguro = None
            if self.seguro_picker.get():
                seguro_date = self.seguro_picker.get_date()
                validade_seguro = datetime.combine(seguro_date, datetime.min.time())

            # Create or update
            if self.fornecedor_id:
                # Update
                success, fornecedor, message = self.manager.atualizar(
                    self.fornecedor_id,
                    nome=nome,
                    estatuto=estatuto,
                    area=area if area else None,
                    funcao=funcao if funcao else None,
                    classificacao=classificacao if classificacao > 0 else None,
                    nif=nif if nif else None,
                    iban=iban if iban else None,
                    morada=morada if morada else None,
                    contacto=contacto if contacto else None,
                    email=email if email else None,
                    website=website if website else None,
                    validade_seguro_trabalho=validade_seguro,
                    nota=nota if nota else None
                )

                if success:
                    self.voltar()
                else:
                    messagebox.showerror("Erro", message)
            else:
                # Create
                success, fornecedor, message = self.manager.criar(
                    nome=nome,
                    estatuto=estatuto,
                    area=area if area else None,
                    funcao=funcao if funcao else None,
                    classificacao=classificacao if classificacao > 0 else None,
                    nif=nif if nif else None,
                    iban=iban if iban else None,
                    morada=morada if morada else None,
                    contacto=contacto if contacto else None,
                    email=email if email else None,
                    website=website if website else None,
                    validade_seguro_trabalho=validade_seguro,
                    nota=nota if nota else None
                )

                if success:
                    self.voltar()
                else:
                    messagebox.showerror("Erro", message)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def voltar(self):
        """Volta para a lista de fornecedores"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("fornecedores")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")
