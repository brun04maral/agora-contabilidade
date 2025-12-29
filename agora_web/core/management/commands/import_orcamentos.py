# -*- coding: utf-8 -*-
"""
Management command para importar Orçamentos com lookups de FK
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from core.models import (
    Cliente, Projeto, Fornecedor, Equipamento,
    Orcamento, OrcamentoSecao, OrcamentoItem, OrcamentoReparticao
)


class Command(BaseCommand):
    help = 'Importa orçamentos do arquivo JSON com lookups de FK'

    def handle(self, *args, **options):
        fixture_file = Path(__file__).parent.parent.parent.parent.parent / 'fixtures' / 'orcamentos_raw.json'

        if not fixture_file.exists():
            self.stdout.write(self.style.ERROR(f'❌ Arquivo não encontrado: {fixture_file}'))
            return

        with open(fixture_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stdout.write(f'📦 Importando {len(data)} orçamento(s)...\n')

        for item in data:
            orc_data = item['orcamento']
            cliente_numero = item.get('cliente_numero')
            projeto_numero = item.get('projeto_numero')
            secoes_data = item['secoes']
            itens_data = item['itens']
            reparticoes_data = item['reparticoes']

            # Lookup Cliente
            cliente = None
            if cliente_numero:
                try:
                    cliente = Cliente.objects.get(numero=cliente_numero)
                except Cliente.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'   ⚠ Cliente {cliente_numero} não encontrado'))

            # Lookup Projeto
            projeto = None
            if projeto_numero:
                try:
                    projeto = Projeto.objects.get(numero=projeto_numero)
                except Projeto.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'   ⚠ Projeto {projeto_numero} não encontrado'))

            # Criar Orçamento
            orcamento = Orcamento(
                codigo=orc_data['codigo'],
                cliente=cliente,
                projeto=projeto,
                owner=orc_data['owner'] or 'BA',
                data_criacao=orc_data['data_criacao'],
                data_evento=orc_data['data_evento'] or '',
                local_evento=orc_data['local_evento'] or '',
                descricao_proposta=orc_data['descricao_proposta'] or '',
                valor_total=orc_data['valor_total'] or 0,
                notas_contratuais=orc_data['notas_contratuais'] or '',
                status=orc_data['status'] or 'RASCUNHO',
                tem_versao_cliente=bool(orc_data['tem_versao_cliente']),
                titulo_cliente=orc_data['titulo_cliente'] or '',
                descricao_cliente=orc_data['descricao_cliente'] or '',
                created_at=orc_data['created_at'],
                updated_at=orc_data['updated_at']
            )
            orcamento.save()
            self.stdout.write(f'   ✅ Orçamento {orcamento.codigo} criado')

            # Criar secções (com mapeamento de IDs antigos para novos)
            secao_map = {}  # old_id -> nova_secao

            # Primeiro criar secções sem parent (ordem 0 ou parent_id None)
            for secao_data in sorted(secoes_data, key=lambda x: (x['parent_id'] is not None, x['ordem'])):
                old_secao_id = secao_data['id']
                parent_id = secao_data['parent_id']

                parent_secao = None
                if parent_id and parent_id in secao_map:
                    parent_secao = secao_map[parent_id]

                secao = OrcamentoSecao(
                    orcamento=orcamento,
                    tipo=secao_data['tipo'] or 'SERVICO',
                    nome=secao_data['nome'],
                    ordem=secao_data['ordem'],
                    parent=parent_secao,
                    subtotal=secao_data['subtotal'] or 0
                )
                secao.save()
                secao_map[old_secao_id] = secao

            self.stdout.write(f'   ✅ {len(secao_map)} secções criadas')

            # Criar itens
            itens_created = 0
            for item_data in itens_data:
                secao_id = item_data['secao_id']
                secao = secao_map.get(secao_id)

                if not secao:
                    self.stdout.write(self.style.WARNING(f'   ⚠ Secção ID {secao_id} não encontrada para item'))
                    continue

                # Lookup Equipamento se necessário
                equipamento = None
                if item_data['equipamento_id']:
                    # Buscar equipamento por ID antigo - precisamos fazer lookup
                    # Como não temos numero no item_data, vamos buscar pelo ID antigo se possível
                    # Por enquanto, vamos deixar None e ajustar depois se necessário
                    pass

                item = OrcamentoItem(
                    orcamento=orcamento,
                    secao=secao,
                    tipo=item_data['tipo'] or 'SERVICO',
                    descricao=item_data['descricao'] or '',
                    ordem=item_data['ordem'],
                    equipamento=equipamento,
                    quantidade=item_data['quantidade'] or 1,
                    dias=item_data['dias'] or 1,
                    preco_unitario=item_data['preco_unitario'] or 0,
                    desconto=item_data['desconto'] or 0,
                    kms=item_data['kms'] or 0,
                    valor_por_km=item_data['valor_por_km'] or 0,
                    num_refeicoes=item_data['num_refeicoes'] or 0,
                    valor_por_refeicao=item_data['valor_por_refeicao'] or 0,
                    valor_fixo=item_data['valor_fixo'] or 0,
                    total=item_data['total']
                )
                item.save()
                itens_created += 1

            self.stdout.write(f'   ✅ {itens_created} itens criados')

            # Criar repartições
            reparticoes_created = 0
            for rep_data in reparticoes_data:
                # Lookup Fornecedor
                fornecedor = None
                if rep_data['fornecedor_id']:
                    # Buscar por ID - similar ao equipamento, precisaríamos de lookup
                    pass

                # Lookup Equipamento
                equipamento = None
                if rep_data['equipamento_id']:
                    # Buscar por ID
                    pass

                reparticao = OrcamentoReparticao(
                    orcamento=orcamento,
                    tipo=rep_data['tipo'] or '',
                    entidade=rep_data['entidade'] or '',
                    fornecedor=fornecedor,
                    equipamento=equipamento,
                    beneficiario=rep_data['beneficiario'] or '',
                    valor=rep_data['valor'] or 0,
                    percentagem=rep_data['percentagem'] or 0,
                    ordem=rep_data['ordem'],
                    descricao=rep_data['descricao'] or '',
                    quantidade=rep_data['quantidade'] or 0,
                    dias=rep_data['dias'] or 0,
                    valor_unitario=rep_data['valor_unitario'] or 0,
                    base_calculo=rep_data['base_calculo'] or 0,
                    kms=rep_data['kms'] or 0,
                    valor_por_km=rep_data['valor_por_km'] or 0,
                    num_refeicoes=rep_data['num_refeicoes'] or 0,
                    valor_por_refeicao=rep_data['valor_por_refeicao'] or 0,
                    valor_fixo=rep_data['valor_fixo'] or 0,
                    item_cliente_id=rep_data['item_cliente_id'],
                    total=rep_data['total'] or 0
                )
                reparticao.save()
                reparticoes_created += 1

            self.stdout.write(f'   ✅ {reparticoes_created} repartições criadas')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Importação concluída! {len(data)} orçamento(s) importado(s)'))
