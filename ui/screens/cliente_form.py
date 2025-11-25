# -*- coding: utf-8 -*-
"""
ClienteFormScreen - Formulário para criar/editar clientes

Migrado para BaseForm framework (SPRINT 2)
Segue padrão estabelecido em ui/components/base_form.py
"""

import customtkinter as ctk
from typing import List, Dict, Any, Optional
import re
from sqlalchemy.orm import Session
from tkinter import messagebox

from ui.components.base_form import BaseForm
from logic.clientes import ClientesManager
from assets.resources import get_icon, CLIENTES


class ClienteFormScreen(BaseForm):
    """
    Formulário para criar/editar clientes

    Navegação via MainWindow.show_screen("cliente_form", cliente_id=None/ID)

    Modos:
    - CREATE: cliente_id=None
    - EDIT: cliente_id=<id>
    """

    def __init__(self, parent, db_session: Session, cliente_id: Optional[int] = None, **kwargs):
        """
        Initialize cliente form screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            cliente_id: ID do cliente (None para criar, ID para editar)
        """
        self.db_session = db_session
        self.cliente_id = cliente_id
        self.manager = ClientesManager(db_session)

        # Load initial data if editing
        initial_data = {}
        if cliente_id:
            cliente = self.manager.buscar_por_id(cliente_id)
            if cliente:
                initial_data = {
                    'nome': cliente.nome,
                    'nome_formal': cliente.nome_formal or '',
                    'nif': cliente.nif or '',
                    'pais': cliente.pais or 'Portugal',
                    'morada': cliente.morada or '',
                    'contacto': cliente.contacto or '',
                    'email': cliente.email or '',
                    'angariacao': cliente.angariacao or '',
                    'nota': cliente.nota or '',
                }
            else:
                messagebox.showerror("Erro", "Cliente não encontrado!")
                # Will call after_cancel_callback to go back
                kwargs['on_cancel_callback'] = self._voltar_para_lista

        # Initialize BaseForm
        super().__init__(
            parent,
            db_session=db_session,
            initial_data=initial_data,
            on_cancel_callback=self._voltar_para_lista,
            **kwargs
        )

    # ===== MÉTODOS ABSTRATOS OBRIGATÓRIOS =====

    def get_form_title(self) -> str:
        """Return form title"""
        if self.cliente_id:
            return "Editar Cliente"
        return "Novo Cliente"

    def get_form_icon(self):
        """Return form icon"""
        return get_icon(CLIENTES, size=(28, 28))

    def get_fields_config(self) -> List[Dict[str, Any]]:
        """
        Return field configurations for cliente form

        Campos:
        - nome (required)
        - nome_formal
        - nif (validator)
        - pais (default: Portugal)
        - morada (textarea)
        - contacto
        - email (validator)
        - angariacao
        - nota (textarea)
        """
        return [
            # Nome (required)
            {
                "key": "nome",
                "label": "Nome",
                "type": "text",
                "required": True,
                "placeholder": "Ex: Farmácia do Povo",
                "width": 500
            },

            # Nome Formal (opcional)
            {
                "key": "nome_formal",
                "label": "Nome Formal",
                "type": "text",
                "placeholder": "Ex: Farmácia Popular do Centro, Lda.",
                "width": 500
            },

            # NIF (com validador)
            {
                "key": "nif",
                "label": "NIF / Tax ID",
                "type": "text",
                "placeholder": "Número de identificação fiscal...",
                "validator": self._validate_nif,
                "width": 300
            },

            # País (default: Portugal)
            {
                "key": "pais",
                "label": "País",
                "type": "text",
                "default": "Portugal",
                "placeholder": "Portugal",
                "width": 300
            },

            # Morada (textarea)
            {
                "key": "morada",
                "label": "Morada",
                "type": "textarea",
                "placeholder": "Endereço completo...",
                "width": 500
            },

            # Contacto
            {
                "key": "contacto",
                "label": "Contacto",
                "type": "text",
                "placeholder": "Telefone...",
                "width": 300
            },

            # Email (com validador)
            {
                "key": "email",
                "label": "Email",
                "type": "text",
                "placeholder": "email@exemplo.pt",
                "validator": self._validate_email,
                "width": 400
            },

            # Angariação
            {
                "key": "angariacao",
                "label": "Angariação",
                "type": "text",
                "placeholder": "Como foi angariado este cliente...",
                "width": 500
            },

            # Nota (textarea)
            {
                "key": "nota",
                "label": "Nota",
                "type": "textarea",
                "placeholder": "Observações adicionais...",
                "width": 500
            },
        ]

    def on_save(self, data: Dict[str, Any]) -> bool | str:
        """
        Handle save - create or update cliente

        Args:
            data: Dict com todos os valores do form

        Returns:
            True se sucesso, ou mensagem de erro
        """
        try:
            # Prepare data (convert empty strings to None)
            nome = data.get('nome', '').strip()
            nome_formal = data.get('nome_formal', '').strip() or None
            nif = data.get('nif', '').strip() or None
            pais = data.get('pais', '').strip() or 'Portugal'
            morada = data.get('morada', '').strip() or None
            contacto = data.get('contacto', '').strip() or None
            email = data.get('email', '').strip() or None
            angariacao = data.get('angariacao', '').strip() or None
            nota = data.get('nota', '').strip() or None

            # Validate nome (BaseForm já valida required, mas double check)
            if not nome:
                return "Nome é obrigatório"

            # Validate NIF if provided (já foi validado pelo validator, mas double check)
            if nif and not self._validate_nif(nif):
                return "NIF inválido"

            # Validate email if provided
            if email and not self._validate_email(email):
                return "Email inválido"

            # Create or update
            if self.cliente_id:
                # UPDATE
                success, cliente, message = self.manager.atualizar(
                    self.cliente_id,
                    nome=nome,
                    nome_formal=nome_formal,
                    nif=nif,
                    pais=pais,
                    morada=morada,
                    contacto=contacto,
                    email=email,
                    angariacao=angariacao,
                    nota=nota
                )

                if not success:
                    return message or "Erro ao atualizar cliente"

            else:
                # CREATE
                success, cliente, message = self.manager.criar(
                    nome=nome,
                    nome_formal=nome_formal,
                    nif=nif,
                    pais=pais,
                    morada=morada,
                    contacto=contacto,
                    email=email,
                    angariacao=angariacao,
                    nota=nota
                )

                if not success:
                    return message or "Erro ao criar cliente"

            # Success!
            return True

        except Exception as e:
            return f"Erro inesperado: {str(e)}"

    # ===== VALIDADORES =====

    def _validate_nif(self, nif: str) -> bool:
        """
        Valida NIF (Número de Identificação Fiscal)

        Regras simples:
        - Deve ter entre 9 e 20 dígitos/caracteres
        - Aceita números, letras e alguns caracteres especiais

        Args:
            nif: NIF a validar

        Returns:
            True se válido, False caso contrário
        """
        if not nif:
            return True  # NIF é opcional

        # Remove espaços
        nif_clean = nif.strip()

        # Deve ter pelo menos 9 caracteres
        if len(nif_clean) < 9:
            return False

        # Não deve ter mais de 20 caracteres
        if len(nif_clean) > 20:
            return False

        # Aceita alfanuméricos e alguns caracteres especiais (-, /, espaço)
        if not re.match(r'^[A-Za-z0-9\s\-/]+$', nif_clean):
            return False

        return True

    def _validate_email(self, email: str) -> bool:
        """
        Valida email

        Regras simples:
        - Formato básico: algo@algo.algo

        Args:
            email: Email a validar

        Returns:
            True se válido, False caso contrário
        """
        if not email:
            return True  # Email é opcional

        # Remove espaços
        email_clean = email.strip()

        # Regex simples para validar email
        # Formato: local@domain.tld
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        return bool(re.match(pattern, email_clean))

    # ===== CALLBACKS =====

    def after_save_callback(self):
        """
        Executado após save bem-sucedido

        Navega de volta para lista de clientes
        """
        self._voltar_para_lista()

    def after_cancel_callback(self):
        """
        Executado após cancelar

        Confirma e navega de volta para lista de clientes
        """
        resposta = messagebox.askyesno(
            "Cancelar",
            "Tem certeza que deseja cancelar?\n\nTodas as alterações serão perdidas."
        )

        if resposta:
            self._voltar_para_lista()

    # ===== HELPERS =====

    def _voltar_para_lista(self):
        """Navega de volta para lista de clientes"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("clientes")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")
