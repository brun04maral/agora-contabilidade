# -*- coding: utf-8 -*-
"""
FormTesteScreen - Formulário de teste/demonstração do BaseForm

Este é um exemplo completo demonstrando todos os tipos de campo
suportados pelo framework BaseForm.

TIPOS DE CAMPO DEMONSTRADOS:
- text: Entry simples
- number: Entry com validação numérica
- dropdown: Menu dropdown com opções
- checkbox: Checkbox booleano
- date: DatePicker com calendário
- textarea: Campo de texto multilinha

FUNCIONALIDADES DEMONSTRADAS:
- Campos obrigatórios (required)
- Placeholders
- Valores default
- Validação automática
- Mensagens de erro
- Feedback após save
"""

import customtkinter as ctk
from typing import List, Dict, Any
from tkinter import messagebox
from ui.components.base_form import BaseForm
from assets.resources import get_icon, PROJECTS  # Usando ícone Projects como exemplo


class FormTesteScreen(BaseForm):
    """
    Formulário de teste demonstrando todos os tipos de campo do BaseForm
    """

    def __init__(self, parent, db_session=None, **kwargs):
        """
        Initialize form teste screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session (não usado neste teste)
        """
        # Initial data para demonstrar modo edit
        initial_data = kwargs.pop('initial_data', {
            'nome': 'João Silva',
            'idade': '25',
            'genero': 'M',
            'ativo': True,
            # nascimento será preenchido pelo default na config
            'observacoes': 'Este é um formulário de teste para demonstrar o BaseForm.'
        })

        super().__init__(
            parent,
            db_session=db_session,
            initial_data=initial_data,
            **kwargs
        )

    # ===== MÉTODOS ABSTRATOS OBRIGATÓRIOS =====

    def get_form_title(self) -> str:
        """Return form title"""
        return "Formulário de Teste - BaseForm Demo"

    def get_form_icon(self):
        """Return form icon"""
        # Usando ícone PROJECTS como exemplo (pode ser None)
        return get_icon(PROJECTS, size=(28, 28))

    def get_fields_config(self) -> List[Dict[str, Any]]:
        """
        Return field configurations demonstrating all supported types
        """
        return [
            # ===== TEXT FIELD =====
            {
                "key": "nome",
                "label": "Nome Completo",
                "type": "text",
                "required": True,
                "placeholder": "Digite o nome completo...",
                "width": 400
            },

            # ===== NUMBER FIELD =====
            {
                "key": "idade",
                "label": "Idade",
                "type": "number",
                "required": True,
                "placeholder": "18",
                "width": 150,
                "validator": self._validate_idade
            },

            # ===== DROPDOWN FIELD =====
            {
                "key": "genero",
                "label": "Género",
                "type": "dropdown",
                "values": ["M", "F", "Outro"],
                "default": "M",
                "required": True,
                "width": 200
            },

            # ===== CHECKBOX FIELD =====
            {
                "key": "ativo",
                "label": "Ativo no Sistema",
                "type": "checkbox",
                "default": True,
            },

            # ===== DATE FIELD =====
            {
                "key": "nascimento",
                "label": "Data de Nascimento",
                "type": "date",
                "required": True,
            },

            # ===== TEXTAREA FIELD =====
            {
                "key": "observacoes",
                "label": "Observações",
                "type": "textarea",
                "placeholder": "Digite observações adicionais...",
                "width": 400
            },

            # ===== READ-ONLY FIELD (DEMONSTRAÇÃO) =====
            {
                "key": "id_interno",
                "label": "ID Interno (Read-only)",
                "type": "text",
                "default": "AUTO-12345",
                "readonly": True,
                "width": 200
            }
        ]

    def on_save(self, data: Dict[str, Any]) -> bool | str:
        """
        Handle save - apenas demonstração (mostra data recebida)

        Args:
            data: Dict com todos os valores do form

        Returns:
            True se sucesso, ou mensagem de erro
        """
        # Validação adicional customizada (exemplo)
        if data.get('idade'):
            try:
                idade = int(data['idade'])
                if idade < 0 or idade > 150:
                    return "Idade inválida (deve estar entre 0 e 150)"
            except:
                return "Idade deve ser um número"

        # Simular save (apenas mostrar dados)
        msg = "📋 DADOS DO FORMULÁRIO:\n\n"
        msg += f"Nome: {data.get('nome', '-')}\n"
        msg += f"Idade: {data.get('idade', '-')}\n"
        msg += f"Género: {data.get('genero', '-')}\n"
        msg += f"Ativo: {'Sim' if data.get('ativo') else 'Não'}\n"
        msg += f"Nascimento: {data.get('nascimento', '-')}\n"
        msg += f"Observações: {data.get('observacoes', '-')[:50]}...\n"
        msg += f"ID Interno: {data.get('id_interno', '-')}\n"

        messagebox.showinfo("Form Teste - Dados Recebidos", msg)

        return True

    # ===== VALIDADORES CUSTOMIZADOS =====

    def _validate_idade(self, value) -> bool:
        """
        Validador customizado para idade

        Args:
            value: Valor a validar

        Returns:
            True se válido, False se inválido
        """
        try:
            idade = int(value)
            return 0 <= idade <= 150
        except:
            return False

    # ===== CALLBACKS (OPCIONAIS) =====

    def after_save_callback(self):
        """
        Executado após save bem-sucedido

        Demonstra como usar callbacks para ações pós-save
        """
        print("✅ FormTeste: Save bem-sucedido!")
        print("   Você pode executar ações adicionais aqui:")
        print("   - Fechar form")
        print("   - Navegar para outra tela")
        print("   - Atualizar listagem")
        print("   - etc.")

    def after_cancel_callback(self):
        """
        Executado após cancelar

        Demonstra como usar callbacks para ações pós-cancel
        """
        resposta = messagebox.askyesno(
            "Cancelar",
            "Tem certeza que deseja cancelar?\n\nTodas as alterações serão perdidas."
        )

        if resposta:
            print("❌ FormTeste: Cancelado pelo usuário")
            # Aqui você poderia:
            # - Fechar o form
            # - Voltar para tela anterior
            # - etc.
