"""
Sistema de Mapeamento Automático de Tags Fiscais

Baseado nas respostas do contabilista (RESPOSTAS_CONTABILISTA.md)
Este ficheiro mapeia tags operacionais para tags fiscais (IRC, IVA, IRS, TSU)
"""

# Mapeamento de keywords de tags operacionais para tags fiscais
# Formato: {'keyword': {'irc': 'codigo_tag', 'iva': 'codigo_tag', 'irs': 'codigo_tag', 'tsu': 'codigo_tag'}}

FISCAL_MAPPING = {
    # ========== PESSOAL ==========

    'ordenado': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,  # Ordenados não têm IVA
        'irs': 'IRS_RETENCAO_TRABALHO',
        'tsu': None,  # Definido dinamicamente (gerente vs trabalhador)
        'notes': 'Verificar se é gerente (TSU_GERENTE) ou trabalhador (TSU_TRABALHADOR)'
    },

    'salario': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_RETENCAO_TRABALHO',
        'tsu': None,
        'notes': 'Verificar se é gerente (TSU_GERENTE) ou trabalhador (TSU_TRABALHADOR)'
    },

    'gerente': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_RETENCAO_TRABALHO',
        'tsu': 'TSU_GERENTE',
        'notes': 'Gerente: 21,4% empresa + 9,3% trabalhador'
    },

    'trabalhador': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_RETENCAO_TRABALHO',
        'tsu': 'TSU_TRABALHADOR',
        'notes': 'Trabalhador: 23,75% empresa + 11% trabalhador'
    },

    'subsídio alimentação': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_ISENTO',
        'tsu': 'TSU_ISENTO',
        'notes': 'Isento se ≤€10,20/dia em vales ou ≤€6/dia em dinheiro'
    },

    'subsidio alimentacao': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_ISENTO',
        'tsu': 'TSU_ISENTO',
        'notes': 'Isento se ≤€10,20/dia em vales ou ≤€6/dia em dinheiro'
    },

    'refeição': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_ISENTO',
        'tsu': 'TSU_ISENTO',
        'notes': 'Subsídio de alimentação - isento se dentro dos limites'
    },

    'premio': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_RETENCAO_TRABALHO',
        'tsu': None,
        'notes': 'Entra na base de IRS e TSU como ordenado normal'
    },

    'bonus': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_RETENCAO_TRABALHO',
        'tsu': None,
        'notes': 'Entra na base de IRS e TSU como ordenado normal'
    },

    # ========== EQUIPAMENTO ==========

    'equipamento': {
        'irc': 'IRC_INVESTIMENTO',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Se ≥€500: investimento (25% aa). Se <€500: despesa corrente 100%'
    },

    'computador': {
        'irc': 'IRC_INVESTIMENTO',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Equipamento informático: 25% aa ou despesa corrente se <€500'
    },

    'camera': {
        'irc': 'IRC_INVESTIMENTO',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Equipamento audiovisual: 25% aa ou despesa corrente se <€500'
    },

    'câmara': {
        'irc': 'IRC_INVESTIMENTO',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Equipamento audiovisual: 25% aa ou despesa corrente se <€500'
    },

    'software': {
        'irc': 'IRC_INVESTIMENTO',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Software: amortização 3-5 anos'
    },

    'microfone': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Geralmente <€500: despesa corrente'
    },

    'luz': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Equipamento de iluminação: geralmente <€500'
    },

    # ========== VIATURAS E COMBUSTÍVEL ==========

    'viatura': {
        'irc': 'IRC_INVESTIMENTO',
        'iva': 'IVA_NAO_DEDUTIVEL',
        'irs': None,
        'tsu': None,
        'notes': 'Limite depreciação €25.000. IVA não dedutível. Considerar renting.'
    },

    'carro': {
        'irc': 'IRC_INVESTIMENTO',
        'iva': 'IVA_NAO_DEDUTIVEL',
        'irs': None,
        'tsu': None,
        'notes': 'Limite depreciação €25.000. IVA não dedutível. Considerar renting.'
    },

    'renting': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Renting: 100% dedutível IRC e IVA. Melhor opção fiscal que compra.'
    },

    'gasolina': {
        'irc': 'IRC_NAO_DEDUTIVEL',
        'iva': 'IVA_NAO_DEDUTIVEL',
        'irs': None,
        'tsu': None,
        'notes': 'Gasolina: 0% dedutível em IRC e IVA'
    },

    'gasóleo': {
        'irc': 'IRC_DEDUTIVEL_PARCIAL',
        'iva': 'IVA_MISTO',
        'irs': None,
        'tsu': None,
        'notes': 'Gasóleo: até 50% dedutível se viatura mista'
    },

    'gasoleo': {
        'irc': 'IRC_DEDUTIVEL_PARCIAL',
        'iva': 'IVA_MISTO',
        'irs': None,
        'tsu': None,
        'notes': 'Gasóleo: até 50% dedutível se viatura mista'
    },

    'combustível': {
        'irc': None,
        'iva': None,
        'irs': None,
        'tsu': None,
        'notes': 'Verificar tipo: gasolina (0%) ou gasóleo (50%)'
    },

    # ========== SERVIÇOS E FREELANCERS ==========

    'freelancer': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': 'IRS_RETENCAO_25',
        'tsu': 'TSU_INDEPENDENTE',
        'notes': 'Freelancer genérico: retenção 25%. Empresa não paga TSU.'
    },

    'freelance': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': 'IRS_RETENCAO_25',
        'tsu': 'TSU_INDEPENDENTE',
        'notes': 'Freelancer genérico: retenção 25%. Empresa não paga TSU.'
    },

    'prestador': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': 'IRS_RETENCAO_25',
        'tsu': 'TSU_INDEPENDENTE',
        'notes': 'Prestador de serviços: retenção 25%. Empresa não paga TSU.'
    },

    'editor': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': 'IRS_RETENCAO_25',
        'tsu': 'TSU_INDEPENDENTE',
        'notes': 'Editor freelancer: retenção 25%'
    },

    'designer': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': 'IRS_RETENCAO_25',
        'tsu': 'TSU_INDEPENDENTE',
        'notes': 'Designer freelancer: retenção 25%'
    },

    'fotógrafo': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': 'IRS_RETENCAO_25',
        'tsu': 'TSU_INDEPENDENTE',
        'notes': 'Fotógrafo freelancer: retenção 25%'
    },

    'fotografo': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': 'IRS_RETENCAO_25',
        'tsu': 'TSU_INDEPENDENTE',
        'notes': 'Fotógrafo freelancer: retenção 25%'
    },

    'contabilista': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': 'IRS_RETENCAO_11_5',
        'tsu': 'TSU_INDEPENDENTE',
        'notes': 'Contabilista (profissional regulado): retenção 11,5%'
    },

    'advogado': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': 'IRS_RETENCAO_16_5',
        'tsu': 'TSU_INDEPENDENTE',
        'notes': 'Advogado: retenção 16,5% (exceção)'
    },

    # ========== REPRESENTAÇÃO E ENTRETENIMENTO ==========

    'almoço': {
        'irc': 'IRC_DEDUTIVEL_PARCIAL',
        'iva': 'IVA_NAO_DEDUTIVEL',
        'irs': None,
        'tsu': None,
        'notes': 'Despesas de representação: limite 0,05% volume negócios. IVA não dedutível.'
    },

    'jantar': {
        'irc': 'IRC_DEDUTIVEL_PARCIAL',
        'iva': 'IVA_NAO_DEDUTIVEL',
        'irs': None,
        'tsu': None,
        'notes': 'Despesas de representação: limite 0,05% volume negócios. IVA não dedutível.'
    },

    'refeição cliente': {
        'irc': 'IRC_DEDUTIVEL_PARCIAL',
        'iva': 'IVA_NAO_DEDUTIVEL',
        'irs': None,
        'tsu': None,
        'notes': 'Despesas de representação: limite 0,05% volume negócios. Documentar cliente e objetivo.'
    },

    'restaurante': {
        'irc': 'IRC_DEDUTIVEL_PARCIAL',
        'iva': 'IVA_NAO_DEDUTIVEL',
        'irs': None,
        'tsu': None,
        'notes': 'Despesas de representação: limite 0,05% volume negócios. IVA não dedutível.'
    },

    'alojamento': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_NAO_DEDUTIVEL',
        'irs': None,
        'tsu': None,
        'notes': 'Alojamento profissional: dedutível IRC mas IVA não dedutível'
    },

    'hotel': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_NAO_DEDUTIVEL',
        'irs': None,
        'tsu': None,
        'notes': 'Hotel profissional: dedutível IRC mas IVA não dedutível'
    },

    # ========== AJUDAS DE CUSTO ==========

    'ajuda de custo': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_ISENTO',
        'tsu': 'TSU_ISENTO',
        'notes': 'Portugal: €62,75/dia. Estrangeiro: varia por país. Necessário mapa de deslocações.'
    },

    'deslocação': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_ISENTO',
        'tsu': 'TSU_ISENTO',
        'notes': 'Deslocações: €0,40/km ou ajudas de custo. Necessário mapa documentado.'
    },

    'quilómetros': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': None,
        'irs': 'IRS_ISENTO',
        'tsu': 'TSU_ISENTO',
        'notes': 'Ajuda de custo quilométrica: €0,40/km. Necessário mapa mensal.'
    },

    # ========== UTILITÁRIOS E SERVIÇOS GERAIS ==========

    'eletricidade': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Despesa corrente 100% dedutível'
    },

    'água': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Despesa corrente 100% dedutível'
    },

    'internet': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Serviço de telecomunicações 100% dedutível'
    },

    'telefone': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Serviço de telecomunicações 100% dedutível'
    },

    'renda': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Renda de instalações 100% dedutível (se atividade profissional)'
    },

    'arrendamento': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Arrendamento de espaço 100% dedutível'
    },

    'seguro': {
        'irc': 'IRC_DEDUTIVEL_100',
        'iva': 'IVA_DEDUTIVEL_100',
        'irs': None,
        'tsu': None,
        'notes': 'Seguros relacionados com atividade: 100% dedutível'
    },
}


def suggest_fiscal_tags(tag_names_or_description):
    """
    Sugere tags fiscais baseadas em tags operacionais ou descrição.

    Args:
        tag_names_or_description: Lista de nomes de tags ou string de descrição

    Returns:
        dict: {'irc': codigo, 'iva': codigo, 'irs': codigo, 'tsu': codigo, 'notes': str, 'confidence': int}
    """
    if isinstance(tag_names_or_description, str):
        # Converter string em lowercase para matching
        text = tag_names_or_description.lower()
    else:
        # Lista de tags - juntar em texto
        text = ' '.join([str(tag).lower() for tag in tag_names_or_description])

    # Procurar matches no mapeamento
    matches = []
    for keyword, mapping in FISCAL_MAPPING.items():
        if keyword in text:
            matches.append((keyword, mapping, len(keyword)))

    if not matches:
        return {
            'irc': None,
            'iva': None,
            'irs': None,
            'tsu': None,
            'notes': 'Nenhuma sugestão automática. Categorizar manualmente.',
            'confidence': 0
        }

    # Ordenar por tamanho do match (matches mais longos são mais específicos)
    matches.sort(key=lambda x: x[2], reverse=True)

    # Usar o match mais específico
    keyword, mapping, _ = matches[0]

    return {
        'irc': mapping.get('irc'),
        'iva': mapping.get('iva'),
        'irs': mapping.get('irs'),
        'tsu': mapping.get('tsu'),
        'notes': mapping.get('notes', ''),
        'confidence': 80 if len(matches) == 1 else 60,  # Alta confiança se só 1 match
        'keyword_matched': keyword
    }


def get_all_mappings():
    """Retorna todas as keywords mapeadas (para debugging/documentação)"""
    return list(FISCAL_MAPPING.keys())
