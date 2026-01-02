# Análise Completa: Importação de Excel para Django

**Data:** 31 Dezembro 2025
**Ficheiro Analisado:** `excel/CONTABILIDADE_FINAL_20251231.xlsx`
**Objetivo:** Extrair lógica de negócio e dados da Google Sheet para integração na aplicação Django

---

## 📋 Índice

1. [Resumo Executivo](#resumo-executivo)
2. [Análise por Aba](#análise-por-aba)
3. [Alterações aos Models Django](#alterações-aos-models-django)
4. [Estratégia de Import](#estratégia-de-import)
5. [Regras de Negócio](#regras-de-negócio)
6. [Validações e Edge Cases](#validações-e-edge-cases)

---

## 📊 Resumo Executivo

### Abas Analisadas (9 total)

| Aba | Tipo | Importar? | Prioridade |
|-----|------|-----------|------------|
| **PROJETOS** | Dados | ✅ Sim | 🔴 Alta |
| **DESPESAS** | Dados | ✅ Parcial | 🔴 Alta |
| **FORNECEDORES** | Dados | ✅ Sim | 🟡 Média |
| **CLIENTES** | Dados | ✅ Sim | 🟡 Média |
| **SALDO_BANCARIO** | Dashboard | ❌ Não | - |
| **CONSULTA_INCOMESOUTCOMES** | Dashboard | ❌ Não | - |
| **CAIXA** | Dashboard | ❌ Não | - |
| **LUCROS** | Calculadora IRC | ❌ Não | - |
| **2024** | View DESPESAS | ❌ Não | - |

### Decisões Críticas

1. **Tipos Compostos de Despesas**: Implementar sistema de tags (ManyToMany)
2. **Despesas "Pessoal"**: Converter em Boletins simplificados
3. **Prémios**: Agregar de DESPESAS → campos `premio_bruno/rafael` em Projeto
4. **Sócios como Clientes**: Ignorar (#C0001, #C0002)
5. **Abas de Dashboard**: Não importar (lógica já no Django via SaldosCalculator)

---

## 🗂️ Análise por Aba

### 1️⃣ PROJETOS (✅ Importar - Alta Prioridade)

**Estrutura:** ~1701 projetos
**Header Row:** Linha 3

#### Headers Encontrados

```
[1]  Nº PROJETO
[2]  CLIENTE (texto)
[3]  DATA INÍCIO
[4]  DATA FIM
[5]  PROJETO (descrição)
[6]  VALOR s/IVA
[7]  DATA FATURAÇÃO
[8]  DATA VENCIMENTO
[9]  DATA RECIBO ⚠️ NOVO CAMPO
[10] ORÇAMENTO (link)
[11] EQUIPA (número) ⚠️ NOVO CAMPO
[12] RECURSOS HUMANOS (texto) ⚠️ NOVO CAMPO
[13] EQUIPAMENTO (texto) ⚠️ NOVO CAMPO
[14] LOCAL (texto) ⚠️ NOVO CAMPO
[15] ESTADO (mistura TIPO + ESTADO!)
[16] OWNER (nome completo do sócio)
[17] NOTAS
[18] VALOR c/IVA
[19] IVA
[32] ESTATUTO
```

#### Mapeamento Django

| Excel | Django Model Field | Transformação |
|-------|-------------------|---------------|
| Nº PROJETO | `numero` | Direto |
| CLIENTE | `cliente` FK | Lookup por nome |
| DATA INÍCIO | `data_inicio` | Direto |
| DATA FIM | `data_fim` | Direto |
| PROJETO | `descricao` | Direto |
| VALOR s/IVA | `valor_sem_iva` | Direto |
| DATA FATURAÇÃO | `data_faturacao` | Direto |
| DATA VENCIMENTO | `data_vencimento` | Direto |
| **DATA RECIBO** | `data_recibo` | ⚠️ Adicionar campo |
| **ORÇAMENTO** | `orcamento_url` | ⚠️ Adicionar campo |
| **EQUIPA** | `equipa` | ⚠️ Adicionar campo |
| **RECURSOS HUMANOS** | `recursos_humanos` | ⚠️ Adicionar campo |
| **EQUIPAMENTO** | `equipamento_usado` | ⚠️ Adicionar campo |
| **LOCAL** | `local` | ⚠️ Adicionar campo |
| ESTADO | `tipo` + `estado` | Ver lógica abaixo |
| OWNER | `socio` FK | Lookup por nome |

#### Lógica ESTADO → tipo + estado

**Regra 1: Determinar TIPO**
```python
if ESTADO == "Pessoal":
    tipo = TipoProjeto.PESSOAL
else:
    tipo = TipoProjeto.EMPRESA
```

**Regra 2: Determinar ESTADO**
```python
if data_recibo is not None:
    estado = EstadoProjeto.PAGO
elif ESTADO == "Pessoal":
    if data_fim < today:
        estado = EstadoProjeto.FINALIZADO
    else:
        estado = EstadoProjeto.ATIVO
elif ESTADO == "Finalizado":
    estado = EstadoProjeto.FINALIZADO
elif ESTADO == "Em Espera":
    estado = EstadoProjeto.ATIVO
else:
    estado = EstadoProjeto.ATIVO  # Default
```

#### Campos a Adicionar ao Model `Projeto`

```python
class Projeto(models.Model):
    # ... campos existentes ...

    # NOVOS CAMPOS
    data_recibo = models.DateField(
        _('Data Recibo'),
        blank=True,
        null=True,
        help_text='Data em que o cliente pagou'
    )
    orcamento_url = models.URLField(
        _('Link Orçamento'),
        max_length=500,
        blank=True,
        null=True
    )
    equipa = models.IntegerField(
        _('Tamanho Equipa'),
        blank=True,
        null=True,
        help_text='Número de pessoas na equipa'
    )
    recursos_humanos = models.TextField(
        _('Recursos Humanos'),
        blank=True,
        null=True,
        help_text='Nomes das pessoas que trabalharam'
    )
    equipamento_usado = models.TextField(
        _('Equipamento Usado'),
        blank=True,
        null=True
    )
    local = models.CharField(
        _('Local'),
        max_length=200,
        blank=True,
        null=True
    )
```

---

### 2️⃣ DESPESAS (✅ Importar Parcialmente - Alta Prioridade)

**Estrutura:** ~976 despesas
**Header Row:** Linha 5

#### Headers Encontrados

```
[1]  Nº DESPESAS
[2]  ANO
[3]  MÊS
[4]  DIA
[5]  CREDOR
[6]  PROJETO (número)
[7]  TIPO ⚠️ COMPOSTOS!
[8]  DESCRIÇÃO
[9]  PERIODICIDADE
[10] VALOR (s/IVA)
[11] VALOR IVA
[12] IRS RETIDO
[13] VALOR (c/IVA)
[14] QUANTIDADE
[15] DIAS
[16-19] TOTAIS (calculados)
[20] DATA DE VENCIMENTO
[21] OUT
[22] ATIVO
[23] NOTAS
```

#### Tipos de Despesas Encontrados (28 únicos!)

**CRÍTICO: Tipos são COMPOSTOS** (ex: "Prémio, Serviço, Equipamento")

**Top 10:**
1. Administrativo (64)
2. Serviço (48)
3. Ordenado (30)
4. Sub. Alimentação (30)
5. Deslocação, Pessoal (24) → **Vira BOLETIM**
6. Per Diem PT, Pessoal (24) → **Vira BOLETIM**
7. Alimentação (23)
8. Equipamento (17)
9. Prémio, Serviço, Equipamento (11) → **DESCARTAR**
10. IRS Retenção (8)

#### Estratégias por Tipo

| Tipo na Sheet | Ação | Destino |
|---------------|------|---------|
| **Contém "Prémio" ou "Comissão"** | Agregar → popular `projeto.premio_*` | ❌ Descartar despesa |
| **"Deslocação, Pessoal" / "Per Diem, Pessoal"** | Converter em Boletim | ✅ Model Boletim |
| **Outros tipos** | Importar com tags | ✅ Model Despesa |

#### Implementação: Sistema de Tags

**Criar novo model:**

```python
class TagDespesa(models.Model):
    codigo = models.CharField(max_length=50, unique=True, primary_key=True)
    nome = models.CharField(max_length=100)
    impacta_saldos = models.BooleanField(default=False)
    impacta_irc = models.BooleanField(default=False)
    ordem = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('Tag de Despesa')
        verbose_name_plural = _('Tags de Despesa')
        ordering = ['ordem', 'nome']
```

**Alterar model Despesa:**

```python
class Despesa(models.Model):
    # ... campos existentes ...

    # SUBSTITUIR
    # tipo = CharField(choices=TipoDespesa.choices)  ← Remover

    # ADICIONAR
    tags = models.ManyToManyField(
        TagDespesa,
        related_name='despesas',
        verbose_name=_('Tags')
    )
    tipo_original = models.CharField(
        _('Tipo Original'),
        max_length=200,
        blank=True,
        help_text='Tipo original da sheet (auditoria)'
    )

    # Helper methods
    def has_tag(self, codigo):
        return self.tags.filter(codigo=codigo).exists()

    @property
    def is_pessoal(self):
        return self.has_tag('PESSOAL')

    @property
    def is_fixa_mensal(self):
        return self.has_tag('ADMINISTRATIVO') or \
               self.has_tag('ORDENADO') or \
               self.has_tag('SUB_ALIMENTACAO')
```

#### Tags a Criar (Fixtures)

```python
# fixtures/tags_despesa.json
[
    {
        "codigo": "EQUIPAMENTO",
        "nome": "Equipamento",
        "impacta_saldos": false,
        "impacta_irc": true
    },
    {
        "codigo": "PESSOAL",
        "nome": "Pessoal",
        "impacta_saldos": true,
        "impacta_irc": true
    },
    {
        "codigo": "SERVICO",
        "nome": "Serviço",
        "impacta_saldos": false,
        "impacta_irc": true
    },
    {
        "codigo": "PREMIO",
        "nome": "Prémio",
        "impacta_saldos": true,
        "impacta_irc": false
    },
    {
        "codigo": "COMISSAO_VENDA",
        "nome": "Comissão de Venda",
        "impacta_saldos": true,
        "impacta_irc": false
    },
    {
        "codigo": "ADMINISTRATIVO",
        "nome": "Administrativo",
        "impacta_saldos": true,
        "impacta_irc": true
    },
    {
        "codigo": "ORDENADO",
        "nome": "Ordenado",
        "impacta_saldos": true,
        "impacta_irc": true
    },
    {
        "codigo": "SUB_ALIMENTACAO",
        "nome": "Sub. Alimentação",
        "impacta_saldos": true,
        "impacta_irc": true
    },
    {
        "codigo": "ALIMENTACAO",
        "nome": "Alimentação",
        "impacta_saldos": false,
        "impacta_irc": true
    },
    {
        "codigo": "PRODUCAO",
        "nome": "Produção",
        "impacta_saldos": false,
        "impacta_irc": true
    },
    {
        "codigo": "DESLOCACAO",
        "nome": "Deslocação",
        "impacta_saldos": false,
        "impacta_irc": true
    },
    {
        "codigo": "PER_DIEM_PT",
        "nome": "Per Diem Portugal",
        "impacta_saldos": true,
        "impacta_irc": true
    },
    {
        "codigo": "PER_DIEM_FORA",
        "nome": "Per Diem Estrangeiro",
        "impacta_saldos": true,
        "impacta_irc": true
    },
    {
        "codigo": "IRS_RETENCAO",
        "nome": "IRS Retenção",
        "impacta_saldos": false,
        "impacta_irc": false
    }
]
```

#### Lógica de Import - Despesas → Boletins

**Despesas tipo "Deslocação, Pessoal" / "Per Diem, Pessoal":**

```python
def convert_despesas_to_boletins(despesas_pessoais):
    """
    Agrupa despesas pessoais por (Sócio, Mês, Ano) e cria Boletins
    """
    # Agrupar por sócio + mês/ano
    grupos = {}
    for desp in despesas_pessoais:
        socio = lookup_socio_by_name(desp.credor)  # "Bruno Amaral" → BA
        chave = (socio, desp.ano, desp.mes)

        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(desp)

    # Criar Boletim para cada grupo
    for (socio, ano, mes), despesas in grupos.items():
        # Verificar estado (PAGO se alguma tem data vencimento)
        datas_venc = [d.data_vencimento for d in despesas if d.data_vencimento]
        estado = EstadoBoletim.PAGO if datas_venc else EstadoBoletim.PENDENTE
        data_pag = max(datas_venc) if datas_venc else None

        # Criar Boletim simplificado (sem linhas)
        Boletim.objects.create(
            socio=socio,
            mes=mes,
            ano=ano,
            descricao=get_month_name(mes),  # "Janeiro", "Fevereiro"...
            data_emissao=date(ano, mes, 27),  # Fixo dia 27
            data_pagamento=data_pag,
            valor_total=sum(d.valor_sem_iva for d in despesas),
            estado=estado,
            # Campos de referência = None (histórico)
            # SEM BoletimLinhas
        )
```

#### Lógica de Import - Prémios → Projeto

**Despesas tipo "Prémio, ..." ou "Comissão venda":**

```python
def aggregate_premios_to_projetos(despesas_premio):
    """
    Agrupa prémios por Projeto e popula campos premio_bruno/premio_rafael
    """
    premios_por_projeto = {}

    for desp in despesas_premio:
        if not desp.projeto:
            continue  # Skip prémios sem projeto

        projeto_id = desp.projeto.id
        socio = lookup_socio_by_name(desp.credor)  # "Bruno Amaral" → BA

        if projeto_id not in premios_por_projeto:
            premios_por_projeto[projeto_id] = {'BA': 0, 'RR': 0}

        premios_por_projeto[projeto_id][socio.codigo] += desp.valor_sem_iva

    # Atualizar projetos
    for projeto_id, premios in premios_por_projeto.items():
        Projeto.objects.filter(id=projeto_id).update(
            premio_bruno=premios['BA'],
            premio_rafael=premios['RR']
        )
```

---

### 3️⃣ FORNECEDORES (✅ Importar - Média Prioridade)

**Estrutura:** ~47 fornecedores
**Header Row:** Linha 1

#### Mapeamento Direto

Quase 1:1 com model Django `Fornecedor`.

#### ESTATUTO: Adicionar "BANCO"

```python
class EstatutoFornecedor(models.TextChoices):
    EMPRESA = 'EMPRESA', _('Empresa')
    FREELANCER = 'FREELANCER', _('Freelancer')
    ESTADO = 'ESTADO', _('Estado')
    BANCO = 'BANCO', _('Banco')  # ← NOVO
    SOCIO_GERENTE = 'SOCIO_GERENTE', _('Sócio Gerente')  # ← OPCIONAL
```

#### Transformações

- **CLASSIFICAÇÃO**: "★★★★★" → IntegerField (contar estrelas)

---

### 4️⃣ CLIENTES (✅ Importar - Média Prioridade)

**Estrutura:** ~40 clientes
**Header Row:** Linha 1

#### Mapeamento Direto

Quase 1:1 com model Django `Cliente`.

#### ⚠️ IGNORAR Sócios

```python
SKIP_CLIENTES = ['#C0001', '#C0002']  # Rafael Reigota, Bruno Amaral

def import_clientes(sheet_rows):
    for row in sheet_rows:
        if row['Nº CLIENTE'] in SKIP_CLIENTES:
            continue  # Skip sócios

        Cliente.objects.update_or_create(
            numero=row['Nº CLIENTE'],
            defaults={
                'nome': row['CLIENTE'],
                'nome_formal': row['CLIENTE'],  # Mesma coisa na sheet
                'nif': row['NIF'],
                'morada': row['MORADA'],
                'pais': row['PAÍS'] or 'Portugal',
                'angariacao': row['ANGARIAÇÃO'],
                'nota': row['NOTA'],
            }
        )
```

---

### 5️⃣ SALDO_BANCARIO (❌ Não Importar)

**Tipo:** Registo de transferências bancárias (incomes)

**Conteúdo:**
- Transferências de clientes (pagamentos) → **Redundante** com `Projeto.data_recibo`
- Transferências de sócios (investimentos) → **Referência histórica** (pode adicionar feature futura)

**Decisão:** Descartar por agora. Opcionalmente criar model `InvestimentoSocio` no futuro.

---

### 6️⃣ CONSULTA_INCOMESOUTCOMES (❌ Não Importar)

**Tipo:** Dashboard de cálculo de saldos pessoais

**Fórmula encontrada:**
```
Saldo = (Projetos_Pessoais + Prémios) - (Despesas_Pessoais + Despesas_Outros_Credores)
```

**Validação:** ✅ Lógica já implementada no Django via `SaldosCalculator`

**Decisão:** Não importar (é apenas visualização).

---

### 7️⃣ CAIXA (❌ Não Importar)

**Tipo:** Outra forma de calcular saldos pessoais

**Decisão:** Não importar (dashboard de visualização).

---

### 8️⃣ LUCROS (❌ Não Importar)

**Tipo:** Calculadora de IRC

**Conteúdo:** Fórmulas fiscais (RAI, IRC, Tributação Autónoma, Derrama)

**Decisão:** Não importar dados. **Feature futura:** Implementar relatório fiscal.

---

### 9️⃣ 2024 (❌ Não Importar)

**Tipo:** View filtrado de DESPESAS (ano 2024)

**Decisão:** Dados duplicados. Não importar.

---

## 🔧 Alterações aos Models Django

### Resumo de Alterações

| Model | Ação | Campos |
|-------|------|--------|
| `Projeto` | ✏️ Adicionar campos | `data_recibo`, `orcamento_url`, `equipa`, `recursos_humanos`, `equipamento_usado`, `local` |
| `Despesa` | 🔄 Refatorar | Remover `tipo` CharField, adicionar `tags` M2M + `tipo_original` |
| `TagDespesa` | ➕ Criar novo | Model completo |
| `EstatutoFornecedor` | ✏️ Adicionar choices | `BANCO`, (`SOCIO_GERENTE`) |
| `Boletim` | ✅ Sem alterações | - |
| `Cliente` | ✅ Sem alterações | - |
| `Fornecedor` | ✅ Sem alterações | - |

### Migration Script

```python
# agora_web/core/migrations/0XXX_excel_import_fields.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0XXX_previous_migration'),
    ]

    operations = [
        # 1. Criar TagDespesa
        migrations.CreateModel(
            name='TagDespesa',
            fields=[
                ('codigo', models.CharField(max_length=50, primary_key=True)),
                ('nome', models.CharField(max_length=100)),
                ('impacta_saldos', models.BooleanField(default=False)),
                ('impacta_irc', models.BooleanField(default=False)),
                ('ordem', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Tag de Despesa',
                'verbose_name_plural': 'Tags de Despesa',
                'ordering': ['ordem', 'nome'],
                'db_table': 'tags_despesa',
            },
        ),

        # 2. Adicionar campos ao Projeto
        migrations.AddField(
            model_name='projeto',
            name='data_recibo',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projeto',
            name='orcamento_url',
            field=models.URLField(max_length=500, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projeto',
            name='equipa',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projeto',
            name='recursos_humanos',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projeto',
            name='equipamento_usado',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projeto',
            name='local',
            field=models.CharField(max_length=200, blank=True, null=True),
        ),

        # 3. Adicionar campos ao Despesa
        migrations.AddField(
            model_name='despesa',
            name='tipo_original',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='despesa',
            name='tags',
            field=models.ManyToManyField(
                related_name='despesas',
                to='core.TagDespesa'
            ),
        ),

        # 4. Atualizar choices de EstatutoFornecedor (manual no models.py)
    ]
```

---

## 🚀 Estratégia de Import

### Ordem de Execução

```
1. FORNECEDORES  → Criar credores primeiro
2. CLIENTES      → Criar clientes (skip sócios)
3. PROJETOS      → Importar projetos
4. DESPESAS      → Processar em 3 fases:
   4a. Prémios   → Agregar para projeto.premio_*
   4b. Pessoais  → Converter em Boletins
   4c. Normais   → Importar como Despesas com tags
```

### Management Command

```bash
python manage.py import_from_excel --file excel/CONTABILIDADE_FINAL_20251231.xlsx
```

### Estrutura do Command

```python
# agora_web/core/management/commands/import_from_excel.py

class Command(BaseCommand):
    help = 'Importa dados da Google Sheet (Excel export)'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        wb = openpyxl.load_workbook(options['file'], data_only=True)

        # 1. Fornecedores
        self.stdout.write('Importando Fornecedores...')
        self.import_fornecedores(wb['FORNECEDORES'])

        # 2. Clientes
        self.stdout.write('Importando Clientes...')
        self.import_clientes(wb['CLIENTES'])

        # 3. Projetos
        self.stdout.write('Importando Projetos...')
        self.import_projetos(wb['PROJETOS'])

        # 4. Despesas (3 fases)
        self.stdout.write('Processando Despesas...')
        despesas_raw = self.parse_despesas(wb['DESPESAS'])

        self.stdout.write('  - Agregando prémios...')
        self.aggregate_premios(despesas_raw['premios'])

        self.stdout.write('  - Criando boletins...')
        self.create_boletins(despesas_raw['pessoais'])

        self.stdout.write('  - Importando despesas normais...')
        self.import_despesas(despesas_raw['normais'])

        self.stdout.write(self.style.SUCCESS('Import completo!'))
```

### Pseudocódigo Import

```python
def import_projetos(ws):
    header_row = 3

    for row_idx in range(header_row + 1, ws.max_row + 1):
        # Parse row
        numero = ws.cell(row_idx, 1).value
        cliente_nome = ws.cell(row_idx, 2).value
        estado_sheet = ws.cell(row_idx, 15).value
        owner_nome = ws.cell(row_idx, 16).value
        data_recibo = ws.cell(row_idx, 9).value
        # ...

        # Lookups
        cliente = Cliente.objects.filter(nome=cliente_nome).first()
        socio = Socio.objects.filter(nome_completo=owner_nome).first()

        # Determinar tipo e estado
        if estado_sheet == "Pessoal":
            tipo = TipoProjeto.PESSOAL
            if data_recibo:
                estado = EstadoProjeto.PAGO
            elif data_fim < today:
                estado = EstadoProjeto.FINALIZADO
            else:
                estado = EstadoProjeto.ATIVO
        else:
            tipo = TipoProjeto.EMPRESA
            if data_recibo:
                estado = EstadoProjeto.PAGO
            elif estado_sheet == "Finalizado":
                estado = EstadoProjeto.FINALIZADO
            else:
                estado = EstadoProjeto.ATIVO

        # Create/Update
        Projeto.objects.update_or_create(
            numero=numero,
            defaults={
                'tipo': tipo,
                'estado': estado,
                'cliente': cliente,
                'socio': socio,
                'data_recibo': data_recibo,
                # ... todos os campos
            }
        )

def parse_despesas(ws):
    """Separa despesas em 3 categorias"""
    premios = []
    pessoais = []
    normais = []

    for row in rows:
        tipo_str = row['TIPO']
        tags = parse_tags(tipo_str)  # "Prémio, Serviço" → ["PREMIO", "SERVICO"]

        if 'PREMIO' in tags or 'COMISSAO_VENDA' in tags:
            premios.append(row)
        elif 'PER_DIEM_PT' in tags or 'PER_DIEM_FORA' in tags or \
             ('DESLOCACAO' in tags and 'PESSOAL' in tags):
            pessoais.append(row)
        else:
            normais.append(row)

    return {'premios': premios, 'pessoais': pessoais, 'normais': normais}
```

---

## 📐 Regras de Negócio

### 1. Saldos Pessoais

**Fórmula:**
```
Saldo = INs - OUTs

INs (empresa DEVE ao sócio):
  • Projetos PESSOAL com estado=PAGO (valor total)
  • Prémios em projetos EMPRESA (campos premio_bruno/rafael)

OUTs (empresa PAGOU ao sócio):
  • Despesas FIXA_MENSAL (Administrativo, Ordenado, Sub.Alimentação) ÷ 2
  • Boletins com estado=PAGO
  • Despesas com tag PESSOAL (identificar sócio pelo credor)
```

**Validação:** ✅ Já implementado em `core/utils/saldos.py`

### 2. Projetos PESSOAL vs EMPRESA

| Tipo | Identificação | Cliente | Impacto Saldos |
|------|---------------|---------|----------------|
| PESSOAL | ESTADO="Pessoal" na sheet | Opcional | Valor total entra nos INs do sócio |
| EMPRESA | ESTADO≠"Pessoal" | Obrigatório | Só prémios entram nos INs |

### 3. Boletins (Ajudas de Custo)

**Origem na Sheet:** Despesas tipo "Deslocação, Pessoal" / "Per Diem, Pessoal"

**Conversão:**
- Agrupar por (Sócio + Mês + Ano)
- Criar Boletim com:
  - `descricao` = nome do mês
  - `data_emissao` = dia 27 do mês
  - `data_pagamento` = DATA_VENCIMENTO (se preenchida)
  - `estado` = PAGO se data_vencimento else PENDENTE
  - `valor_total` = soma dos valores
  - **SEM BoletimLinhas** (histórico simplificado)

**Impacto IRC:**
- ✅ Boletins são gastos dedutíveis
- ⚠️ Tributação Autónoma 5% (se não faturados)
- 📋 Precisam Mapa de Itinerário (feito manualmente)

### 4. Prémios

**Sheet:** Despesas tipo "Prémio, ..." ou "..., Comissão venda"

**Lógica:**
1. Filtrar despesas com tag PREMIO ou COMISSAO_VENDA
2. Agrupar por Projeto + Sócio (identificar pelo credor)
3. Somar valores
4. Popular `projeto.premio_bruno` / `projeto.premio_rafael`
5. **Descartar** as despesas (não importar para tabela Despesas)

**Impacto Saldos:**
- ✅ Entram como INs nos saldos pessoais
- ❌ Pagos via Boletins (entram como OUTs)

### 5. Despesas com Tags Compostas

**Exemplo:** "Equipamento, Pessoal"

**Interpretação:**
- É compra de **Equipamento** → Conta para IRC
- É despesa **Pessoal** do sócio → Desconta do saldo pessoal
- Ambas as tags aplicam!

**Impacto:**
```python
despesa.tags.add(tag_equipamento, tag_pessoal)
# impacta_irc = True (equipamento)
# impacta_saldos = True (pessoal)
```

### 6. IRS Retenção

**Tipo:** Pagamento de retenções na fonte ao Estado

**Características:**
- ❌ **NÃO** entra no cálculo de saldos
- ❌ **NÃO** entra no cálculo de IRC (é pagamento de imposto, não gasto)
- ✅ Sempre associado a Projetos (nunca pessoal)

**Tag:**
```python
{
    "codigo": "IRS_RETENCAO",
    "impacta_saldos": False,
    "impacta_irc": False
}
```

---

## ⚠️ Validações e Edge Cases

### Import de Projetos

**Validações:**
```python
# 1. Cliente não encontrado
if cliente_nome and not Cliente.objects.filter(nome=cliente_nome).exists():
    logger.warning(f"Cliente '{cliente_nome}' não encontrado para projeto {numero}")
    # Criar cliente automático ou skip?

# 2. Sócio não encontrado
if owner_nome not in ['Bruno Amaral', 'Rafael Reigota']:
    logger.error(f"Owner inválido: '{owner_nome}' no projeto {numero}")
    # Usar default BA ou erro?

# 3. Datas inválidas
if data_inicio and data_fim and data_inicio > data_fim:
    logger.warning(f"Data início > Data fim no projeto {numero}")

# 4. Projeto EMPRESA sem cliente
if tipo == TipoProjeto.EMPRESA and not cliente:
    logger.warning(f"Projeto EMPRESA {numero} sem cliente")
```

**Update vs Create:**
```python
# Usar numero como chave única
Projeto.objects.update_or_create(
    numero=numero,
    defaults={...}
)
# Se projeto já existe → update
# Se não existe → create
```

### Import de Despesas

**Parsing de Tags:**
```python
def parse_tags(tipo_str):
    """
    "Prémio, Serviço, Equipamento" → ["PREMIO", "SERVICO", "EQUIPAMENTO"]
    """
    if not tipo_str:
        return []

    # Split por vírgula
    parts = [p.strip() for p in tipo_str.split(',')]

    # Normalizar para códigos
    mapping = {
        'Prémio': 'PREMIO',
        'Serviço': 'SERVICO',
        'Equipamento': 'EQUIPAMENTO',
        'Pessoal': 'PESSOAL',
        'Comissão venda': 'COMISSAO_VENDA',
        'Administrativo': 'ADMINISTRATIVO',
        'Ordenado': 'ORDENADO',
        'Sub. Alimentação': 'SUB_ALIMENTACAO',
        'Alimentação': 'ALIMENTACAO',
        'Produção': 'PRODUCAO',
        'Deslocação': 'DESLOCACAO',
        'Per Diem PT': 'PER_DIEM_PT',
        'Per Diem FORA': 'PER_DIEM_FORA',
        'IRS Retenção': 'IRS_RETENCAO',
    }

    tags = []
    for part in parts:
        if part in mapping:
            tags.append(mapping[part])
        else:
            logger.warning(f"Tag desconhecida: '{part}'")

    return tags
```

**Validação de Tags:**
```python
# Verificar se todas as tags existem
for tag_codigo in tags:
    if not TagDespesa.objects.filter(codigo=tag_codigo).exists():
        logger.error(f"Tag '{tag_codigo}' não existe!")
        # Criar automaticamente ou erro?
```

**Identificar Sócio em Despesas Pessoais:**
```python
def identify_socio_from_credor(credor_nome):
    """
    Identifica sócio pelo nome no campo CREDOR
    """
    if 'Bruno' in credor_nome or 'Amaral' in credor_nome:
        return Socio.objects.get(codigo='BA')
    elif 'Rafael' in credor_nome or 'Reigota' in credor_nome:
        return Socio.objects.get(codigo='RR')
    else:
        logger.warning(f"Não consegui identificar sócio: '{credor_nome}'")
        return None
```

### Conversão Boletins

**Agrupamento:**
```python
# Criar chave única (socio, ano, mes)
chave = (socio.codigo, ano, mes)

# Verificar duplicados
if Boletim.objects.filter(socio=socio, ano=ano, mes=mes).exists():
    logger.warning(f"Boletim já existe: {socio.codigo} {mes}/{ano}")
    # Atualizar valor ou skip?
```

**Validação de Valores:**
```python
# Valores de referência para Boletins futuros (limites de isenção 2025)
VAL_DIA_NACIONAL_GERENTE = 72.65  # €/dia
VAL_DIA_ESTRANGEIRO_GERENTE = 175.42  # €/dia
VAL_KM = 0.40  # €/km

# Para boletins históricos: deixar None
# Para boletins novos (criados manualmente): validar limites
```

### Agregação de Prémios

**Validações:**
```python
# 1. Prémio sem projeto associado
if not despesa.projeto:
    logger.warning(f"Despesa {despesa.numero} é prémio mas não tem projeto")
    # Criar "Prémio Avulso" ou skip?

# 2. Prémio com credor desconhecido
socio = identify_socio_from_credor(despesa.credor)
if not socio:
    logger.error(f"Não consegui identificar sócio para prémio {despesa.numero}")
    # Assumir BA? RR? Erro?

# 3. Múltiplos prémios no mesmo projeto
# Somar valores (esperado)
premios_existentes = Projeto.objects.get(numero='#P0001').premio_bruno
novo_premio = premios_existentes + valor_adicional
```

### Import de Fornecedores

**Classificação (estrelas):**
```python
def parse_classificacao(stars_str):
    """
    "*****" → 5
    "***" → 3
    "" → None
    """
    if not stars_str:
        return None
    return stars_str.count('★') or stars_str.count('*')
```

**NIF/NIPC:**
```python
# Pode vir como número float do Excel
nif = ws.cell(row, col).value
if nif:
    nif = str(int(nif))  # 500399905.0 → "500399905"
```

### Import de Clientes

**Skip Sócios:**
```python
SKIP_CLIENTES = ['#C0001', '#C0002']

if numero in SKIP_CLIENTES:
    logger.info(f"Skipping sócio cliente: {numero}")
    continue
```

**ANGARIAÇÃO:**
```python
# Campo livre, pode ter nome do sócio
angariacao = row['ANGARIAÇÃO']
# "Bruno Amaral", "Rafael Reigota", ou texto livre
# Não criar FK, manter como texto
```

---

## 🎯 Próximos Passos

1. **Criar Migration** com novos campos
2. **Criar Fixtures** de TagDespesa
3. **Implementar Management Command** `import_from_excel`
4. **Testar Import** em ambiente local
5. **Validar Saldos** após import (comparar com sheet)
6. **Ajustar SaldosCalculator** se necessário
7. **Documentar** processo de sync futura (Google Sheets API)

---

## 📚 Referências

- **Ficheiro Original:** `excel/CONTABILIDADE_FINAL_20251231.xlsx`
- **Django Models:** `agora_web/core/models.py`
- **SaldosCalculator:** `agora_web/core/utils/saldos.py`
- **Documentação Saldos:** `docs/SALDOS_DASHBOARD.md`
- **Documentação Sócios:** `docs/SOCIOS_MIGRATION.md`

---

**Última Atualização:** 31 Dezembro 2025
**Autor:** Claude (análise automatizada)
**Status:** ✅ Análise Completa - Pronto para Implementação
