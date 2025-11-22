==================================================
INTEGRACOES.md - Integracoes com Sistemas Externos
==================================================

VISAO GERAL
==================================================

Este documento especifica todas as integracoes planeadas entre o sistema Agora e sistemas externos (TOConline, BizDocs, BPI Empresas).

Criado: 22/11/2025
Ultima revisao: 22/11/2025
Status: Planeamento completo - Aguarda implementacao


==================================================
ARQUITETURA DE INTEGRACAO
==================================================

Modelo Hub Central
--------------------------------------------------

                    AGORA SYSTEM
         (Hub Central - Gestao de Projetos)

  - Receitas (import TOConline)
  - Despesas (import BizDocs)
  - Reconciliacao Bancaria (import BPI)
  - P&L Consolidado por Projeto

           |                |                |
           |                |                |
      TOConline         BizDocs            BPI
        (SOT)            (SOT)          Empresas
       FATURAS          DESPESAS         EXTRATO


Sources of Truth (SOT)
--------------------------------------------------

Sistema         Responsabilidade              Direcao Dados           Integracao
-------------------------------------------------------------------------------------------------
TOConline       Faturas emitidas (receitas)   TOConline -> Agora      API REST (Fase 2) ou CSV (Fase 1)
BizDocs         Despesas e documentos         BizDocs -> Agora        CSV Export (Fase 1) ou API (Fase 3)
BPI Empresas    Movimentos bancarios          BPI -> Agora            CSV/OFX Export (Fase 1)
Agora           Projetos, Boletins, Socios    -                       Sistema central


==================================================
1. INTEGRACAO TOCONLINE (FATURAS/RECEITAS)
==================================================

1.1 Visao Geral
--------------------------------------------------

Sistema: TOConline - Software de Contabilidade e Faturacao
Responsavel: TOC (Tecnico Oficial de Contas)
Source of Truth: TOConline (faturas oficiais para AT)
Objetivo: Importar faturas emitidas e associar a projetos no Agora


1.2 API Disponivel
--------------------------------------------------

Portal: https://api-docs.toconline.pt
Tipo: API REST
Autenticacao: OAuth2 (authorization code flow)
Base URL: https://app.toconline.pt/api/
Documentacao: Swagger/OpenAPI disponivel
Custo: Gratuito (incluido na subscricao TOConline)


1.3 Endpoints Relevantes
--------------------------------------------------

Vendas/Faturas:

GET    /api/v1/commercial_sales_documents          # Listar faturas
GET    /api/v1/commercial_sales_documents/{id}    # Obter fatura
POST   /api/v1/commercial_sales_documents         # Criar fatura
PUT    /api/v1/commercial_sales_documents/{id}    # Atualizar fatura
DELETE /api/v1/commercial_sales_documents/{id}    # Eliminar fatura

GET    /api/v1/receipts                           # Listar recibos
POST   /api/v1/receipts                           # Criar recibo

Entidades:

GET    /api/customers                              # Listar clientes
GET    /api/customers?filter[tax_registration_number]=NIF
POST   /api/customers                              # Criar cliente

GET    /api/suppliers                              # Listar fornecedores
POST   /api/suppliers                              # Criar fornecedor

Auxiliares:

GET    /api/taxes                                  # Taxas IVA
GET    /api/products                               # Produtos
GET    /api/services                               # Servicos
GET    /api/bank_accounts                          # Contas bancarias


1.4 Cenario Operacional - Modelo Hibrido
--------------------------------------------------

CENARIO A: CREATE -> SYNC (Criar no Agora -> Enviar TOConline)

Fluxo:
1. User cria rascunho de fatura no Agora
2. Agora envia para TOConline via API (ou export manual Fase 1)
3. TOC valida/ajusta/emite oficialmente no TOConline
4. TOConline comunica fatura a AT (automatico)
5. Agora importa fatura oficial (sync)
6. Fatura fica associada ao projeto

Casos de uso:
- Proposta aceite -> gerar fatura
- Milestone atingido -> faturar parcialmente


CENARIO B: IMPORT -> LINK (Emitir no TOConline -> Importar no Agora)

Fluxo:
1. TOC emite fatura diretamente no TOConline
2. Agora sincroniza faturas periodicamente
3. Sistema sugere link automatico a projeto (NIF + valor + data)
4. User confirma ou ajusta associacao

Casos de uso:
- Faturas recorrentes emitidas pelo TOC
- Faturas urgentes emitidas fora do Agora


1.5 Implementacao
--------------------------------------------------

Fase 1: Export/Import Manual (MVP - 2 semanas)

Agora -> TOConline (Export):
- Botao "Exportar Rascunho Fatura"
- Gera JSON/CSV com dados da fatura
- User copia/cola ou envia por email para TOC

TOConline -> Agora (Import):
- TOC exporta faturas de TOConline (CSV)
- Botao "Importar Faturas TOConline" no Agora
- Upload CSV e parse automatico
- Matching automatico por NIF cliente + valor + data
- User confirma associacao a projetos

Estrutura CSV esperada:

numero_fatura,data_fatura,cliente_nif,cliente_nome,valor_sem_iva,iva,valor_total,estado
FT 2025/001,2025-11-15,123456789,Europalco Lda,10000.00,2300.00,12300.00,EMITIDA


Fase 2: Integracao OAuth (3 meses apos Fase 1)

Setup OAuth:
1. TOC fornece credenciais (client_id, client_secret)
2. Configurar em Agora: Empresa > Configuracoes > TOConline
3. User autoriza acesso (redirect OAuth)
4. Token guardado encriptado

Features:
- Sync bidirecional automatico
- Criacao de faturas via API
- Webhook (se disponivel)
- Retry automatico de erros

Periodicidade sync: Diaria ou tempo real


1.6 Estrutura de Dados
--------------------------------------------------

Campos em receitas:

ALTER TABLE receitas ADD COLUMN toconline_invoice_id INTEGER;
ALTER TABLE receitas ADD COLUMN toconline_sync_status VARCHAR(20);
  -- SYNC_OK | PENDING | ERROR | LOCAL_ONLY | DRAFT_SENT
ALTER TABLE receitas ADD COLUMN toconline_synced_at DATETIME;
ALTER TABLE receitas ADD COLUMN toconline_draft BOOLEAN DEFAULT FALSE;
ALTER TABLE receitas ADD COLUMN toconline_url TEXT;


Mapeamento Campos:

Campo Agora          Campo TOConline API         Notas
--------------------------------------------------------------------------------
cliente_id           customer_id                 Lookup via NIF
fatura_numero        document_number             TOConline pode gerar
data_fatura          document_date               -
descricao            lines[].description         -
valor_sem_iva        lines[].unit_price          -
taxa_iva             lines[].tax_code            "NOR" = 23%
iva_liquidado        Calculado                   -
projeto_id           -                           So no Agora


1.7 Exemplo Request API
--------------------------------------------------

Criar Fatura:

POST /api/v1/commercial_sales_documents
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "data": {
    "type": "commercial_sales_documents",
    "attributes": {
      "customer_id": 123,
      "document_date": "2025-11-22",
      "due_date": "2025-12-22",
      "currency_id": 1,
      "lines": [
        {
          "item_code": "SERV001",
          "description": "Producao Video Corporativo",
          "quantity": 1,
          "unit_price": 10000.00,
          "tax_code": "NOR"
        }
      ]
    }
  }
}


Listar Faturas (Sync):

GET /api/v1/commercial_sales_documents?filter[updated_at][gte]=2025-11-01
Authorization: Bearer {access_token}

Response:
{
  "data": [
    {
      "id": 456,
      "type": "commercial_sales_documents",
      "attributes": {
        "document_number": "FT 2025/001",
        "document_date": "2025-11-15",
        "customer_id": 123,
        "subtotal": 10000.00,
        "tax_amount": 2300.00,
        "total": 12300.00,
        "status": "EMITTED"
      }
    }
  ]
}


==================================================
2. INTEGRACAO BIZDOCS (DESPESAS)
==================================================

2.1 Visao Geral
--------------------------------------------------

Sistema: BizDocs - Arquivo Digital e Gestao Documental
Fornecedor: Latourrette Consulting
Source of Truth: BizDocs (despesas e documentos digitalizados)
Objetivo: Importar despesas aprovadas e associar a projetos


2.2 API Disponivel
--------------------------------------------------

Status: API existe mas requer parceria certificada
Acesso: Nao e self-service, requer contacto com Latourrette
Contacto: info@bizdocs.mobi | +351 935 107 344
Modelo: Integracao customizada por parceiro certificado
Custo estimado: 2.000 - 5.000 EUR setup (a negociar)

Integracoes conhecidas:
- Sage for Accountants (nativa)
- Primavera (nativa)
- PHC (via parceiro)


2.3 Alternativa: Export/Import Manual
--------------------------------------------------

BizDocs suporta exports:
- CIUS-PT (XML fatura eletronica)
- CSV (campos estruturados)
- Excel (via conversao)

Campos tipicos exportados:

- numero_documento
- data_documento
- fornecedor_nome
- fornecedor_nif
- valor_sem_iva
- iva
- valor_total
- categoria_despesa
- estado (aprovado/pendente)
- pdf_link (link para documento digitalizado)


2.4 Cenario Operacional
--------------------------------------------------

Fluxo recomendado (Fase 1 - Manual):

1. Despesa registada/scaneada no BizDocs
2. Workflow de aprovacao no BizDocs (se aplicavel)
3. Export CSV mensal/semanal do BizDocs
4. Upload CSV no Agora (botao "Importar BizDocs")
5. Parse automatico e criacao de despesas
6. Matching automatico com projetos:
   - Por fornecedor recorrente
   - Por palavras-chave na descricao
   - Por periodo de projeto ativo
7. User confirma/ajusta associacoes


2.5 Implementacao
--------------------------------------------------

Fase 1: Import CSV (MVP - 2 semanas)

Estrutura CSV esperada:

numero_doc,data,fornecedor_nome,fornecedor_nif,valor_sem_iva,iva,valor_total,categoria,pdf_link
DSP001,2025-11-15,Joao Silva,123456789,1000.00,230.00,1230.00,Freelancer Video,https://bizdocs.mobi/doc/123
DSP002,2025-11-16,Tech Store Lda,987654321,500.00,115.00,615.00,Equipamento,https://bizdocs.mobi/doc/124


Funcionalidades:
- Upload CSV via UI
- Parse e validacao automatica
- Criacao/update de fornecedores (via NIF)
- Criacao de despesas com estado PAGO
- Link para PDF no BizDocs (se disponivel)
- Sugestoes de match a projetos
- Log de import (sucessos/erros)


Codigo exemplo:

def importar_despesas_bizdocs_csv(file):
    """
    Import despesas de CSV exportado do BizDocs
    """
    results = {
        'total': 0,
        'sucesso': 0,
        'erro': 0,
        'erros': []
    }
    
    for row in csv.DictReader(file):
        results['total'] += 1
        
        try:
            # Criar/atualizar fornecedor
            fornecedor = Fornecedor.find_or_create(
                nif=row['fornecedor_nif'],
                defaults={
                    'nome': row['fornecedor_nome'],
                    'tipo': 'FREELANCER' if 'freelancer' in row['categoria'].lower() else 'EMPRESA'
                }
            )
            
            # Criar despesa
            despesa = Despesa.create({
                'numero': generate_numero_despesa(),
                'fornecedor_id': fornecedor.id,
                'data_despesa': parse_date(row['data']),
                'valor_sem_iva': Decimal(row['valor_sem_iva']),
                'iva_dedutivel': Decimal(row['iva']),
                'valor_c_iva': Decimal(row['valor_total']),
                'descricao': row['categoria'],
                'tipo': map_tipo_despesa(row['categoria']),
                'estado': 'PAGO',
                'bizdocs_doc_id': row['numero_doc'],
                'bizdocs_pdf_link': row.get('pdf_link'),
                'bizdocs_synced_at': now()
            })
            
            # Matching automatico a projeto
            sugestao = match_despesa_projeto(despesa)
            if sugestao:
                despesa.projeto_sugerido_id = sugestao['projeto_id']
                despesa.confianca_match = sugestao['score']
                despesa.save()
            
            results['sucesso'] += 1
            
        except Exception as e:
            results['erro'] += 1
            results['erros'].append({
                'linha': results['total'],
                'erro': str(e),
                'dados': row
            })
    
    # Criar log
    ImportLog.create({
        'tipo_import': 'BIZDOCS_DESPESAS',
        'ficheiro_nome': file.name,
        'num_registos': results['total'],
        'num_sucesso': results['sucesso'],
        'num_erro': results['erro'],
        'erros_detalhes': json.dumps(results['erros'])
    })
    
    return results


Fase 3: Integracao API (6+ meses) - Opcional

Quando: Se volume de despesas justificar automacao total

Processo:
1. Contactar Latourrette Consulting
2. Apresentar caso de uso e volume
3. Avaliacao de viabilidade
4. Parceiro certificado desenvolve integracao
5. Custo: negociar (estimativa 2-5k EUR setup)

Features esperadas (se API):
- Sync automatico diario/tempo real
- Webhook de novas despesas aprovadas
- Download automatico de PDFs
- Atualizacao de estados

Decisao: Avaliar apos 3-6 meses de uso do import manual


2.6 Estrutura de Dados
--------------------------------------------------

Campos em despesas:

ALTER TABLE despesas ADD COLUMN bizdocs_doc_id VARCHAR(50);
ALTER TABLE despesas ADD COLUMN bizdocs_pdf_link TEXT;
ALTER TABLE despesas ADD COLUMN bizdocs_synced_at DATETIME;
ALTER TABLE despesas ADD COLUMN bizdocs_categoria VARCHAR(100);


Mapeamento de Categorias:

BizDocs -> Agora:

Categoria BizDocs      Tipo Despesa Agora    Logica
---------------------------------------------------------------------------------
"Freelancer *"         PROJETO               Contem "freelancer"
"Equipamento *"        EQUIPAMENTO           Contem "equipamento"
"Escritorio *"         FIXA_MENSAL           Contem "escritorio" ou "fixo"
"Viagem BA *"          PESSOAL_BA            Contem "BA" ou "Bruno"
"Viagem RR *"          PESSOAL_RR            Contem "RR" ou "Rafael"
Outros                 PROJETO               Default


==================================================
3. INTEGRACAO BPI EMPRESAS (RECONCILIACAO BANCARIA)
==================================================

3.1 Visao Geral
--------------------------------------------------

Sistema: BPI Net Empresas
Objetivo: Reconciliar movimentos bancarios com receitas/despesas
Uso: Controlo de cash flow e validacao de pagamentos


3.2 Opcoes de Integracao
--------------------------------------------------

Opcao 1: Open Banking via SIBS API Market (Complexo)

Requisitos:
- Licenca PSD2 (AISP - Account Information Service Provider)
- Certificado eIDAS (QSEAL + QWAC)
- Registo Banco de Portugal
- Processo longo (meses) e caro

Custo: 5.000+ EUR setup, 100+/mes EUR

Conclusao: Nao recomendado para uso interno empresarial


Opcao 2: Agregador Terceiro (Tink, Plaid)

Fornecedor sugerido: Tink (agora Visa)
Cobertura: BPI + 20 bancos portugueses
Custo: 50-200 EUR/mes (variavel por volume)

Features:
- Acesso saldos e movimentos
- Categorizacao automatica
- API unificada

Conclusao: Avaliar em Fase 2/3 se reconciliacao manual for pesada


Opcao 3: Export Manual + Matching Inteligente (RECOMENDADO)

Processo:
1. Download extrato BPI Net Empresas (CSV ou OFX)
2. Upload no Agora
3. Parse automatico
4. Matching inteligente com receitas/despesas
5. Confirmacao manual de sugestoes

Custo: 0 EUR
Complexidade: Baixa
Prazo: 2-3 semanas implementacao


3.3 Cenario Operacional
--------------------------------------------------

Fluxo recomendado:

1. Export mensal do BPI:
   - Login BPI Net Empresas
   - Conta > Movimentos > Exportar (CSV ou OFX)
   - Periodo: ultimo mes

2. Import no Agora:
   - Botao "Importar Extrato Bancario"
   - Upload ficheiro
   - Parse e validacao

3. Matching automatico:
   - Por valor exato + range datas (+-3 dias)
   - Por referencia multibanco (se disponivel)
   - Por descricao (fuzzy matching com fornecedor/cliente)
   - Score de confianca (0-100%)

4. Revisao manual:
   - UI mostra sugestoes ordenadas por confianca
   - User confirma, rejeita ou pesquisa manualmente
   - Transacoes reconciliadas ficam marcadas

5. Estados:
   - POR_RECONCILIAR (nova transacao)
   - RECONCILIADO (confirmado)
   - DESCARTADO (movimento interno/irrelevante)


3.4 Implementacao
--------------------------------------------------

Fase 1: Import + Matching (MVP - 3 semanas)

Estrutura CSV esperada (formato BPI):

Data Mov.,Data Valor,Descricao,Debito,Credito,Saldo,Ref.
15/11/2025,15/11/2025,TRANSF EUROPALCO LDA,,12300.00,45600.00,REF123456789
16/11/2025,16/11/2025,TRANSF JOAO SILVA FREELANCER,1230.00,,44370.00,


Algoritmo de Matching:

def match_transacao_bancaria(transacao):
    """
    Sugere match de transacao bancaria com receita ou despesa
    Retorna lista de sugestoes ordenadas por score
    """
    sugestoes = []
    
    if transacao.tipo == 'CREDITO':
        # Tentar match com receitas
        receitas_candidatas = Receita.filter(
            valor_c_iva__range=(transacao.valor * 0.98, transacao.valor * 1.02),
            data_recebimento__range=(
                transacao.data_valor - timedelta(days=5),
                transacao.data_valor + timedelta(days=5)
            ),
            estado='EMITIDO'  # Ainda nao recebida
        )
        
        for receita in receitas_candidatas:
            score = 0
            
            # Valor exato: +50 pontos
            if abs(receita.valor_c_iva - transacao.valor) < 0.01:
                score += 50
            # Valor proximo (+-2%): +30 pontos
            elif abs(receita.valor_c_iva - transacao.valor) / transacao.valor < 0.02:
                score += 30
            
            # Data exata: +30 pontos
            if receita.data_fatura == transacao.data_valor:
                score += 30
            # Data proxima (+-3 dias): +15 pontos
            elif abs((receita.data_fatura - transacao.data_valor).days) <= 3:
                score += 15
            
            # Cliente no nome transacao: +20 pontos
            if fuzzy_match(receita.cliente.nome, transacao.descricao) > 0.8:
                score += 20
            
            sugestoes.append({
                'tipo': 'RECEITA',
                'id': receita.id,
                'objeto': receita,
                'score': score,
                'motivo': f"Valor: {score_valor(receita, transacao)} | Data: {score_data(receita, transacao)}"
            })
    
    else:  # DEBITO
        # Tentar match com despesas
        despesas_candidatas = Despesa.filter(
            valor_c_iva__range=(abs(transacao.valor) * 0.98, abs(transacao.valor) * 1.02),
            data_pagamento__range=(
                transacao.data_valor - timedelta(days=5),
                transacao.data_valor + timedelta(days=5)
            ),
            estado='PENDENTE'  # Ainda nao paga
        )
        
        for despesa in despesas_candidatas:
            score = 0
            
            # Similar ao credito
            if abs(despesa.valor_c_iva - abs(transacao.valor)) < 0.01:
                score += 50
            
            if despesa.data_despesa == transacao.data_valor:
                score += 30
            
            if fuzzy_match(despesa.fornecedor.nome, transacao.descricao) > 0.8:
                score += 20
            
            sugestoes.append({
                'tipo': 'DESPESA',
                'id': despesa.id,
                'objeto': despesa,
                'score': score,
                'motivo': f"Valor: {...} | Data: {...} | Fornecedor: {...}"
            })
    
    # Ordenar por score descendente
    sugestoes.sort(key=lambda x: x['score'], reverse=True)
    
    return sugestoes[:5]  # Top 5 sugestoes


def confirmar_reconciliacao(transacao_id, tipo, entidade_id):
    """
    Confirma reconciliacao de transacao com receita ou despesa
    """
    transacao = TransacaoBancaria.get(transacao_id)
    
    if tipo == 'RECEITA':
        receita = Receita.get(entidade_id)
        receita.estado = 'RECEBIDO'
        receita.data_recebimento = transacao.data_valor
        receita.save()
        
        transacao.tipo_matching = 'RECEITA'
        transacao.receita_id = receita.id
        
    elif tipo == 'DESPESA':
        despesa = Despesa.get(entidade_id)
        despesa.estado = 'PAGO'
        despesa.data_pagamento = transacao.data_valor
        despesa.save()
        
        transacao.tipo_matching = 'DESPESA'
        transacao.despesa_id = despesa.id
    
    transacao.estado = 'RECONCILIADO'
    transacao.confirmado_manual = True
    transacao.save()


3.5 Estrutura de Dados
--------------------------------------------------

Tabela transacoes_bancarias:

CREATE TABLE transacoes_bancarias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Dados da transacao
    data_transacao DATE NOT NULL,
    data_valor DATE,
    descricao TEXT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    saldo_apos DECIMAL(10,2),
    referencia VARCHAR(50),
    tipo VARCHAR(10) NOT NULL,  -- CREDITO | DEBITO
    
    -- Estado reconciliacao
    estado VARCHAR(20) DEFAULT 'POR_RECONCILIAR',
      -- POR_RECONCILIAR | RECONCILIADO | DESCARTADO
    
    -- Matching
    tipo_matching VARCHAR(20),  -- DESPESA | RECEITA | OUTRO
    despesa_id INTEGER,
    receita_id INTEGER,
    confianca_matching INTEGER,  -- 0-100
    confirmado_manual BOOLEAN DEFAULT FALSE,
    
    -- Import
    ficheiro_origem VARCHAR(255),
    import_id INTEGER,
    
    -- Metadata
    notas TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (despesa_id) REFERENCES despesas(id) ON DELETE SET NULL,
    FOREIGN KEY (receita_id) REFERENCES receitas(id) ON DELETE SET NULL,
    FOREIGN KEY (import_id) REFERENCES import_log(id) ON DELETE SET NULL
);

CREATE INDEX idx_transacoes_data_valor ON transacoes_bancarias(data_valor);
CREATE INDEX idx_transacoes_estado ON transacoes_bancarias(estado);
CREATE INDEX idx_transacoes_tipo ON transacoes_bancarias(tipo);
CREATE INDEX idx_transacoes_valor ON transacoes_bancarias(valor);


3.6 UI de Reconciliacao
--------------------------------------------------

Tela: ReconciliacaoScreen

RECONCILIACAO BANCARIA - Novembro 2025
================================================================================

[Importar Extrato]  [Dashboard]  [Config]

--------------------------------------------------------------------------------

Transacao TB00123 - POR RECONCILIAR

Data: 15/11/2025
Descricao: TRANSF EUROPALCO LDA
Valor: 12.300,00 EUR (credito)
Saldo apos: 45.600,00 EUR

Sugestoes (ordenadas por confianca):

  [ ] RECEITA R000145 - 95% confianca                          [Confirmar]
      Projeto P0050 - Evento Corporativo
      Cliente: Europalco Lda
      Fatura: FT 2025/001
      Valor: 12.300,00 EUR (exato)
      Data fatura: 14/11/2025 (1 dia diff)
      Estado: EMITIDO -> RECEBIDO

  [ ] RECEITA R000132 - 45% confianca                          [Confirmar]
      Valor: 12.500,00 EUR (diff 200 EUR)
      Data: 10/11/2025 (5 dias diff)

[Descartar]  [Procurar Manual]  [Proximo]

--------------------------------------------------------------------------------

Status: 12 por reconciliar | 45 reconciliadas | 3 descartadas


Funcionalidades:
- Lista de transacoes nao reconciliadas
- Filtros: periodo, tipo (credito/debito), valor
- Sugestoes automaticas com score
- Confirmacao 1-click
- Pesquisa manual (caso sugestoes nao sirvam)
- Bulk actions (descartar multiplas)
- Export reconciliacoes (Excel)


==================================================
4. ESTRUTURA GLOBAL - LOGS E AUDITORIA
==================================================

4.1 Tabela import_log
--------------------------------------------------

CREATE TABLE import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_import VARCHAR(20) NOT NULL,
      -- TOCONLINE_RECEITAS | BIZDOCS_DESPESAS | BPI_EXTRATO
    
    ficheiro_nome VARCHAR(255),
    ficheiro_hash VARCHAR(64),  -- SHA256 para evitar duplicados
    
    data_import DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    
    num_registos INTEGER DEFAULT 0,
    num_sucesso INTEGER DEFAULT 0,
    num_erro INTEGER DEFAULT 0,
    num_duplicados INTEGER DEFAULT 0,
    
    erros_detalhes TEXT,  -- JSON com erros
    
    status VARCHAR(20) DEFAULT 'CONCLUIDO',
      -- EM_PROGRESSO | CONCLUIDO | ERRO
    
    FOREIGN KEY (user_id) REFERENCES usuarios(id)
);

CREATE INDEX idx_import_log_tipo ON import_log(tipo_import);
CREATE INDEX idx_import_log_data ON import_log(data_import);
CREATE INDEX idx_import_log_hash ON import_log(ficheiro_hash);


4.2 Dashboard de Integracoes
--------------------------------------------------

UI: IntegracoesScreen

INTEGRACOES - Dashboard
================================================================================

TOConline (Faturas)                                             ATIVO
  Ultima sincronizacao: 22/11/2025 09:00
  Faturas importadas: 156 (ultimo mes: 12)
  Estado: OAuth ativo, token valido ate 22/12/2025
  [Sincronizar Agora]  [Configurar]

BizDocs (Despesas)                                              MANUAL
  Ultimo import: 15/11/2025
  Despesas importadas: 342 (ultimo import: 28)
  Proximo import sugerido: 22/11/2025
  [Importar CSV]  [Ver Historico]

BPI Empresas (Reconciliacao)                                    MANUAL
  Ultimo import: 20/11/2025
  Transacoes: 89 (por reconciliar: 12)
  Taxa reconciliacao: 87% (78/89)
  [Importar Extrato]  [Reconciliar]

================================================================================

Historico de Imports (ultimos 7 dias)

22/11 09:00  TOConline     5 faturas      Sucesso
20/11 14:30  BPI Extrato   34 transacoes  Sucesso
15/11 10:15  BizDocs       28 despesas    Sucesso
14/11 16:45  TOConline     3 faturas      1 erro

[Ver Log Completo]


==================================================
5. ROADMAP DE IMPLEMENTACAO
==================================================

FASE 1: MVPs Manuais (PRIORITARIO - 4-6 semanas)
--------------------------------------------------

Objetivo: Implementar imports manuais funcionais

Sprint 1: TOConline - Import Receitas (2 semanas)
- Upload CSV TOConline
- Parser e validacao
- Criacao/update receitas
- Matching automatico clientes (NIF)
- Sugestao de link a projetos
- Log de imports

Sprint 2: BizDocs - Import Despesas (2 semanas)
- Upload CSV BizDocs
- Parser e validacao
- Criacao/update fornecedores e despesas
- Matching automatico a projetos
- Link para PDFs no BizDocs
- Log de imports

Sprint 3: BPI - Import Extrato + Matching (2-3 semanas)
- Upload CSV/OFX BPI
- Parser e validacao
- Criacao de transacoes bancarias
- Algoritmo de matching inteligente
- UI de reconciliacao
- Confirmacao e atualizacao de estados
- Dashboard de reconciliacao

Sprint 4: Dashboard Integracoes (1 semana)
- Tela central de integracoes
- Status de cada sistema
- Historico de imports
- Botoes de acao rapida

Entregaveis Fase 1:
- Import CSV funcional para 3 sistemas
- Matching automatico inteligente
- UI de reconciliacao completa
- Logs e auditoria
- Sistema 100% funcional sem APIs


FASE 2: OAuth TOConline (3 meses apos Fase 1)
--------------------------------------------------

Pre-requisitos:
- Fase 1 validada e em uso
- Credenciais OAuth obtidas de TOC
- Processo manual funciona bem

Tarefas:
- Implementar OAuth2 flow
- Configuracao em UI
- Sync automatico diario
- Criacao de faturas via API
- Webhook (se disponivel)
- Retry e error handling

Entregaveis Fase 2:
- Integracao API TOConline completa
- Sync bidirecional
- Reducao de trabalho manual


FASE 3: Otimizacoes e Avaliacoes (6+ meses)
--------------------------------------------------

Avaliar necessidade de:

1. API BizDocs (se volume despesas justificar)
   - Contactar Latourrette
   - Analise custo-beneficio
   - Decisao: API ou manter CSV

2. Agregador Bancario (Tink) (se reconciliacao manual pesada)
   - Teste sandbox Tink
   - Analise custo vs tempo poupado
   - Decisao: API ou manter CSV

3. Webhooks e tempo real
   - Se disponiveis nos sistemas
   - Avaliacao de ROI

Entregaveis Fase 3:
- Sistema otimizado
- Decisoes baseadas em uso real
- Automacao adicional se justificada


==================================================
6. DOCUMENTACAO COMPLEMENTAR
==================================================

Ficheiros Relacionados
--------------------------------------------------

- FISCAL.md - Obrigacoes fiscais e calculos
- DATABASE_SCHEMA.md - Schema completo (atualizar com novas tabelas)
- ARCHITECTURE.md - Arquitetura geral (atualizar com integracoes)
- TODO.md - Adicionar sprints de implementacao


Contactos Importantes
--------------------------------------------------

TOConline:
- Suporte: suporte@toconline.pt
- API: Via TOC da empresa

BizDocs:
- Email: info@bizdocs.mobi
- Telefone: +351 935 107 344
- Website: https://bizdocs.mobi

Agora (Tecnico):
- Bruno Amaral - bruno@agoramedia.pt
- Rafael Reigota - rafael@agoramedia.pt


==================================================

Ultima atualizacao: 22/11/2025
Proxima revisao: Apos conclusao Fase 1

==================================================
