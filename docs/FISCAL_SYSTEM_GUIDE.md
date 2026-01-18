# Sistema de Categorização Fiscal - Guia Completo

**Versão:** 0.3.0
**Data:** 18 Janeiro 2026
**Status:** ✅ Implementado e Testado

---

## ⚠️ PROPÓSITO DESTA APP

### O que esta app É:

✅ **Sistema de contabilidade interna** para os sócios da Agora Media Production
✅ **Ferramenta de reconciliação** com contabilidade organizada externa
✅ **Sistema de saldos pessoais** (quem deve a quem entre sócios)
✅ **Gerador de relatórios** para enviar ao contabilista oficial
✅ **Sistema de boletins itinerários** para per diems e despesas de deslocação

### O que esta app NÃO É:

❌ **NÃO substitui** a contabilidade organizada oficial
❌ **NÃO gera** declarações fiscais oficiais (IRS, IRC, IVA)
❌ **NÃO substitui** software profissional (Primavera, PHC, etc.)
❌ **NÃO é** um sistema de faturação completo

### Workflow Real:

```
1. Sócios → Registam despesas nesta app
2. App → Categoriza e organiza (tags fiscais são pré-categorização)
3. App → Gera relatórios (Excel, PDF, boletins itinerários)
4. Relatórios → Enviados ao contabilista oficial
5. Contabilista → Revê, corrige se necessário, e processa oficialmente
6. Contabilista → Faz declarações fiscais no software profissional
```

**Vantagem:** Reduzir idas e vindas com contabilista ("o que é esta despesa?", "quem pagou isto?", "qual foi o objetivo desta viagem?")

---

## 📋 Visão Geral do Sistema Fiscal

O sistema de categorização fiscal permite **pré-categorizar** automaticamente despesas e templates de acordo com as regras fiscais portuguesas (IRC, IVA, IRS, TSU). Baseado nas respostas detalhadas do contabilista.

### Objetivos

1. **Automatizar** a pré-categorização fiscal de despesas
2. **Reduzir erros** humanos na classificação inicial
3. **Facilitar** comunicação com contabilista (dados já organizados)
4. **Fornecer relatórios** estruturados para reconciliação
5. **Gerar boletins itinerários** automáticos para ajudas de custo

**IMPORTANTE:** As tags fiscais são **sugestões** baseadas em regras conhecidas. O contabilista oficial tem sempre a palavra final e pode ajustar conforme necessário.

---

## 🏗️ Arquitectura

### 1. Modelos de Tags Fiscais

Localização: `agora_web/core/models.py` (linhas 447-628)

#### TagIRC - Dedutibilidade em IRC
- **IRC_DEDUTIVEL_100**: 100% dedutível
- **IRC_DEDUTIVEL_PARCIAL**: Dedutível parcialmente (50% combustíveis, 0.05% representação)
- **IRC_NAO_DEDUTIVEL**: Não dedutível (gasolina)
- **IRC_INVESTIMENTO**: Investimento amortizável (equipamento ≥€500)

#### TagIVA - Dedutibilidade em IVA
- **IVA_DEDUTIVEL_100**: 100% dedutível (equipamento, serviços)
- **IVA_NAO_DEDUTIVEL**: Não dedutível (viaturas, refeições, gasolina)
- **IVA_MISTO**: Uso misto 50% (gasóleo viatura)
- **IVA_ISENTO**: Isento/Sem IVA

#### TagIRS - Retenção na Fonte
- **IRS_ISENTO**: Isento (subsídio alimentação ≤€10,20/dia)
- **IRS_RETENCAO_TRABALHO**: Trabalho dependente (gerentes, trabalhadores)
- **IRS_RETENCAO_25**: Freelancers genéricos (25%)
- **IRS_RETENCAO_11_5**: Profissionais regulados (11.5%)
- **IRS_RETENCAO_16_5**: Advogados (16.5%)

#### TagTSU - Segurança Social
- **TSU_GERENTE**: Gerente (21.4% empresa + 9.3% trabalhador)
- **TSU_TRABALHADOR**: Trabalhador (23.75% empresa + 11% trabalhador)
- **TSU_ISENTO**: Isento (subsídios)
- **TSU_INDEPENDENTE**: Trabalhador independente (não paga empresa)

### 2. Campos nos Modelos

#### DespesaTemplate e Despesa
```python
tag_irc = ForeignKey('TagIRC', null=True, blank=True)
tag_iva = ForeignKey('TagIVA', null=True, blank=True)
tag_irs = ForeignKey('TagIRS', null=True, blank=True)
tag_tsu = ForeignKey('TagTSU', null=True, blank=True)
```

#### Propriedade fiscal_info (só em Despesa)
```python
@property
def fiscal_info(self):
    return {
        'irc_dedutivel': self.tag_irc.percentagem_dedutivel if self.tag_irc else 0,
        'iva_dedutivel': self.tag_iva.percentagem_dedutivel if self.tag_iva else 0,
        'irs_taxa': self.tag_irs.taxa_retencao_default if self.tag_irs else 0,
        'tsu_empresa': self.tag_tsu.taxa_empresa if self.tag_tsu else 0,
        'tsu_trabalhador': self.tag_tsu.taxa_trabalhador if self.tag_tsu else 0,
    }
```

---

## 🤖 Sistema de Auto-Sugestão

### 1. Mapeamento Backend

Localização: `agora_web/core/fiscal_mapping.py`

Contém mapeamento completo de **50+ keywords** para tags fiscais. Exemplos:

| Keyword | IRC | IVA | IRS | TSU |
|---------|-----|-----|-----|-----|
| ordenado gerente | DEDUTIVEL_100 | - | RETENCAO_TRABALHO | TSU_GERENTE |
| subsídio alimentação | DEDUTIVEL_100 | - | ISENTO | ISENTO |
| freelancer | DEDUTIVEL_100 | DEDUTIVEL_100 | RETENCAO_25 | INDEPENDENTE |
| equipamento | INVESTIMENTO | DEDUTIVEL_100 | - | - |
| renting | DEDUTIVEL_100 | DEDUTIVEL_100 | - | - |
| gasolina | NAO_DEDUTIVEL | NAO_DEDUTIVEL | - | - |
| gasóleo | DEDUTIVEL_PARCIAL | MISTO | - | - |

### 2. Interface no Admin

Localização: `agora_web/static/js/admin_custom.js` (linhas 218-395)

#### Funcionalidades

1. **Botão "🤖 Sugerir Tags Fiscais"**
   - Aparece em páginas de edição de Despesas e Despesas Fixas
   - Analisa descrição e sugere tags automaticamente
   - Feedback visual com notificações

2. **Algoritmo de Matching**
   - Procura keywords na descrição (case-insensitive)
   - Preferência por matches mais específicos (keywords longas)
   - Aplica tags automaticamente aos campos

3. **Notificações**
   - ✓ Sucesso: Verde com keyword identificada
   - ⚠ Aviso: Laranja se não houver sugestão

---

## 📊 Admin Interfaces

### TagIRCAdmin, TagIVAAdmin, TagIRSAdmin, TagTSUAdmin

Localização: `agora_web/core/admin.py` (linhas 342-424)

**Funcionalidades:**
- Lista editável com campo `ordem` (drag & drop futuro)
- Busca por código, nome, descrição
- Ordenação por ordem e código
- Fieldsets organizados (Informação Básica + Parâmetros Fiscais)

### DespesaTemplateAdmin / DespesaAdmin

**Novo Fieldset "Categorização Fiscal":**
```python
('Categorização Fiscal', {
    'fields': ('tag_irc', 'tag_iva', 'tag_irs', 'tag_tsu'),
    'description': 'Tags automáticas para cálculo de impostos'
})
```

**Autocomplete:**
```python
autocomplete_fields = ['credor', 'projeto', 'tag_irc', 'tag_iva', 'tag_irs', 'tag_tsu']
```

---

## 🗃️ Base de Dados

### Tabelas Criadas

```sql
-- Tags fiscais
tags_irc (codigo PK, nome, descricao, percentagem_dedutivel, ordem)
tags_iva (codigo PK, nome, descricao, percentagem_dedutivel, ordem)
tags_irs (codigo PK, nome, descricao, taxa_retencao_default, ordem)
tags_tsu (codigo PK, nome, descricao, taxa_empresa, taxa_trabalhador, ordem)

-- Campos adicionados
despesa_templates.tag_irc_id VARCHAR(50) FK → tags_irc
despesa_templates.tag_iva_id VARCHAR(50) FK → tags_iva
despesa_templates.tag_irs_id VARCHAR(50) FK → tags_irs
despesa_templates.tag_tsu_id VARCHAR(50) FK → tags_tsu

despesas.tag_irc_id VARCHAR(50) FK → tags_irc
despesas.tag_iva_id VARCHAR(50) FK → tags_iva
despesas.tag_irs_id VARCHAR(50) FK → tags_irs
despesas.tag_tsu_id VARCHAR(50) FK → tags_tsu

-- Tabelas históricas (django-simple-history)
core_historicaldespesatemplate.tag_*_id
core_historicaldespesa.tag_*_id
```

### Fixtures Carregadas

```bash
# Dados carregados:
tags_irc.json: 4 tags
tags_iva.json: 4 tags
tags_irs.json: 5 tags
tags_tsu.json: 4 tags
Total: 17 objetos
```

---

## 📖 Como Usar

### 1. Criar Despesa com Auto-Sugestão

1. Ir para Admin → Despesas → Adicionar despesa
2. Preencher **Descrição** (ex: "Ordenado gerente - Janeiro 2026")
3. Clicar em **"🤖 Sugerir Tags Fiscais"**
4. Sistema preenche automaticamente:
   - IRC: IRC_DEDUTIVEL_100
   - IRS: IRS_RETENCAO_TRABALHO
   - TSU: TSU_GERENTE
5. Revisar e ajustar se necessário
6. Guardar

### 2. Criar Template de Despesa Fixa

1. Admin → Despesas Fixas Mensais → Adicionar
2. Preencher dados (Número, Descrição, Valores, Dia do Mês)
3. Usar auto-sugestão ou selecionar manualmente tags fiscais
4. Guardar

### 3. Consultar Informação Fiscal

```python
# Em Django shell ou views
despesa = Despesa.objects.get(numero='D-2026-001')

# Ver tags
print(f"IRC: {despesa.tag_irc.nome if despesa.tag_irc else 'N/A'}")
print(f"IVA: {despesa.tag_iva.nome if despesa.tag_iva else 'N/A'}")
print(f"IRS: {despesa.tag_irs.nome if despesa.tag_irs else 'N/A'}")
print(f"TSU: {despesa.tag_tsu.nome if despesa.tag_tsu else 'N/A'}")

# Ver info fiscal calculada
info = despesa.fiscal_info
print(f"IRC dedutível: {info['irc_dedutivel']}%")
print(f"IVA dedutível: {info['iva_dedutivel']}%")
print(f"IRS taxa: {info['irs_taxa']}%")
print(f"TSU empresa: {info['tsu_empresa']}%")
print(f"TSU trabalhador: {info['tsu_trabalhador']}%")
```

---

## 🔍 Regras Fiscais Implementadas

### IRC - Dedutibilidade

| Despesa | Dedutibilidade | Tag |
|---------|---------------|-----|
| Ordenado gerente | 100% | IRC_DEDUTIVEL_100 |
| Subsídio alimentação | 100% | IRC_DEDUTIVEL_100 |
| Prémios | 100% | IRC_DEDUTIVEL_100 |
| Equipamento <€500 | 100% (despesa corrente) | IRC_DEDUTIVEL_100 |
| Equipamento ≥€500 | 25% aa (investimento) | IRC_INVESTIMENTO |
| Renting viatura | 100% | IRC_DEDUTIVEL_100 |
| Combustível gasóleo | 50% (uso misto) | IRC_DEDUTIVEL_PARCIAL |
| Combustível gasolina | 0% | IRC_NAO_DEDUTIVEL |
| Refeições cliente | 0.05% volume negócios | IRC_DEDUTIVEL_PARCIAL |

### IVA - Dedutibilidade

| Despesa | Dedutibilidade | Tag |
|---------|---------------|-----|
| Equipamento | 100% | IVA_DEDUTIVEL_100 |
| Serviços freelancer | 100% | IVA_DEDUTIVEL_100 |
| Renting viatura | 100% | IVA_DEDUTIVEL_100 |
| Viatura compra | 0% | IVA_NAO_DEDUTIVEL |
| Gasolina | 0% | IVA_NAO_DEDUTIVEL |
| Gasóleo | 50% (uso misto) | IVA_MISTO |
| Refeições | 0% | IVA_NAO_DEDUTIVEL |
| Alojamento | 0% | IVA_NAO_DEDUTIVEL |

### IRS - Retenção

| Rendimento | Taxa | Tag |
|-----------|------|-----|
| Ordenado gerente | Tabela AT | IRS_RETENCAO_TRABALHO |
| Subsídio alimentação ≤€10,20 | 0% (isento) | IRS_ISENTO |
| Prémios | Tabela AT | IRS_RETENCAO_TRABALHO |
| Freelancer genérico | 25% | IRS_RETENCAO_25 |
| Profissional regulado | 11.5% | IRS_RETENCAO_11_5 |
| Advogado | 16.5% | IRS_RETENCAO_16_5 |
| Ajudas de custo | 0% (isento) | IRS_ISENTO |

### TSU - Segurança Social

| Tipo | Taxa Empresa | Taxa Trabalhador | Tag |
|------|-------------|-----------------|-----|
| Gerente | 21.4% | 9.3% | TSU_GERENTE |
| Trabalhador | 23.75% | 11% | TSU_TRABALHADOR |
| Freelancer | - | Regime próprio | TSU_INDEPENDENTE |
| Subsídios isentos | - | - | TSU_ISENTO |

---

## 📊 Relatórios para Contabilista

### 1. Boletins Itinerários (IMPLEMENTADO ✅)

**Propósito:** Documentar deslocações e ajudas de custo conforme Lei 106/98

**Funcionalidades:**
- Registo de deslocações com data, origem, destino, objetivo
- Cálculo automático de per diems (€62,75/dia Portugal, varia estrangeiro)
- Ajudas de custo quilométricas (€0,40/km)
- Exportação em PDF para anexar à contabilidade
- Assinatura digital dos sócios

**Como usar:**
1. Admin → Boletins → Adicionar boletim
2. Selecionar sócio e período
3. Adicionar linhas de deslocação (data, local, kms, objetivo)
4. Sistema calcula automaticamente valores isentos de IRS/TSU
5. Exportar PDF → Enviar ao contabilista

**Por que é importante:**
- Autoridade Tributária exige documentação de ajudas de custo
- Sem boletim, ajudas de custo podem ser tributadas como rendimento
- Facilita auditoria (tudo documentado e justificado)

### 2. Relatórios Fiscais (FUTURO)

**Planeados:**
- [ ] Breakdown IRC (dedutível vs não dedutível) → Para preparar IRC anual
- [ ] IVA trimestral (liquidado vs dedutível) → Para Modelo 3
- [ ] IRS mensal (retenções por fornecedor) → Para DMR (Declaração Mensal Remunerações)
- [ ] TSU mensal (base de incidência) → Para Segurança Social
- [ ] Análise anual de dedutibilidade → Para planeamento fiscal

**Formato de Exportação:**
- Excel (.xlsx) - PRIORITÁRIO (contabilista prefere)
- PDF - Para arquivo e apresentação
- CSV - Para integração com outros sistemas

### 2. Validações Automáticas

- [ ] Alertar se valor equipamento ≥€500 sem tag IRC_INVESTIMENTO
- [ ] Validar limite 0.05% volume negócios para representação
- [ ] Verificar consistência fiscal (ex: IVA_DEDUTIVEL sem IRC correspondente)

### 3. Exportação

- [ ] Exportar relatórios em Excel (.xlsx)
- [ ] Exportar em PDF
- [ ] Templates para Modelo 3 IVA
- [ ] Templates para declaração IRC

### 4. Integração

- [ ] API endpoint para sugestões fiscais via AJAX
- [ ] Webhook para notificar contabilista de novas despesas
- [ ] Dashboard fiscal com indicadores

---

## 📚 Referências

- **Respostas do Contabilista**: `docs/RESPOSTAS_CONTABILISTA.md`
- **Código IRC**: Artigos 43º, 44º, 49º
- **Código IVA**: Artigo 61º
- **Lei 106/98**: Ajudas de custo
- **Decreto-Lei 192/2010**: Subsídio de alimentação

---

## 🐛 Troubleshooting

### Auto-sugestão não funciona

1. Verificar se JavaScript está carregado: `view-source` → procurar `admin_custom.js`
2. Verificar console do browser (F12) para erros
3. Confirmar que campo "Descrição" existe na página
4. Testar com keyword conhecida (ex: "ordenado", "freelancer")

### Tags não aparecem no admin

1. Verificar fixtures: `docker compose exec web python manage.py loaddata tags_irc tags_iva tags_irs tags_tsu`
2. Ver se tabelas existem: `docker compose exec web python manage.py dbshell` → `\dt tags_*`
3. Verificar migration aplicada: `docker compose exec web python manage.py showmigrations core`

### Erros de migration

1. Fazer rebuild: `docker compose up -d --build web`
2. Se persistir, contactar desenvolvedor

---

**Documentação criada por:** Claude Code
**Última atualização:** 18 Janeiro 2026
**Versão do sistema:** 0.3.0
