# -*- coding: utf-8 -*-
"""
Tela de Formulário de Cliente - Screen dedicado para criar/editar clientes
Segue mesmo padrão de ui/screens/projeto_form.py
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from logic.clientes import ClientesManager
from typing import Optional
from tkinter import messagebox


class ClienteFormScreen(ctk.CTkFrame):
    """
    Screen para criar/editar clientes

    Navegação via MainWindow.show_screen("cliente_form", cliente_id=None/ID)
    """

    def __init__(self, parent, db_session: Session, cliente_id: Optional[int] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.cliente_id = cliente_id
        self.manager = ClientesManager(db_session)

        # Estado
        self.cliente = None

        # Configure
        self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.create_widgets()

        # Load data se edição
        if cliente_id:
            self.carregar_cliente()

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
        # 2. CAMPOS DO CLIENTE
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
        titulo = "Novo Cliente" if not self.cliente_id else "Editar Cliente"
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
            row=0, column=0, sticky="w", pady=(0, 5))
        ctk.CTkLabel(
            fields_frame,
            text="Nome curto para listagens (max 120 caracteres)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.nome_entry = ctk.CTkEntry(fields_frame, placeholder_text="Ex: Farmácia do Povo", height=35)
        self.nome_entry.grid(row=2, column=0, sticky="ew", pady=(0, 18))

        # Nome Formal
        ctk.CTkLabel(fields_frame, text="Nome Formal", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=3, column=0, sticky="w", pady=(0, 5))
        ctk.CTkLabel(
            fields_frame,
            text="Nome completo/formal da empresa (opcional, max 255 caracteres)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.nome_formal_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ex: Farmácia Popular do Centro, Lda.",
            height=35
        )
        self.nome_formal_entry.grid(row=5, column=0, sticky="ew", pady=(0, 18))

        # NIF
        ctk.CTkLabel(fields_frame, text="NIF / Tax ID", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=6, column=0, sticky="w", pady=(0, 8))
        self.nif_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Número de identificação fiscal...",
            height=35
        )
        self.nif_entry.grid(row=7, column=0, sticky="ew", pady=(0, 18))

        # País
        ctk.CTkLabel(fields_frame, text="País", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=8, column=0, sticky="w", pady=(0, 8))
        self.pais_entry = ctk.CTkEntry(fields_frame, placeholder_text="Portugal", height=35)
        self.pais_entry.grid(row=9, column=0, sticky="ew", pady=(0, 18))

        # Morada
        ctk.CTkLabel(fields_frame, text="Morada", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=10, column=0, sticky="w", pady=(0, 8))
        self.morada_entry = ctk.CTkTextbox(fields_frame, height=60)
        self.morada_entry.grid(row=11, column=0, sticky="ew", pady=(0, 18))

        # Contacto e Email (side by side)
        contacto_email_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        contacto_email_frame.grid(row=12, column=0, sticky="ew", pady=(0, 18))
        contacto_email_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(contacto_email_frame, text="Contacto", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 12))
        self.contacto_entry = ctk.CTkEntry(contacto_email_frame, placeholder_text="Telefone...", height=35)
        self.contacto_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(8, 0))

        ctk.CTkLabel(contacto_email_frame, text="Email", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=1, sticky="w")
        self.email_entry = ctk.CTkEntry(contacto_email_frame, placeholder_text="email@exemplo.pt", height=35)
        self.email_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))

        # Angariação
        ctk.CTkLabel(fields_frame, text="Angariação", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=13, column=0, sticky="w", pady=(0, 8))
        self.angariacao_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Como foi angariado este cliente...",
            height=35
        )
        self.angariacao_entry.grid(row=14, column=0, sticky="ew", pady=(0, 18))

        # Nota
        ctk.CTkLabel(fields_frame, text="Nota", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=15, column=0, sticky="w", pady=(0, 8))
        self.nota_entry = ctk.CTkTextbox(fields_frame, height=80)
        self.nota_entry.grid(row=16, column=0, sticky="ew", pady=(0, 10))

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

    def carregar_cliente(self):
        """Carrega dados do cliente para edição"""
        self.cliente = self.manager.buscar_por_id(self.cliente_id)
        if not self.cliente:
            messagebox.showerror("Erro", "Cliente não encontrado!")
            self.voltar()
            return

        # Atualizar título
        self.title_label.configure(text=f"Editar Cliente {self.cliente.numero}")

        c = self.cliente

        # Nome
        self.nome_entry.insert(0, c.nome)

        # Nome Formal
        if c.nome_formal:
            self.nome_formal_entry.insert(0, c.nome_formal)

        # NIF
        if c.nif:
            self.nif_entry.insert(0, c.nif)

        # País
        if c.pais:
            self.pais_entry.insert(0, c.pais)

        # Morada
        if c.morada:
            self.morada_entry.insert("1.0", c.morada)

        # Contacto
        if c.contacto:
            self.contacto_entry.insert(0, c.contacto)

        # Email
        if c.email:
            self.email_entry.insert(0, c.email)

        # Angariação
        if c.angariacao:
            self.angariacao_entry.insert(0, c.angariacao)

        # Nota
        if c.nota:
            self.nota_entry.insert("1.0", c.nota)

    def guardar(self):
        """Guarda o cliente"""
        try:
            # Get values
            nome = self.nome_entry.get().strip()
            nome_formal = self.nome_formal_entry.get().strip()
            nif = self.nif_entry.get().strip()
            pais = self.pais_entry.get().strip() or "Portugal"
            morada = self.morada_entry.get("1.0", "end-1c").strip()
            contacto = self.contacto_entry.get().strip()
            email = self.email_entry.get().strip()
            angariacao = self.angariacao_entry.get().strip()
            nota = self.nota_entry.get("1.0", "end-1c").strip()

            # Validate
            if not nome:
                messagebox.showerror("Erro", "Nome é obrigatório")
                return

            # Create or update
            if self.cliente_id:
                # Update
                success, cliente, message = self.manager.atualizar(
                    self.cliente_id,
                    nome=nome,
                    nome_formal=nome_formal if nome_formal else None,
                    nif=nif if nif else None,
                    pais=pais,
                    morada=morada if morada else None,
                    contacto=contacto if contacto else None,
                    email=email if email else None,
                    angariacao=angariacao if angariacao else None,
                    nota=nota if nota else None
                )

                if success:
                    self.voltar()
                else:
                    messagebox.showerror("Erro", message)
            else:
                # Create
                success, cliente, message = self.manager.criar(
                    nome=nome,
                    nome_formal=nome_formal if nome_formal else None,
                    nif=nif if nif else None,
                    pais=pais,
                    morada=morada if morada else None,
                    contacto=contacto if contacto else None,
                    email=email if email else None,
                    angariacao=angariacao if angariacao else None,
                    nota=nota if nota else None
                )

                if success:
                    self.voltar()
                else:
                    messagebox.showerror("Erro", message)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def voltar(self):
        """Volta para a lista de clientes"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("clientes")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")
