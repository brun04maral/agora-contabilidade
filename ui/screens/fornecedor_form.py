# -*- coding: utf-8 -*-
"""
FornecedorFormScreen - Formulário para criar/editar fornecedores

Migrado para BaseForm framework (SPRINT 3)
Segue padrão estabelecido em ui/components/base_form.py
"""

import customtkinter as ctk
from typing import List, Dict, Any, Optional
import re
from sqlalchemy.orm import Session
from tkinter import messagebox

from ui.components.base_form import BaseForm
from logic.fornecedores import FornecedoresManager
from database.models import EstatutoFornecedor
from assets.resources import get_icon, FORNECEDORES


class FornecedorFormScreen(BaseForm):
    """
    Formulário para criar/editar fornecedores

    Navegação via MainWindow.show_screen("fornecedor_form", fornecedor_id=None/ID)

    Modos:
    - CREATE: fornecedor_id=None
    - EDIT: fornecedor_id=<id>
    """

    def __init__(self, parent, db_session: Session, fornecedor_id: Optional[int] = None, **kwargs):
        """
        Initialize fornecedor form screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            fornecedor_id: ID do fornecedor (None para criar, ID para editar)
        """
        self.db_session = db_session
        self.fornecedor_id = fornecedor_id
        self.manager = FornecedoresManager(db_session)

        # Load initial data if editing
        initial_data = {}
        if fornecedor_id:
            fornecedor = self.manager.buscar_por_id(fornecedor_id)
            if fornecedor:
                initial_data = {
                    'nome': fornecedor.nome,
                    'estatuto': fornecedor.estatuto.value if fornecedor.estatuto else 'FREELANCER',
                    'area': fornecedor.area or '',
                    'funcao': fornecedor.funcao or '',
                    'classificacao': str(fornecedor.classificacao or 0),
                    'nif': fornecedor.nif or '',
                    'iban': fornecedor.iban or '',
                    'morada': fornecedor.morada or '',
                    'contacto': fornecedor.contacto or '',
                    'email': fornecedor.email or '',
                    'website': fornecedor.website or '',
                    'nota': fornecedor.nota or '',
                }
            else:
                messagebox.showerror("Erro", "Fornecedor não encontrado!")
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
        if self.fornecedor_id:
            return "Editar Fornecedor"
        return "Novo Fornecedor"

    def get_form_icon(self):
        """Return form icon"""
        return get_icon(FORNECEDORES, size=(28, 28))

    def get_fields_config(self) -> List[Dict[str, Any]]:
        """
        Return field configurations for fornecedor form

        Campos:
        - nome (required)
        - estatuto (dropdown: EMPRESA, FREELANCER, ESTADO)
        - area
        - funcao
        - classificacao (0-5 stars)
        - nif (validator)
        - iban
        - morada (textarea)
        - contacto
        - email (validator)
        - website
        - nota (textarea)
        """
        return [
            # Nome (required)
            {
                "key": "nome",
                "label": "Nome",
                "type": "text",
                "required": True,
                "placeholder": "Nome do fornecedor...",
                "width": 500
            },

            # Estatuto (dropdown com enum)
            {
                "key": "estatuto",
                "label": "Estatuto",
                "type": "dropdown",
                "values": ["EMPRESA", "FREELANCER", "ESTADO"],
                "default": "FREELANCER",
                "required": True,
                "width": 200
            },

            # Área
            {
                "key": "area",
                "label": "Área",
                "type": "text",
                "placeholder": "Ex: Produção, Som...",
                "width": 300
            },

            # Função
            {
                "key": "funcao",
                "label": "Função",
                "type": "text",
                "placeholder": "Ex: Editor, Realizador...",
                "width": 300
            },

            # Classificação (0-5 stars)
            {
                "key": "classificacao",
                "label": "Classificação (0-5 estrelas)",
                "type": "number",
                "default": "0",
                "placeholder": "0-5",
                "validator": self._validate_classificacao,
                "width": 150
            },

            # NIF (com validador)
            {
                "key": "nif",
                "label": "NIF / Tax ID",
                "type": "text",
                "placeholder": "Número fiscal...",
                "validator": self._validate_nif,
                "width": 300
            },

            # IBAN
            {
                "key": "iban",
                "label": "IBAN",
                "type": "text",
                "placeholder": "PT50...",
                "width": 400
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

            # Website
            {
                "key": "website",
                "label": "Website",
                "type": "text",
                "placeholder": "https://exemplo.pt",
                "width": 400
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
        Handle save - create or update fornecedor

        Args:
            data: Dict com todos os valores do form

        Returns:
            True se sucesso, ou mensagem de erro
        """
        try:
            # Prepare data (convert empty strings to None)
            nome = data.get('nome', '').strip()
            estatuto_str = data.get('estatuto', 'FREELANCER').strip()
            area = data.get('area', '').strip() or None
            funcao = data.get('funcao', '').strip() or None
            classificacao_str = data.get('classificacao', '0').strip()
            nif = data.get('nif', '').strip() or None
            iban = data.get('iban', '').strip() or None
            morada = data.get('morada', '').strip() or None
            contacto = data.get('contacto', '').strip() or None
            email = data.get('email', '').strip() or None
            website = data.get('website', '').strip() or None
            nota = data.get('nota', '').strip() or None

            # Validate nome (BaseForm já valida required, mas double check)
            if not nome:
                return "Nome é obrigatório"

            # Parse estatuto enum
            try:
                estatuto = EstatutoFornecedor[estatuto_str]
            except (KeyError, AttributeError):
                return "Estatuto inválido"

            # Parse classificacao
            try:
                classificacao = int(classificacao_str) if classificacao_str else 0
                if classificacao < 0 or classificacao > 5:
                    return "Classificação deve estar entre 0 e 5"
            except ValueError:
                return "Classificação inválida"

            # Validate NIF if provided
            if nif and not self._validate_nif(nif):
                return "NIF inválido"

            # Validate email if provided
            if email and not self._validate_email(email):
                return "Email inválido"

            # Create or update
            if self.fornecedor_id:
                # UPDATE
                success, fornecedor, message = self.manager.atualizar(
                    self.fornecedor_id,
                    nome=nome,
                    estatuto=estatuto,
                    area=area,
                    funcao=funcao,
                    classificacao=classificacao if classificacao > 0 else None,
                    nif=nif,
                    iban=iban,
                    morada=morada,
                    contacto=contacto,
                    email=email,
                    website=website,
                    validade_seguro_trabalho=None,  # Campo removido nesta migração
                    nota=nota
                )

                if not success:
                    return message or "Erro ao atualizar fornecedor"

            else:
                # CREATE
                success, fornecedor, message = self.manager.criar(
                    nome=nome,
                    estatuto=estatuto,
                    area=area,
                    funcao=funcao,
                    classificacao=classificacao if classificacao > 0 else None,
                    nif=nif,
                    iban=iban,
                    morada=morada,
                    contacto=contacto,
                    email=email,
                    website=website,
                    validade_seguro_trabalho=None,  # Campo removido nesta migração
                    nota=nota
                )

                if not success:
                    return message or "Erro ao criar fornecedor"

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

    def _validate_classificacao(self, classificacao: str) -> bool:
        """
        Valida classificação (0-5 estrelas)

        Args:
            classificacao: Classificação a validar

        Returns:
            True se válido, False caso contrário
        """
        if not classificacao:
            return True  # Pode ser vazio (default 0)

        try:
            valor = int(classificacao)
            return 0 <= valor <= 5
        except ValueError:
            return False

    # ===== CALLBACKS =====

    def after_save_callback(self):
        """
        Executado após save bem-sucedido

        Navega de volta para lista de fornecedores
        """
        self._voltar_para_lista()

    def after_cancel_callback(self):
        """
        Executado após cancelar

        Confirma e navega de volta para lista de fornecedores
        """
        resposta = messagebox.askyesno(
            "Cancelar",
            "Tem certeza que deseja cancelar?\n\nTodas as alterações serão perdidas."
        )

        if resposta:
            self._voltar_para_lista()

    # ===== HELPERS =====

    def _voltar_para_lista(self):
        """Navega de volta para lista de fornecedores"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("fornecedores")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")
