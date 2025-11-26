# -*- coding: utf-8 -*-
"""
DespesaFormScreen - Formulário para criar/editar despesas

Migrado para BaseForm framework (SPRINT 5)
Segue padrão estabelecido em ui/components/base_form.py
"""

import customtkinter as ctk
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from tkinter import messagebox
from decimal import Decimal

from ui.components.base_form import BaseForm
from logic.despesas import DespesasManager
from assets.resources import get_icon, DESPESAS
from database.models.despesa import TipoDespesa, EstadoDespesa


class DespesaFormScreen(BaseForm):
    """
    Formulário para criar/editar despesas

    Navegação via MainWindow.show_screen("despesa_form", despesa_id=None/ID)

    Modos:
    - CREATE: despesa_id=None
    - EDIT: despesa_id=<id>
    """

    def __init__(self, parent, db_session: Session, despesa_id: Optional[int] = None, **kwargs):
        """
        Initialize despesa form screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            despesa_id: ID da despesa (None para criar, ID para editar)
        """
        self.db_session = db_session
        self.despesa_id = despesa_id
        self.manager = DespesasManager(db_session)
        self.is_create = (despesa_id is None)

        # Obter listas dinâmicas ANTES de chamar super().__init__()
        self.fornecedores = self.manager.obter_fornecedores()
        self.fornecedores_map = {f"{f.numero} - {f.nome}": f.id for f in self.fornecedores}
        self.fornecedor_options = ["(Nenhum)"] + [f"{f.numero} - {f.nome}" for f in self.fornecedores]

        self.projetos = self.manager.obter_projetos()
        self.projetos_map = {f"{p.numero} - {p.descricao[:30]}": p.id for p in self.projetos}
        self.projeto_options = ["(Nenhum)"] + [f"{p.numero} - {p.descricao[:30]}" for p in self.projetos]

        # Load initial data if editing
        initial_data = {}
        if despesa_id:
            despesa = self.manager.obter_por_id(despesa_id)
            if despesa:
                # Tipo: enum → string display
                tipo_display_map = {
                    TipoDespesa.FIXA_MENSAL: "Fixa Mensal",
                    TipoDespesa.PESSOAL_BRUNO: "Pessoal BA",
                    TipoDespesa.PESSOAL_RAFAEL: "Pessoal RR",
                    TipoDespesa.EQUIPAMENTO: "Equipamento",
                    TipoDespesa.PROJETO: "Projeto"
                }

                # Estado: enum → string display
                estado_display_map = {
                    EstadoDespesa.PENDENTE: "Pendente",
                    EstadoDespesa.VENCIDO: "Vencido",
                    EstadoDespesa.PAGO: "Pago"
                }

                # Credor: object → string display
                credor_display = "(Nenhum)"
                if despesa.credor:
                    credor_display = f"{despesa.credor.numero} - {despesa.credor.nome}"

                # Projeto: object → string display
                projeto_display = "(Nenhum)"
                if despesa.projeto:
                    projeto_display = f"{despesa.projeto.numero} - {despesa.projeto.descricao[:30]}"

                initial_data = {
                    'data': despesa.data,  # date object
                    'tipo': tipo_display_map.get(despesa.tipo, "Fixa Mensal"),
                    'credor': credor_display,
                    'projeto': projeto_display,
                    'descricao': despesa.descricao or '',
                    'valor_sem_iva': str(float(despesa.valor_sem_iva)) if despesa.valor_sem_iva else '0.00',
                    'valor_com_iva': str(float(despesa.valor_com_iva)) if despesa.valor_com_iva else '0.00',
                    'estado': estado_display_map.get(despesa.estado, "Pendente"),
                    'data_pagamento': despesa.data_pagamento,  # date object ou None
                    'nota': despesa.nota or '',
                }
            else:
                messagebox.showerror("Erro", "Despesa não encontrada!")
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
        if self.despesa_id:
            return "Editar Despesa"
        return "Nova Despesa"

    def get_form_icon(self):
        """Return form icon"""
        return get_icon(DESPESAS, size=(28, 28))

    def get_fields_config(self) -> List[Dict[str, Any]]:
        """
        Return field configurations for despesa form

        Campos (baseados no DB real):
        - data (date, required)
        - tipo (dropdown, required)
        - credor (dropdown dinâmico, required)
        - projeto (dropdown dinâmico, opcional)
        - descricao (textarea, required)
        - valor_sem_iva (number, required, min=0)
        - valor_com_iva (number, required, min=0)
        - estado (dropdown, required)
        - data_pagamento (date, opcional)
        - nota (textarea, opcional)
        """
        return [
            # Data (required)
            {
                "key": "data",
                "label": "Data",
                "type": "date",
                "required": True,
            },

            # Tipo (dropdown 5 opções, required)
            {
                "key": "tipo",
                "label": "Tipo",
                "type": "dropdown",
                "values": ["Fixa Mensal", "Pessoal BA", "Pessoal RR", "Equipamento", "Projeto"],
                "default": "Fixa Mensal",
                "required": True,
                "width": 300
            },

            # Credor/Fornecedor (dropdown dinâmico, required)
            {
                "key": "credor",
                "label": "Credor/Fornecedor",
                "type": "dropdown",
                "values": self.fornecedor_options,
                "default": "(Nenhum)",
                "required": True,
                "width": 400
            },

            # Projeto associado (dropdown dinâmico, opcional)
            {
                "key": "projeto",
                "label": "Projeto Associado",
                "type": "dropdown",
                "values": self.projeto_options,
                "default": "(Nenhum)",
                "width": 400
            },

            # Descrição (textarea, required)
            {
                "key": "descricao",
                "label": "Descrição",
                "type": "textarea",
                "required": True,
                "placeholder": "Descrição da despesa...",
                "width": 500
            },

            # Valor sem IVA (number, required, min=0)
            {
                "key": "valor_sem_iva",
                "label": "Valor s/ IVA (€)",
                "type": "number",
                "required": True,
                "placeholder": "0.00",
                "validator": self._validate_valor_sem_iva,
                "width": 250
            },

            # Valor com IVA (number, required, min=0)
            {
                "key": "valor_com_iva",
                "label": "Valor c/ IVA (€)",
                "type": "number",
                "required": True,
                "placeholder": "0.00",
                "validator": self._validate_valor_com_iva,
                "width": 250
            },

            # Estado (dropdown 3 opções, required)
            {
                "key": "estado",
                "label": "Estado",
                "type": "dropdown",
                "values": ["Pendente", "Vencido", "Pago"],
                "default": "Pendente",
                "required": True,
                "width": 200
            },

            # Data Pagamento (date, opcional)
            {
                "key": "data_pagamento",
                "label": "Data Pagamento (se pago)",
                "type": "date",
            },

            # Nota (textarea, opcional)
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
        Handle save - create or update despesa

        Args:
            data: Dict com todos os valores do form

        Returns:
            True se sucesso, ou mensagem de erro
        """
        try:
            # ===== 1. PARSE TIPO (string → enum) =====
            tipo_str = data.get('tipo', '').strip()
            tipo_map = {
                "Fixa Mensal": TipoDespesa.FIXA_MENSAL,
                "Pessoal BA": TipoDespesa.PESSOAL_BRUNO,
                "Pessoal RR": TipoDespesa.PESSOAL_RAFAEL,
                "Equipamento": TipoDespesa.EQUIPAMENTO,
                "Projeto": TipoDespesa.PROJETO
            }

            if tipo_str not in tipo_map:
                return "Tipo de despesa inválido"

            tipo = tipo_map[tipo_str]

            # ===== 2. PARSE DATA (date object, required) =====
            data_despesa = data.get('data')
            if not data_despesa:
                return "Data é obrigatória"

            # ===== 3. PARSE CREDOR (string → ID) =====
            credor_str = data.get('credor', '').strip()
            if not credor_str or credor_str == "(Nenhum)":
                return "Credor/Fornecedor é obrigatório"

            credor_id = self.fornecedores_map.get(credor_str)
            if not credor_id:
                return "Credor/Fornecedor inválido"

            # ===== 4. PARSE PROJETO (string → ID, opcional) =====
            projeto_str = data.get('projeto', '').strip()
            if projeto_str and projeto_str != "(Nenhum)":
                projeto_id = self.projetos_map.get(projeto_str)
            else:
                projeto_id = None

            # ===== 5. PARSE DESCRIÇÃO (required) =====
            descricao = data.get('descricao', '').strip()
            if not descricao:
                return "Descrição é obrigatória"

            # ===== 6. PARSE VALORES (required, min=0) =====
            try:
                valor_sem_iva_str = data.get('valor_sem_iva', '').strip()
                if not valor_sem_iva_str:
                    return "Valor s/ IVA é obrigatório"

                valor_sem_iva = Decimal(valor_sem_iva_str.replace(',', '.'))
                if valor_sem_iva < 0:
                    return "Valor s/ IVA deve ser >= 0"

            except (ValueError, TypeError):
                return "Valor s/ IVA inválido"

            try:
                valor_com_iva_str = data.get('valor_com_iva', '').strip()
                if not valor_com_iva_str:
                    return "Valor c/ IVA é obrigatório"

                valor_com_iva = Decimal(valor_com_iva_str.replace(',', '.'))
                if valor_com_iva < 0:
                    return "Valor c/ IVA deve ser >= 0"

            except (ValueError, TypeError):
                return "Valor c/ IVA inválido"

            # ===== 7. PARSE ESTADO (string → enum) =====
            estado_str = data.get('estado', '').strip()
            estado_map = {
                "Pendente": EstadoDespesa.PENDENTE,
                "Vencido": EstadoDespesa.VENCIDO,
                "Pago": EstadoDespesa.PAGO
            }

            if estado_str not in estado_map:
                return "Estado inválido"

            estado = estado_map[estado_str]

            # ===== 8. PARSE DATA PAGAMENTO (date object, condicional) =====
            data_pagamento = data.get('data_pagamento')  # date object ou None

            # Validação: se estado = Pago, data_pagamento é obrigatória
            if estado == EstadoDespesa.PAGO and not data_pagamento:
                return "Data de Pagamento é obrigatória quando estado é 'Pago'"

            # ===== 9. PARSE NOTA (opcional) =====
            nota = data.get('nota', '').strip() or None

            # ===== 10. CREATE OR UPDATE =====
            if self.despesa_id:
                # UPDATE
                sucesso, erro = self.manager.atualizar(
                    self.despesa_id,
                    tipo=tipo,
                    data=data_despesa,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    estado=estado,
                    data_pagamento=data_pagamento,
                    nota=nota
                )

                if not sucesso:
                    return erro or "Erro ao atualizar despesa"

            else:
                # CREATE
                sucesso, despesa, erro = self.manager.criar(
                    tipo=tipo,
                    data=data_despesa,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    estado=estado,
                    data_pagamento=data_pagamento,
                    nota=nota
                )

                if not sucesso:
                    return erro or "Erro ao criar despesa"

            # Success!
            return True

        except Exception as e:
            return f"Erro inesperado: {str(e)}"

    # ===== VALIDADORES =====

    def _validate_valor_sem_iva(self, valor: str) -> bool:
        """
        Valida Valor sem IVA

        Args:
            valor: Valor a validar

        Returns:
            True se válido, False caso contrário
        """
        if not valor:
            return False  # Obrigatório

        try:
            val = float(valor.replace(',', '.'))
            return val >= 0
        except ValueError:
            return False

    def _validate_valor_com_iva(self, valor: str) -> bool:
        """
        Valida Valor com IVA

        Args:
            valor: Valor a validar

        Returns:
            True se válido, False caso contrário
        """
        if not valor:
            return False  # Obrigatório

        try:
            val = float(valor.replace(',', '.'))
            return val >= 0
        except ValueError:
            return False

    # ===== CALLBACKS =====

    def after_save_callback(self):
        """
        Executado após save bem-sucedido

        Navega de volta para lista de despesas
        """
        self._voltar_para_lista()

    def after_cancel_callback(self):
        """
        Executado após cancelar

        Confirma e navega de volta para lista de despesas
        """
        resposta = messagebox.askyesno(
            "Cancelar",
            "Tem certeza que deseja cancelar?\n\nTodas as alterações serão perdidas."
        )

        if resposta:
            self._voltar_para_lista()

    # ===== HELPERS =====

    def _voltar_para_lista(self):
        """Navega de volta para lista de despesas"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("despesas")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")
