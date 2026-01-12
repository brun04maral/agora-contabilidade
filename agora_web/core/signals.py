# -*- coding: utf-8 -*-
"""
Signals para auto-população de campos de audit trail
"""
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from simple_history.signals import pre_create_historical_record

from .models import (
    Socio, Cliente, Fornecedor, Projeto, Despesa, DespesaTemplate,
    Boletim, Equipamento, Orcamento
)


def get_current_user():
    """
    Obtém o user atual do middleware de simple_history

    IMPORTANTE: Isto funciona porque o HistoryRequestMiddleware
    armazena o user atual no thread local.
    """
    from simple_history.middleware import HistoryRequestMiddleware
    return HistoryRequestMiddleware.get_current_user()


def populate_audit_fields(sender, instance, **kwargs):
    """
    Popula automaticamente created_by e updated_by antes de salvar

    - Se é novo objeto (sem pk): define created_by e updated_by
    - Se já existe (tem pk): atualiza apenas updated_by
    """
    try:
        user = get_current_user()
    except Exception:
        # Se não conseguir obter o user, simplesmente não atualiza
        return

    # Apenas atualiza se houver um user logado
    if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
        # Se é novo objeto, define created_by
        if instance.pk is None and hasattr(instance, 'created_by'):
            if not instance.created_by:
                instance.created_by = user

        # Sempre atualiza updated_by
        if hasattr(instance, 'updated_by'):
            instance.updated_by = user


# Registar signal para todos os modelos com UserTrackingMixin
TRACKED_MODELS = [
    Socio, Cliente, Fornecedor, Projeto, Despesa, DespesaTemplate,
    Boletim, Equipamento, Orcamento
]

for model in TRACKED_MODELS:
    pre_save.connect(populate_audit_fields, sender=model)


@receiver(pre_create_historical_record)
def set_history_user_from_request(sender, **kwargs):
    """
    Garante que o history_user é sempre definido corretamente

    Isto é um backup caso o middleware não capture o user.
    """
    history_instance = kwargs.get('history_instance')

    try:
        user = get_current_user()
    except Exception:
        return

    if user and hasattr(user, 'is_authenticated') and user.is_authenticated and not history_instance.history_user:
        history_instance.history_user = user
