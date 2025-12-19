# -*- coding: utf-8 -*-
"""
ProjetoFormScreen - Formulário para criar/editar projetos

Migrado para BaseForm framework (SPRINT 7)
Primeiro form a usar layout 2 colunas (columns=2)
Segue padrão estabelecido em ui/components/base_form.py
"""

import customtkinter as ctk
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from tkinter import messagebox
from decimal import Decimal
from datetime import date

from ui.components.base_form import BaseForm
from logic.projetos import ProjetosManager
from logic.clientes import ClientesManager
from assets.resources import get_icon, PROJETOS
from database.models.projeto import TipoProjeto, EstadoProjeto


class ProjetoFormScreen(BaseForm):
    """
    Formulário para criar/editar projetos

    Navegação via MainWindow.show_screen("projeto_form", projeto_id=None/ID)

    Modos:
    - CREATE: projeto_id=None
    - EDIT: projeto_id=<id>

    FEATURES:
    - Layout 2 COLUNAS (primeiro form a usar columns=2)
    - Campos organizados em grid responsivo
    - Período usa 2 date pickers separados (data_inicio + data_fim)
    """

    def __init__(self, parent, db_session: Session, projeto_id: Optional[int] = None, **kwargs):
        """
        Initialize projeto form screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            projeto_id: ID do projeto (None para criar, ID para editar)
        """
        self.db_session = db_session
        self.projeto_id = projeto_id
        self.manager = ProjetosManager(db_session)
        self.clientes_manager = ClientesManager(db_session)
        self.is_create = (projeto_id is None)

        # Obter clientes ANTES de chamar super().__init__()
        clientes = self.clientes_manager.listar_todos(order_by="nome")
        self.cliente_options = ["(Nenhum)"] + [f"{c.numero} - {c.nome}" for c in clientes]
        self.clientes_map = {f"{c.numero} - {c.nome}": c.id for c in clientes}

        # Load initial data if editing
        initial_data = {}
        if projeto_id:
            projeto = self.manager.obter_por_id(projeto_id)
            if projeto:
                # Tipo: enum → string display
                tipo_display = "Empresa" if projeto.tipo == TipoProjeto.EMPRESA else "Pessoal"

                # Estado: enum → string display
                estado_display_map = {
                    EstadoProjeto.ATIVO: "Ativo",
                    EstadoProjeto.FINALIZADO: "Finalizado",
                    EstadoProjeto.PAGO: "Pago",
                    EstadoProjeto.ANULADO: "Anulado"
                }

                # Cliente: object → string display
                cliente_display = "(Nenhum)"
                if projeto.cliente:
                    cliente_display = f"{projeto.cliente.numero} - {projeto.cliente.nome}"

                initial_data = {
                    'numero': projeto.numero,
                    'tipo': tipo_display,
                    'owner': projeto.owner,
                    'cliente': cliente_display,
                    'descricao': projeto.descricao or '',
                    'valor_sem_iva': str(float(projeto.valor_sem_iva)) if projeto.valor_sem_iva else '0.00',
                    'data_inicio': projeto.data_inicio,  # date object ou None
                    'data_fim': projeto.data_fim,  # date object ou None
                    'data_faturacao': projeto.data_faturacao,  # date object ou None
                    'data_vencimento': projeto.data_vencimento,  # date object ou None
                    'estado': estado_display_map.get(projeto.estado, "Ativo"),
                    'premio_bruno': str(float(projeto.premio_bruno)) if projeto.premio_bruno else '',
                    'premio_rafael': str(float(projeto.premio_rafael)) if projeto.premio_rafael else '',
                    'nota': projeto.nota or '',
                }
            else:
                messagebox.showerror("Erro", "Projeto não encontrado!")
                kwargs['on_cancel_callback'] = self._voltar_para_lista
        else:
            # Defaults para modo CREATE
            initial_data = {
                'tipo': 'Empresa',
                'owner': 'BA',
                'estado': 'Ativo',
                'data_inicio': date.today(),
            }

        # Initialize BaseForm com 2 COLUNAS
        super().__init__(
            parent,
            db_session=db_session,
            columns=2,  # ← LAYOUT 2 COLUNAS!
            initial_data=initial_data,
            on_cancel_callback=self._voltar_para_lista,
            **kwargs
        )

    # ===== MÉTODOS ABSTRATOS OBRIGATÓRIOS =====

    def get_form_title(self) -> str:
        """Return form title"""
        if self.projeto_id:
            return "Editar Projeto"
        return "Novo Projeto"

    def get_form_icon(self):
        """Return form icon"""
        return get_icon(PROJETOS, size=(28, 28))

    def get_fields_config(self) -> List[Dict[str, Any]]:
        """
        Return field configurations for projeto form

        Layout 2 COLUNAS com colspan para campos full-width

        Campos (baseados no DB real):
        - numero (readonly, gerado automaticamente)
        - tipo (dropdown: Empresa/Pessoal, required)
        - owner (dropdown: BA/RR, required)
        - cliente (dropdown dinâmico, opcional)
        - descricao (textarea, required, full-width)
        - valor_sem_iva (number, required)
        - data_inicio (date)
        - data_fim (date)
        - data_faturacao (date)
        - data_vencimento (date)
        - estado (dropdown, required)
        - premio_bruno (number, Decimal)
        - premio_rafael (number, Decimal)
        - nota (textarea, full-width)
        """
        return [
            # LINHA 1 - Número (readonly, full-width)
            {
                "key": "numero",
                "label": "Número",
                "type": "text",
                "readonly": True,
                "placeholder": "(Será gerado automaticamente)",
                "colspan": 2,
                "width": 300
            },

            # LINHA 2 - Tipo e Owner (duas colunas)
            {
                "key": "tipo",
                "label": "Tipo",
                "type": "dropdown",
                "values": ["Empresa", "Pessoal"],
                "default": "Empresa",
                "required": True,
                "width": 250
            },
            {
                "key": "owner",
                "label": "Responsável",
                "type": "dropdown",
                "values": ["BA", "RR"],
                "default": "BA",
                "required": True,
                "width": 150
            },

            # LINHA 3 - Cliente (full-width)
            {
                "key": "cliente",
                "label": "Cliente",
                "type": "dropdown",
                "values": self.cliente_options,
                "default": "(Nenhum)",
                "colspan": 2,
                "width": 500
            },

            # LINHA 4 - Descrição (full-width)
            {
                "key": "descricao",
                "label": "Descrição",
                "type": "textarea",
                "required": True,
                "placeholder": "Descrição do projeto...",
                "colspan": 2,
                "width": 600
            },

            # LINHA 5 - Valor e Estado (duas colunas)
            {
                "key": "valor_sem_iva",
                "label": "Valor s/ IVA (€)",
                "type": "number",
                "required": True,
                "placeholder": "0.00",
                "validator": self._validate_valor,
                "width": 250
            },
            {
                "key": "estado",
                "label": "Estado",
                "type": "dropdown",
                "values": ["Ativo", "Finalizado", "Pago", "Anulado"],
                "default": "Ativo",
                "required": True,
                "width": 250
            },

            # LINHA 6 - Data Início e Data Fim (duas colunas)
            {
                "key": "data_inicio",
                "label": "Data Início",
                "type": "date",
            },
            {
                "key": "data_fim",
                "label": "Data Fim Prevista",
                "type": "date",
            },

            # LINHA 7 - Data Faturação e Data Vencimento (duas colunas)
            {
                "key": "data_faturacao",
                "label": "Data Faturação",
                "type": "date",
            },
            {
                "key": "data_vencimento",
                "label": "Data Vencimento",
                "type": "date",
            },

            # LINHA 8 - Prémios (duas colunas)
            {
                "key": "premio_bruno",
                "label": "Prémio BA (€)",
                "type": "number",
                "placeholder": "0.00",
                "validator": self._validate_premio,
                "width": 250
            },
            {
                "key": "premio_rafael",
                "label": "Prémio RR (€)",
                "type": "number",
                "placeholder": "0.00",
                "validator": self._validate_premio,
                "width": 250
            },

            # LINHA 9 - Nota (full-width)
            {
                "key": "nota",
                "label": "Nota",
                "type": "textarea",
                "placeholder": "Observações adicionais...",
                "colspan": 2,
                "width": 600
            },
        ]

    def on_save(self, data: Dict[str, Any]) -> bool | str:
        """
        Handle save - create or update projeto

        Args:
            data: Dict com todos os valores do form

        Returns:
            True se sucesso, ou mensagem de erro
        """
        try:
            # Prepare data (convert empty strings to None)
            descricao = data.get('descricao', '').strip()
            tipo_str = data.get('tipo', 'Empresa').strip()
            owner = data.get('owner', 'BA').strip()
            estado_str = data.get('estado', 'Ativo').strip()
            nota = data.get('nota', '').strip() or None

            # Validate descricao (BaseForm já valida required, mas double check)
            if not descricao:
                return "Descrição é obrigatória"

            # Parse tipo enum
            tipo_map = {
                "Empresa": TipoProjeto.EMPRESA,
                "Pessoal": TipoProjeto.PESSOAL
            }
            tipo = tipo_map.get(tipo_str, TipoProjeto.EMPRESA)

            # Parse estado enum
            estado_map = {
                "Ativo": EstadoProjeto.ATIVO,
                "Finalizado": EstadoProjeto.FINALIZADO,
                "Pago": EstadoProjeto.PAGO,
                "Anulado": EstadoProjeto.ANULADO
            }
            estado = estado_map.get(estado_str, EstadoProjeto.ATIVO)

            # Parse cliente
            cliente_str = data.get('cliente', '(Nenhum)').strip()
            if cliente_str == "(Nenhum)":
                cliente_id = None
            else:
                cliente_id = self.clientes_map.get(cliente_str)
                if cliente_id is None and cliente_str != "(Nenhum)":
                    return f"Cliente '{cliente_str}' não encontrado"

            # Parse valor_sem_iva
            try:
                valor_sem_iva_str = data.get('valor_sem_iva', '').strip()
                if not valor_sem_iva_str:
                    return "Valor sem IVA é obrigatório"

                valor_sem_iva = Decimal(valor_sem_iva_str.replace(',', '.'))
                if valor_sem_iva < 0:
                    return "Valor sem IVA deve ser >= 0"

            except (ValueError, TypeError):
                return "Valor sem IVA inválido"

            # Parse prémios
            try:
                premio_bruno_str = data.get('premio_bruno', '').strip()
                if premio_bruno_str:
                    premio_bruno = Decimal(premio_bruno_str.replace(',', '.'))
                    if premio_bruno < 0:
                        return "Prémio BA deve ser >= 0"
                else:
                    premio_bruno = None

                premio_rafael_str = data.get('premio_rafael', '').strip()
                if premio_rafael_str:
                    premio_rafael = Decimal(premio_rafael_str.replace(',', '.'))
                    if premio_rafael < 0:
                        return "Prémio RR deve ser >= 0"
                else:
                    premio_rafael = None

            except (ValueError, TypeError):
                return "Prémios inválidos"

            # Parse datas (BaseForm já retorna date objects ou None)
            data_inicio = data.get('data_inicio')  # date object ou None
            data_fim = data.get('data_fim')  # date object ou None
            data_faturacao = data.get('data_faturacao')  # date object ou None
            data_vencimento = data.get('data_vencimento')  # date object ou None

            # Validação: data_fim >= data_inicio (se ambas preenchidas)
            if data_inicio and data_fim and data_fim < data_inicio:
                return "Data Fim não pode ser anterior à Data Início"

            # Prepare data dict for manager
            projeto_data = {
                "tipo": tipo,
                "owner": owner,
                "cliente_id": cliente_id,
                "descricao": descricao,
                "valor_sem_iva": valor_sem_iva,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "data_faturacao": data_faturacao,
                "data_vencimento": data_vencimento,
                "estado": estado,
                "premio_bruno": premio_bruno,
                "premio_rafael": premio_rafael,
                "nota": nota,
            }

            # Create or update
            if self.projeto_id:
                # UPDATE
                sucesso, erro = self.manager.atualizar(
                    self.projeto_id,
                    **projeto_data
                )

                if not sucesso:
                    return erro or "Erro ao atualizar projeto"

            else:
                # CREATE
                sucesso, projeto, erro = self.manager.criar(
                    **projeto_data
                )

                if not sucesso:
                    return erro or "Erro ao criar projeto"

            # Success!
            return True

        except Exception as e:
            return f"Erro inesperado: {str(e)}"

    # ===== VALIDADORES =====

    def _validate_valor(self, valor: str) -> bool:
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
            val = Decimal(valor.replace(',', '.'))
            return val >= 0
        except (ValueError, TypeError):
            return False

    def _validate_premio(self, valor: str) -> bool:
        """
        Valida Prémio

        Args:
            valor: Valor a validar

        Returns:
            True se válido, False caso contrário
        """
        if not valor:
            return True  # Opcional

        try:
            val = Decimal(valor.replace(',', '.'))
            return val >= 0
        except (ValueError, TypeError):
            return False

    # ===== CALLBACKS =====

    def after_save_callback(self):
        """
        Executado após save bem-sucedido

        Navega de volta para lista de projetos
        """
        self._voltar_para_lista()

    def after_cancel_callback(self):
        """
        Executado após cancelar

        Confirma e navega de volta para lista de projetos
        """
        resposta = messagebox.askyesno(
            "Cancelar",
            "Tem certeza que deseja cancelar?\n\nTodas as alterações serão perdidas."
        )

        if resposta:
            self._voltar_para_lista()

    # ===== HELPERS =====

    def _voltar_para_lista(self):
        """Navega de volta para lista de projetos"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("projetos")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")
