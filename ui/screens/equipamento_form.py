# -*- coding: utf-8 -*-
"""
EquipamentoFormScreen - Formulário para criar/editar equipamento

Migrado para BaseForm framework (SPRINT 4)
Segue padrão estabelecido em ui/components/base_form.py
"""

import customtkinter as ctk
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from tkinter import messagebox

from ui.components.base_form import BaseForm
from logic.equipamento import EquipamentoManager
from assets.resources import get_icon, EQUIPAMENTO


class EquipamentoFormScreen(BaseForm):
    """
    Formulário para criar/editar equipamento

    Navegação via MainWindow.show_screen("equipamento_form", equipamento_id=None/ID)

    Modos:
    - CREATE: equipamento_id=None
    - EDIT: equipamento_id=<id>
    """

    def __init__(self, parent, db_session: Session, equipamento_id: Optional[int] = None, **kwargs):
        """
        Initialize equipamento form screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            equipamento_id: ID do equipamento (None para criar, ID para editar)
        """
        self.db_session = db_session
        self.equipamento_id = equipamento_id
        self.manager = EquipamentoManager(db_session)
        self.is_create = (equipamento_id is None)

        # Obter tipos ANTES de chamar super().__init__()
        # Remove "Todos" da lista (usado apenas para filtros, não para criar equipamento)
        tipos_raw = self.manager.obter_tipos()
        self.tipos_disponiveis = [t for t in tipos_raw if t != "Todos"]

        # Se lista vazia, adiciona opção default
        if not self.tipos_disponiveis:
            self.tipos_disponiveis = ["Vídeo", "Áudio", "Iluminação", "Outro"]

        # Load initial data if editing
        initial_data = {}
        if equipamento_id:
            equipamento = self.manager.obter_equipamento(equipamento_id)
            if equipamento:
                initial_data = {
                    'produto': equipamento.produto,
                    'tipo': equipamento.tipo or '',
                    'valor_compra': str(float(equipamento.valor_compra)) if equipamento.valor_compra else '0',
                    'preco_aluguer': str(float(equipamento.preco_aluguer)) if equipamento.preco_aluguer else '',
                    'quantidade': str(equipamento.quantidade) if equipamento.quantidade else '1',
                    'estado': equipamento.estado or '',
                    'fornecedor': equipamento.fornecedor or '',
                    'data_compra': equipamento.data_compra,  # date object ou None
                    'garantia_ate': None,  # Campo novo, não existe no legacy
                    'notas': equipamento.nota or '',
                }
            else:
                messagebox.showerror("Erro", "Equipamento não encontrado!")
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
        if self.equipamento_id:
            return "Editar Equipamento"
        return "Novo Equipamento"

    def get_form_icon(self):
        """Return form icon"""
        return get_icon(EQUIPAMENTO, size=(28, 28))

    def get_fields_config(self) -> List[Dict[str, Any]]:
        """
        Return field configurations for equipamento form

        Campos:
        - produto (required)
        - tipo (dropdown dinâmico, required)
        - valor_compra (number, required, min=0)
        - preco_aluguer (number, min=0)
        - quantidade (number, required, min=1, default=1)
        - estado
        - fornecedor
        - data_compra (date)
        - garantia_ate (date)
        - notas (textarea)
        """
        return [
            # Produto (required)
            {
                "key": "produto",
                "label": "Produto",
                "type": "text",
                "required": True,
                "placeholder": "Nome do equipamento...",
                "width": 500
            },

            # Tipo (dropdown dinâmico, required)
            {
                "key": "tipo",
                "label": "Tipo",
                "type": "dropdown",
                "values": self.tipos_disponiveis,
                "required": True,
                "width": 300
            },

            # Valor Compra (required, min=0)
            {
                "key": "valor_compra",
                "label": "Valor Compra (€)",
                "type": "number",
                "required": True,
                "placeholder": "0.00",
                "validator": self._validate_valor_compra,
                "width": 250
            },

            # Preço Aluguer (opcional, min=0)
            {
                "key": "preco_aluguer",
                "label": "Preço Aluguer/dia (€)",
                "type": "number",
                "placeholder": "0.00",
                "validator": self._validate_preco_aluguer,
                "width": 250
            },

            # Quantidade (required, min=1, default=1)
            {
                "key": "quantidade",
                "label": "Quantidade",
                "type": "number",
                "required": True,
                "default": "1",
                "placeholder": "1",
                "validator": self._validate_quantidade,
                "width": 150
            },

            # Estado
            {
                "key": "estado",
                "label": "Estado",
                "type": "text",
                "placeholder": "Ex: Novo, Usado, Avariado...",
                "width": 300
            },

            # Fornecedor
            {
                "key": "fornecedor",
                "label": "Fornecedor",
                "type": "text",
                "placeholder": "Nome do fornecedor...",
                "width": 400
            },

            # Data Compra
            {
                "key": "data_compra",
                "label": "Data Compra",
                "type": "date",
            },

            # Garantia até
            {
                "key": "garantia_ate",
                "label": "Garantia até",
                "type": "date",
            },

            # Notas (textarea)
            {
                "key": "notas",
                "label": "Notas/Observações",
                "type": "textarea",
                "placeholder": "Observações adicionais sobre o equipamento...",
                "width": 500
            },
        ]

    def on_save(self, data: Dict[str, Any]) -> bool | str:
        """
        Handle save - create or update equipamento

        Args:
            data: Dict com todos os valores do form

        Returns:
            True se sucesso, ou mensagem de erro
        """
        try:
            # Prepare data (convert empty strings to None)
            produto = data.get('produto', '').strip()
            tipo = data.get('tipo', '').strip()
            estado = data.get('estado', '').strip() or None
            fornecedor = data.get('fornecedor', '').strip() or None
            notas = data.get('notas', '').strip() or None

            # Validate produto e tipo (BaseForm já valida required, mas double check)
            if not produto:
                return "Produto é obrigatório"

            if not tipo:
                return "Tipo é obrigatório"

            # Parse valores numéricos
            try:
                valor_compra_str = data.get('valor_compra', '').strip()
                if not valor_compra_str:
                    return "Valor de Compra é obrigatório"

                valor_compra = float(valor_compra_str)
                if valor_compra < 0:
                    return "Valor de Compra deve ser >= 0"

            except ValueError:
                return "Valor de Compra inválido"

            try:
                preco_aluguer_str = data.get('preco_aluguer', '').strip()
                if preco_aluguer_str:
                    preco_aluguer = float(preco_aluguer_str)
                    if preco_aluguer < 0:
                        return "Preço de Aluguer deve ser >= 0"
                else:
                    preco_aluguer = None

            except ValueError:
                return "Preço de Aluguer inválido"

            try:
                quantidade_str = data.get('quantidade', '').strip()
                if not quantidade_str:
                    return "Quantidade é obrigatória"

                quantidade = int(quantidade_str)
                if quantidade < 1:
                    return "Quantidade deve ser >= 1"

            except ValueError:
                return "Quantidade inválida (deve ser um número inteiro)"

            # Parse datas (BaseForm já retorna date objects ou None)
            data_compra = data.get('data_compra')  # date object ou None
            garantia_ate = data.get('garantia_ate')  # date object ou None

            # Prepare data dict for manager
            equipamento_data = {
                "produto": produto,
                "tipo": tipo,
                "valor_compra": valor_compra,
                "preco_aluguer": preco_aluguer,
                "quantidade": quantidade,
                "estado": estado,
                "fornecedor": fornecedor,
                "data_compra": data_compra,
                "nota": notas,  # Note: campo no DB é 'nota', não 'notas'
            }

            # Create or update
            if self.equipamento_id:
                # UPDATE
                sucesso, equipamento, erro = self.manager.atualizar_equipamento(
                    self.equipamento_id,
                    **equipamento_data
                )

                if not sucesso:
                    return erro or "Erro ao atualizar equipamento"

            else:
                # CREATE
                # Obter próximo número disponível
                proximo_numero = self.manager.proximo_numero()

                sucesso, equipamento, erro = self.manager.criar_equipamento(
                    numero=proximo_numero,
                    **equipamento_data
                )

                if not sucesso:
                    return erro or "Erro ao criar equipamento"

            # Success!
            return True

        except Exception as e:
            return f"Erro inesperado: {str(e)}"

    # ===== VALIDADORES =====

    def _validate_valor_compra(self, valor: str) -> bool:
        """
        Valida Valor de Compra

        Args:
            valor: Valor a validar

        Returns:
            True se válido, False caso contrário
        """
        if not valor:
            return False  # Obrigatório

        try:
            val = float(valor)
            return val >= 0
        except ValueError:
            return False

    def _validate_preco_aluguer(self, valor: str) -> bool:
        """
        Valida Preço de Aluguer

        Args:
            valor: Valor a validar

        Returns:
            True se válido, False caso contrário
        """
        if not valor:
            return True  # Opcional

        try:
            val = float(valor)
            return val >= 0
        except ValueError:
            return False

    def _validate_quantidade(self, valor: str) -> bool:
        """
        Valida Quantidade

        Args:
            valor: Valor a validar

        Returns:
            True se válido, False caso contrário
        """
        if not valor:
            return False  # Obrigatório

        try:
            val = int(valor)
            return val >= 1
        except ValueError:
            return False

    # ===== CALLBACKS =====

    def after_save_callback(self):
        """
        Executado após save bem-sucedido

        Navega de volta para lista de equipamento
        """
        self._voltar_para_lista()

    def after_cancel_callback(self):
        """
        Executado após cancelar

        Confirma e navega de volta para lista de equipamento
        """
        resposta = messagebox.askyesno(
            "Cancelar",
            "Tem certeza que deseja cancelar?\n\nTodas as alterações serão perdidas."
        )

        if resposta:
            self._voltar_para_lista()

    # ===== HELPERS =====

    def _voltar_para_lista(self):
        """Navega de volta para lista de equipamento"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("equipamento")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")
