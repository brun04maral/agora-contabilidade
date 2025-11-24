# -*- coding: utf-8 -*-
"""
Formulário de Equipamento - Screen dedicado para criar/editar equipamento
"""
import customtkinter as ctk
from typing import Optional
from sqlalchemy.orm import Session
from tkinter import messagebox

from logic.equipamento import EquipamentoManager
from ui.components.date_picker_dropdown import DatePickerDropdown


class EquipamentoFormScreen(ctk.CTkFrame):
    """
    Screen dedicado para criar/editar equipamento
    """

    def __init__(self, parent, db_session: Session, equipamento_id: Optional[int] = None, **kwargs):
        """
        Initialize equipamento form screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            equipamento_id: ID do equipamento para editar (None = criar novo)
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = EquipamentoManager(db_session)
        self.equipamento_id = equipamento_id
        self.equipamento = None

        # Load equipamento if editing
        if equipamento_id:
            self.equipamento = self.manager.obter_equipamento(equipamento_id)
            if not self.equipamento:
                messagebox.showerror("Erro", "Equipamento não encontrado")
                self.voltar()
                return

        # Configure
        self.configure(fg_color="transparent")

        # Layout with grid for proper scroll support
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.create_widgets()

        # Load data if editing
        if self.equipamento:
            self.load_data()

    def create_widgets(self):
        """Create screen widgets"""

        # Main scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Back button
        back_btn = ctk.CTkButton(
            header_frame,
            text="< Voltar",
            command=self.voltar,
            width=100,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        back_btn.pack(side="left")

        # Title
        if self.equipamento:
            title_text = f"Editar Equipamento #{self.equipamento.numero}"
        else:
            title_text = "Novo Equipamento"

        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20)

        # Form container
        form_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        form_frame.grid(row=1, column=0, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)

        current_row = 0

        # ID (auto-generated or display)
        if not self.equipamento:
            proximo = self.manager.proximo_numero()
            id_label = ctk.CTkLabel(
                form_frame,
                text=f"ID: {proximo}",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            id_label.grid(row=current_row, column=0, sticky="w", pady=(0, 15))
            self.numero_value = proximo
        else:
            id_label = ctk.CTkLabel(
                form_frame,
                text=f"ID: {self.equipamento.numero}",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            id_label.grid(row=current_row, column=0, sticky="w", pady=(0, 15))
            self.numero_value = self.equipamento.numero
        current_row += 1

        # Produto *
        ctk.CTkLabel(
            form_frame,
            text="Produto *",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=current_row, column=0, sticky="w", pady=(10, 5))
        current_row += 1

        self.produto_entry = ctk.CTkEntry(form_frame, height=35)
        self.produto_entry.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        current_row += 1

        # Tipo e Label (2 columns)
        tipo_label_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        tipo_label_frame.grid(row=current_row, column=0, sticky="ew", pady=(10, 10))
        tipo_label_frame.grid_columnconfigure((0, 1), weight=1)
        current_row += 1

        # Tipo
        tipo_col = ctk.CTkFrame(tipo_label_frame, fg_color="transparent")
        tipo_col.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(tipo_col, text="Tipo", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.tipo_entry = ctk.CTkEntry(tipo_col, placeholder_text="Ex: Vídeo, Áudio, Iluminação", height=35)
        self.tipo_entry.pack(fill="x")

        # Label
        label_col = ctk.CTkFrame(tipo_label_frame, fg_color="transparent")
        label_col.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(label_col, text="Label/Categoria", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.label_entry = ctk.CTkEntry(label_col, placeholder_text="Categoria", height=35)
        self.label_entry.pack(fill="x")

        # Descrição
        ctk.CTkLabel(
            form_frame,
            text="Descrição",
            font=ctk.CTkFont(size=13)
        ).grid(row=current_row, column=0, sticky="w", pady=(10, 5))
        current_row += 1

        self.descricao_entry = ctk.CTkTextbox(form_frame, height=60)
        self.descricao_entry.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        current_row += 1

        # Valores (2 columns)
        valores_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        valores_frame.grid(row=current_row, column=0, sticky="ew", pady=(10, 10))
        valores_frame.grid_columnconfigure((0, 1), weight=1)
        current_row += 1

        # Valor compra
        left_frame = ctk.CTkFrame(valores_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(left_frame, text="Valor Compra (€)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.valor_compra_entry = ctk.CTkEntry(left_frame, placeholder_text="0.00", height=35)
        self.valor_compra_entry.pack(fill="x")

        # Preço aluguer
        right_frame = ctk.CTkFrame(valores_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(right_frame, text="Preço Aluguer/dia (€)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.preco_aluguer_entry = ctk.CTkEntry(right_frame, placeholder_text="0.00", height=35)
        self.preco_aluguer_entry.pack(fill="x")

        # Quantidade e Estado (2 columns)
        detalhes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        detalhes_frame.grid(row=current_row, column=0, sticky="ew", pady=(10, 10))
        detalhes_frame.grid_columnconfigure((0, 1), weight=1)
        current_row += 1

        # Quantidade
        qtd_frame = ctk.CTkFrame(detalhes_frame, fg_color="transparent")
        qtd_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(qtd_frame, text="Quantidade", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.quantidade_entry = ctk.CTkEntry(qtd_frame, placeholder_text="1", height=35)
        self.quantidade_entry.pack(fill="x")

        # Estado
        estado_frame = ctk.CTkFrame(detalhes_frame, fg_color="transparent")
        estado_frame.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(estado_frame, text="Estado", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.estado_entry = ctk.CTkEntry(estado_frame, placeholder_text="Novo, Usado, etc", height=35)
        self.estado_entry.pack(fill="x")

        # Fornecedor e Data de Compra (2 columns)
        fornecedor_data_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fornecedor_data_frame.grid(row=current_row, column=0, sticky="ew", pady=(10, 10))
        fornecedor_data_frame.grid_columnconfigure((0, 1), weight=1)
        current_row += 1

        # Fornecedor
        fornecedor_col = ctk.CTkFrame(fornecedor_data_frame, fg_color="transparent")
        fornecedor_col.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(fornecedor_col, text="Fornecedor", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.fornecedor_entry = ctk.CTkEntry(fornecedor_col, height=35)
        self.fornecedor_entry.pack(fill="x")

        # Data de Compra
        data_col = ctk.CTkFrame(fornecedor_data_frame, fg_color="transparent")
        data_col.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(data_col, text="Data Compra", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.data_compra_picker = DatePickerDropdown(data_col, placeholder="Selecionar data de compra...")
        self.data_compra_picker.pack(fill="x")

        # Especificações técnicas (3 columns)
        specs_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        specs_frame.grid(row=current_row, column=0, sticky="ew", pady=(10, 10))
        specs_frame.grid_columnconfigure((0, 1, 2), weight=1)
        current_row += 1

        # Número de Série
        serie_col = ctk.CTkFrame(specs_frame, fg_color="transparent")
        serie_col.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(serie_col, text="Nº Série", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.numero_serie_entry = ctk.CTkEntry(serie_col, height=35)
        self.numero_serie_entry.pack(fill="x")

        # MAC Address
        mac_col = ctk.CTkFrame(specs_frame, fg_color="transparent")
        mac_col.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(mac_col, text="MAC Address", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.mac_address_entry = ctk.CTkEntry(mac_col, height=35)
        self.mac_address_entry.pack(fill="x")

        # Referência
        ref_col = ctk.CTkFrame(specs_frame, fg_color="transparent")
        ref_col.grid(row=0, column=2, sticky="ew")
        ctk.CTkLabel(ref_col, text="Referência", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.referencia_entry = ctk.CTkEntry(ref_col, height=35)
        self.referencia_entry.pack(fill="x")

        # Tamanho, Localização, Uso Pessoal (3 columns)
        outros_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        outros_frame.grid(row=current_row, column=0, sticky="ew", pady=(10, 10))
        outros_frame.grid_columnconfigure((0, 1, 2), weight=1)
        current_row += 1

        # Tamanho
        tamanho_col = ctk.CTkFrame(outros_frame, fg_color="transparent")
        tamanho_col.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(tamanho_col, text="Tamanho", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.tamanho_entry = ctk.CTkEntry(tamanho_col, height=35)
        self.tamanho_entry.pack(fill="x")

        # Localização
        loc_col = ctk.CTkFrame(outros_frame, fg_color="transparent")
        loc_col.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(loc_col, text="Localização", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.localizacao_entry = ctk.CTkEntry(loc_col, height=35)
        self.localizacao_entry.pack(fill="x")

        # Uso Pessoal
        uso_col = ctk.CTkFrame(outros_frame, fg_color="transparent")
        uso_col.grid(row=0, column=2, sticky="ew")
        ctk.CTkLabel(uso_col, text="Uso Pessoal", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.uso_pessoal_entry = ctk.CTkEntry(uso_col, placeholder_text="BA, RR, Empresa", height=35)
        self.uso_pessoal_entry.pack(fill="x")

        # URLs (Fatura e Foto)
        urls_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        urls_frame.grid(row=current_row, column=0, sticky="ew", pady=(10, 10))
        urls_frame.grid_columnconfigure((0, 1), weight=1)
        current_row += 1

        # Fatura URL
        fatura_col = ctk.CTkFrame(urls_frame, fg_color="transparent")
        fatura_col.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(fatura_col, text="URL Fatura", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.fatura_url_entry = ctk.CTkEntry(fatura_col, height=35)
        self.fatura_url_entry.pack(fill="x")

        # Foto URL
        foto_col = ctk.CTkFrame(urls_frame, fg_color="transparent")
        foto_col.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(foto_col, text="URL Foto", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.foto_url_entry = ctk.CTkEntry(foto_col, height=35)
        self.foto_url_entry.pack(fill="x")

        # Nota
        ctk.CTkLabel(
            form_frame,
            text="Nota",
            font=ctk.CTkFont(size=13)
        ).grid(row=current_row, column=0, sticky="w", pady=(10, 5))
        current_row += 1

        self.nota_entry = ctk.CTkTextbox(form_frame, height=60)
        self.nota_entry.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        current_row += 1

        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=current_row, column=0, sticky="ew", pady=(20, 0))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.voltar,
            width=140,
            height=40,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=self.guardar,
            width=140,
            height=40,
            fg_color=("#2196F3", "#1565C0"),
            hover_color=("#1976D2", "#0D47A1")
        )
        save_btn.pack(side="right")

    def load_data(self):
        """Load equipamento data into form"""
        if not self.equipamento:
            return

        # Identificação
        self.produto_entry.insert(0, self.equipamento.produto or "")
        self.tipo_entry.insert(0, self.equipamento.tipo or "")
        self.label_entry.insert(0, self.equipamento.label or "")

        if self.equipamento.descricao:
            self.descricao_entry.insert("1.0", self.equipamento.descricao)

        # Valores
        self.valor_compra_entry.insert(0, str(float(self.equipamento.valor_compra or 0)))
        self.preco_aluguer_entry.insert(0, str(float(self.equipamento.preco_aluguer or 0)))

        # Quantidade e Estado
        self.quantidade_entry.insert(0, str(self.equipamento.quantidade or 1))
        self.estado_entry.insert(0, self.equipamento.estado or "")

        # Fornecedor e Data
        self.fornecedor_entry.insert(0, self.equipamento.fornecedor or "")
        if self.equipamento.data_compra:
            self.data_compra_picker.set_date(self.equipamento.data_compra)

        # Especificações técnicas
        self.numero_serie_entry.insert(0, self.equipamento.numero_serie or "")
        self.mac_address_entry.insert(0, self.equipamento.mac_address or "")
        self.referencia_entry.insert(0, self.equipamento.referencia or "")

        # Outros
        self.tamanho_entry.insert(0, self.equipamento.tamanho or "")
        self.localizacao_entry.insert(0, self.equipamento.localizacao or "")
        self.uso_pessoal_entry.insert(0, self.equipamento.uso_pessoal or "")

        # URLs
        self.fatura_url_entry.insert(0, self.equipamento.fatura_url or "")
        self.foto_url_entry.insert(0, self.equipamento.foto_url or "")

        # Nota
        if self.equipamento.nota:
            self.nota_entry.insert("1.0", self.equipamento.nota)

    def guardar(self):
        """Save equipamento"""
        # Validate
        produto = self.produto_entry.get().strip()
        if not produto:
            messagebox.showerror("Erro", "Produto é obrigatório")
            return

        # Parse valores
        try:
            valor_compra = float(self.valor_compra_entry.get().strip() or 0)
            preco_aluguer = float(self.preco_aluguer_entry.get().strip() or 0)
            quantidade = int(self.quantidade_entry.get().strip() or 1)
        except ValueError:
            messagebox.showerror("Erro", "Valores numéricos inválidos")
            return

        # Parse data de compra
        data_compra = None
        if self.data_compra_picker.get():
            data_compra = self.data_compra_picker.get_date()

        # Prepare data
        data = {
            "produto": produto,
            "tipo": self.tipo_entry.get().strip() or None,
            "label": self.label_entry.get().strip() or None,
            "descricao": self.descricao_entry.get("1.0", "end-1c").strip() or None,
            "valor_compra": valor_compra,
            "preco_aluguer": preco_aluguer,
            "quantidade": quantidade,
            "estado": self.estado_entry.get().strip() or None,
            "fornecedor": self.fornecedor_entry.get().strip() or None,
            "data_compra": data_compra,
            "numero_serie": self.numero_serie_entry.get().strip() or None,
            "mac_address": self.mac_address_entry.get().strip() or None,
            "referencia": self.referencia_entry.get().strip() or None,
            "tamanho": self.tamanho_entry.get().strip() or None,
            "localizacao": self.localizacao_entry.get().strip() or None,
            "uso_pessoal": self.uso_pessoal_entry.get().strip() or None,
            "fatura_url": self.fatura_url_entry.get().strip() or None,
            "foto_url": self.foto_url_entry.get().strip() or None,
            "nota": self.nota_entry.get("1.0", "end-1c").strip() or None,
        }

        # Save
        if self.equipamento:
            # Update
            sucesso, _, erro = self.manager.atualizar_equipamento(self.equipamento.id, **data)
        else:
            # Create
            sucesso, _, erro = self.manager.criar_equipamento(numero=self.numero_value, **data)

        if sucesso:
            self.voltar()
        else:
            messagebox.showerror("Erro", f"Erro ao guardar: {erro}")

    def voltar(self):
        """Navigate back to equipamento list"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("equipamento")
        elif hasattr(main_window, 'show_equipamento'):
            main_window.show_equipamento()
