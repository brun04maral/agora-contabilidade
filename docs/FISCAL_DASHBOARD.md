# Dashboard Fiscal - Implementation Guide

**Date:** 18 Janeiro 2026
**Status:** ✅ Complete
**Version:** 0.3.1
**URL:** `/admin/core/fiscal/`

---

## Overview

Dashboard fiscal personalizado no Django Admin para gestão de IVA, IRS e IRC, com páginas dedicadas para cada imposto integradas dentro do admin do Unfold.

**Empresa:** Amaral & Reigota - Produção Audiovisual, Lda (NIPC: 518 351 190)
**Marca:** Agora Media Production

### Features

- ✅ **Landing Page Dashboard:** Vista geral com 3 cards clicáveis (IVA, IRS, IRC)
- ✅ **Páginas Dedicadas Integradas:** IVA, IRS e IRC dentro do admin (com sidebar + header Unfold)
- ✅ **Navegação por Períodos:** Tabs estilo Unfold
  - IVA: Navegação trimestral (Q1/Q2/Q3/Q4)
  - IRS: Navegação mensal (Jan-Dez)
  - IRC: Navegação anual
- ✅ **Breadcrumbs:** Estado Fiscal > [Tipo] > [Período]
- ✅ **Breakdown por Tags Fiscais:** Tabelas detalhadas de dedutibilidade
- ✅ **Exportação Excel:** Relatórios formatados para contabilista
- ✅ **Alertas:** Avisos para despesas sem tags fiscais
- ✅ **Dark Mode Support:** Layout funciona com tema claro e escuro do Unfold
- ✅ **Lazy Loading:** Apenas calcula dados do período selecionado (performance)
- ✅ **Cores Terra:** Identificação visual por imposto (#D4A574, #8B9474, #A89674)

---

## Dashboard Structure

### Landing Page (`/admin/core/fiscal/`)

```
┌────────────────────────────────────────────────────────────┐
│ Estado Fiscal                                              │
│ Gestão de IVA, IRS e IRC                                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│ │ IVA Trimest  │  │ IRS Mensal   │  │ IRC Anual    │    │
│ │ Q1/2025   →  │  │ Jan/2025  →  │  │ 2025      →  │    │
│ │ €12,345.67   │  │ €890.12      │  │ €23,456.78   │    │
│ │ A Pagar ao   │  │ 12 retenções │  │ Estimativa   │    │
│ │ Estado       │  │              │  │              │    │
│ │ #D4A574      │  │ #8B9474      │  │ #A89674      │    │
│ └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Cada card mostra:**
- Tipo de imposto e periodicidade
- Período corrente
- Valor principal (a pagar, retido, estimado)
- Informação contextual
- Cor identificadora (borda lateral + ícone)

**Clique no card:** Abre página dedicada integrada no admin

---

### Página IVA (`/admin/core/fiscal/iva/`)

```
┌────────────────────────────────────────────────────────────┐
│ Breadcrumb: Estado Fiscal > IVA Trimestral > Q1/2025     │
├────────────────────────────────────────────────────────────┤
│ IVA Trimestral                                            │
│ Gestão de IVA por trimestre                               │
├────────────────────────────────────────────────────────────┤
│ Ano: [2024] [2025*] [2026]                               │
├────────────────────────────────────────────────────────────┤
│ Tabs: Q1* | Q2 | Q3 | Q4    (estilo Unfold border-bottom)│
├────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────┐ [Exportar    │
│ │ Resumo Q1/2025                         │  Excel]       │
│ │                                         │               │
│ │ IVA Liquidado    €5,000.00  (verde)   │               │
│ │ IVA Dedutível   -€2,000.00  (vermelho)│               │
│ │ A Pagar          €3,000.00  (vermelho)│               │
│ │ Prazo: 31/03/2025                      │               │
│ └────────────────────────────────────────┘               │
│                                                            │
│ ⚠ 5 despesa(s) sem tag IVA (assumido 100% dedutível)    │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐│
│ │ Breakdown por Categoria Fiscal                        ││
│ │┌─────────────────┬────┬──────────┬──────┬────────────┐││
│ ││Categoria        │Desp│IVA Bruto │% Ded │IVA Dedutív│││
│ │├─────────────────┼────┼──────────┼──────┼────────────┤││
│ ││IVA_DEDUTIVEL_100│ 12 │€1,500.00 │100% ✓│€1,500.00  │││
│ ││IVA_NAO_DEDUTIVEL│  3 │€300.00   │  0% ✗│€0.00      │││
│ ││IVA_MISTO        │  1 │€400.00   │ 50% ⚠│€200.00    │││
│ │└─────────────────┴────┴──────────┴──────┴────────────┘││
│ └────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────┘
```

**Funcionalidades:**
- **Year Navigation:** Chips de ano (2024, 2025*, 2026)
- **Quarter Tabs:** Q1/Q2/Q3/Q4 com border-bottom ativo
- **Resumo:** Cards com valores principais e prazo de pagamento
- **Alerta:** Se existirem despesas sem tag IVA
- **Breakdown Table:** Detalhes por tag fiscal com color coding
- **Exportar Excel:** Botão verde com gradiente

---

### Página IRS (`/admin/core/fiscal/irs/`)

```
┌────────────────────────────────────────────────────────────┐
│ Breadcrumb: Estado Fiscal > IRS Mensal > Janeiro/2025    │
├────────────────────────────────────────────────────────────┤
│ IRS Retido Mensal                                         │
│ Gestão de retenções IRS por mês                          │
├────────────────────────────────────────────────────────────┤
│ Ano: [2024] [2025*] [2026]                               │
├────────────────────────────────────────────────────────────┤
│ Tabs: Jan* | Fev | Mar | Abr | Mai | Jun | ...          │
├────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────┐                 │
│ │ Resumo Janeiro/2025                  │                 │
│ │                                       │                 │
│ │ Total Retido: €890.12                │ (vermelho)      │
│ │ Retenções: 12 despesas               │                 │
│ │ Prazo: 20/02/2025                    │                 │
│ └──────────────────────────────────────┘                 │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐│
│ │ Detalhes das Retenções                                ││
│ │┌─────────────┬──────────┬────────┬────┬────────┬────┐││
│ ││Fornecedor   │Descrição │Val Base│Taxa│IRS Ret │Data│││
│ │├─────────────┼──────────┼────────┼────┼────────┼────┤││
│ ││João Silva   │Freelance │€1000.00│25% │€250.00 │... │││
│ ││Maria Costa  │Design    │€500.00 │25% │€125.00 │... │││
│ │└─────────────┴──────────┴────────┴────┴────────┴────┘││
│ │                                    TOTAL: €890.12     ││
│ └────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────┘
```

**Funcionalidades:**
- **Year Navigation:** Chips de ano
- **Month Tabs:** Jan-Dez com abreviação (Jan, Fev, Mar...)
- **Resumo:** Total retido, número de retenções, prazo
- **Tabela de Retenções:** Lista de despesas com IRS retido
- **Sem Exportação:** IRS é reportado mensalmente via DMR (não precisa exportar)

---

### Página IRC (`/admin/core/fiscal/irc/`)

```
┌────────────────────────────────────────────────────────────┐
│ Breadcrumb: Estado Fiscal > IRC Anual > 2025             │
├────────────────────────────────────────────────────────────┤
│ IRC Anual                                                 │
│ Estimativa de IRC por ano                                 │
├────────────────────────────────────────────────────────────┤
│ Ano: [2024] [2025*] [2026]          (sem tabs, só anos)  │
├────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────┐ [Exportar    │
│ │ Resumo IRC 2025                        │  Excel]       │
│ │                                         │               │
│ │ Receitas Totais  €100,000.00  (verde)  │               │
│ │ Despesas Totais  -€60,000.00  (vermelho)│              │
│ │ Lucro Tributável  €40,000.00  (laranja)│               │
│ │                                         │               │
│ │ IRC 16% (€0-50k)  €6,400.00            │               │
│ │ IRC 20% (>€50k)   €0.00                │               │
│ │ IRC Total         €6,400.00    (#A89674)│              │
│ │                                         │               │
│ │ Prazo Declaração: 31/05/2026           │               │
│ └────────────────────────────────────────┘               │
│                                                            │
│ ⚠ 8 despesa(s) sem tag IRC (assumido 100% dedutível)    │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐│
│ │ Breakdown por Categoria Fiscal                        ││
│ │┌──────────────────┬────┬──────────┬──────┬───────────┐││
│ ││Categoria         │Desp│Valor Brut│% Ded │Val Dedutív│││
│ │├──────────────────┼────┼──────────┼──────┼───────────┤││
│ ││IRC_DEDUTIVEL_100 │ 45 │€50,000.00│100% ✓│€50,000.00 │││
│ ││IRC_DEDUTIVEL_PARC│  5 │€8,000.00 │ 50% ⚠│€4,000.00  │││
│ ││IRC_NAO_DEDUTIVEL │  2 │€2,000.00 │  0% ✗│€0.00      │││
│ ││IRC_INVESTIMENTO  │  1 │€10,000.00│ 25%aa│€2,500.00  │││
│ │└──────────────────┴────┴──────────┴──────┴───────────┘││
│ └────────────────────────────────────────────────────────┘│
│                                                            │
│ Nota: Cálculo simplificado. O TOC fará as correções      │
│ fiscais necessárias (despesas não dedutíveis, benefícios  │
│ fiscais, prejuízos anteriores, etc).                      │
└────────────────────────────────────────────────────────────┘
```

**Funcionalidades:**
- **Year Navigation:** Apenas chips de ano (sem tabs mensais/trimestrais)
- **Resumo Completo:** Receitas, despesas, lucro tributável, IRC calculado
- **Cálculo IRC:** 16% primeiros €50k + 20% excedente
- **Alerta:** Despesas sem tag IRC
- **Breakdown Table:** Detalhes por tag fiscal
- **Nota Importante:** Disclaimer sobre cálculo simplificado
- **Exportar Excel:** Botão para relatório anual

---

## Architecture

### Proxy Model

**File:** `agora_web/core/models.py`

```python
class Fiscal(models.Model):
    """Proxy model para mostrar Dashboard Fiscal no admin"""
    id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False  # Django doesn't create table
        verbose_name = _('Estado Fiscal')
        verbose_name_plural = _('Estado Fiscal')
        db_table = 'fiscal_view'  # Fictitious table
        default_permissions = ()  # No add/change/delete permissions
```

---

### Admin Implementation

**File:** `agora_web/core/admin.py` (linhas 1294-1543)

#### 1. Custom URLs via `get_urls()`

```python
@admin.register(Fiscal)
class FiscalAdmin(ModelAdmin):
    def get_urls(self):
        """Adiciona URLs customizadas para páginas dedicadas"""
        urls = super().get_urls()
        custom_urls = [
            path('iva/', self.admin_site.admin_view(self.iva_view),
                 name='core_fiscal_iva'),
            path('irs/', self.admin_site.admin_view(self.irs_view),
                 name='core_fiscal_irs'),
            path('irc/', self.admin_site.admin_view(self.irc_view),
                 name='core_fiscal_irc'),
        ]
        return custom_urls + urls
```

**Resultado:**
- `/admin/core/fiscal/` → Landing page (`changelist_view`)
- `/admin/core/fiscal/iva/` → Página dedicada IVA
- `/admin/core/fiscal/irs/` → Página dedicada IRS
- `/admin/core/fiscal/irc/` → Página dedicada IRC

**Vantagem:** URLs dentro do admin = sidebar + header Unfold funcionam!

#### 2. View Methods

Cada página dedicada tem sua própria view method:

```python
def iva_view(self, request):
    """Página dedicada IVA com navegação trimestral"""
    calculator = FiscalCalculator()
    hoje = datetime.now().date()

    ano = int(request.GET.get('ano', hoje.year))
    trimestre = int(request.GET.get('trimestre', ((hoje.month - 1) // 3) + 1))

    # ... cálculos ...

    context = {
        **self.admin_site.each_context(request),  # 🔑 Unfold context
        'title': 'IVA Trimestral',
        'ano_atual': ano,
        'trimestre_atual': trimestre,
        'iva': iva,
        'iva_breakdown': iva_breakdown,
    }

    return render(request, 'admin/core/fiscal/iva.html', context)
```

**`self.admin_site.each_context(request)`** fornece:
- Sidebar navigation
- User info
- Site title/header
- Dark mode classes
- Todos os widgets do Unfold

#### 3. Landing Page (`changelist_view`)

```python
def changelist_view(self, request, extra_context=None):
    """Vista personalizada para mostrar dashboard fiscal"""
    calculator = FiscalCalculator()
    hoje = date.today()

    # Calcular dados correntes (lazy)
    mes_atual = hoje.month
    trimestre_atual = (mes_atual - 1) // 3 + 1
    ano_atual = hoje.year

    iva = calculator.calcular_iva_trimestral(ano_atual, trimestre_atual)
    irs = calculator.calcular_irs_mensal(ano_atual, mes_atual)
    irc = calculator.estimar_irc_anual(ano_atual)

    context = {
        **self.admin_site.each_context(request),
        'title': 'Estado Fiscal',
        'ano_atual': ano_atual,
        'mes_atual': mes_atual,
        'trimestre_atual': trimestre_atual,
        'iva': iva,
        'irs': irs,
        'irc': irc,
    }

    return render(request, 'admin/core/fiscal/changelist.html', context)
```

---

### Templates

**Location:** `agora_web/core/templates/admin/core/fiscal/`

#### Files:
1. `changelist.html` - Landing page com 3 cards clicáveis
2. `iva.html` - Página dedicada IVA
3. `irs.html` - Página dedicada IRS
4. `irc.html` - Página dedicada IRC

#### Template Pattern:

```django
{% extends "admin/base_site.html" %}  {# ← Herda do Unfold admin #}
{% load i18n static %}

{% block extrahead %}
<style>
    /* Estilos inline com dark mode support */
    .fiscal-card { ... }
    .dark .fiscal-card { ... }
</style>
{% endblock %}

{% block content %}
<div style="padding: 1.5rem; max-width: 80rem; margin: 0 auto;">
    <!-- Breadcrumbs -->
    <!-- Header -->
    <!-- Navigation (Year chips + Tabs) -->
    <!-- Resumo Cards -->
    <!-- Alerts -->
    <!-- Breakdown Tables -->
</div>
{% endblock %}
```

**Nota:** Usando `{% extends "admin/base_site.html" %}` garante que:
- ✅ Sidebar Unfold aparece
- ✅ Header com user menu aparece
- ✅ Dark mode funciona
- ✅ Navegação entre páginas do admin funciona
- ✅ Permissões do admin aplicam-se

---

### Calculator Logic

**File:** `agora_web/core/utils/fiscal.py`

```python
class FiscalCalculator:
    def calcular_iva_trimestral(self, ano, trimestre):
        """Calcula IVA para um trimestre específico"""
        # Lazy load: só busca dados do trimestre pedido
        inicio_trimestre = date(ano, (trimestre - 1) * 3 + 1, 1)
        fim_trimestre = inicio_trimestre + relativedelta(months=3, days=-1)

        # IVA Liquidado (de projetos)
        projetos = Projeto.objects.filter(
            data_inicio__range=[inicio_trimestre, fim_trimestre]
        )
        iva_liquidado = sum(p.iva or 0 for p in projetos)

        # IVA Dedutível (de despesas com tags)
        despesas = Despesa.objects.filter(
            data__range=[inicio_trimestre, fim_trimestre]
        )
        iva_dedutivel = sum(
            (d.iva or 0) * (d.tag_iva.percentagem_dedutivel / 100)
            if d.tag_iva else (d.iva or 0)  # Sem tag = 100%
            for d in despesas
        )

        return {
            'iva_liquidado': {'total': iva_liquidado},
            'iva_dedutivel': {'total': iva_dedutivel},
            'iva_a_pagar': iva_liquidado - iva_dedutivel,
            'prazo_pagamento': fim_trimestre + timedelta(days=10)
        }

    def breakdown_iva_por_tags(self, ano, trimestre):
        """Retorna breakdown de IVA agrupado por tags fiscais"""
        # ... groupby logic ...
        return {
            'IVA_DEDUTIVEL_100': {
                'nome': 'IVA 100% Dedutível',
                'count': 12,
                'iva_bruto': 1500.00,
                'percentagem': 100,
                'iva_dedutivel': 1500.00
            },
            # ...
        }
```

**Performance:**
- ✅ Lazy loading: apenas busca dados do período selecionado
- ✅ Queries otimizadas com `select_related` e `prefetch_related`
- ✅ Agregação em Python (mais flexível que SQL para lógica fiscal complexa)

---

### Export to Excel

**File:** `agora_web/core/views.py` (linhas 161-388)

```python
@staff_member_required
def export_fiscal_excel(request):
    """
    Export fiscal breakdown data to Excel.
    Generates comprehensive fiscal reports with IVA and IRC breakdowns.
    """
    ano = int(request.GET.get('ano', datetime.now().year))
    trimestre = int(request.GET.get('trimestre', 1))
    report_type = request.GET.get('type', 'iva')  # 'iva' or 'irc'

    calculator = FiscalCalculator()
    wb = Workbook()
    ws = wb.active

    # Define styles
    header_fill = PatternFill(start_color="4F81BD", ...)
    green_font = Font(color="10B981", bold=True)
    red_font = Font(color="EF4444", bold=True)

    if report_type == 'iva':
        # IVA Report
        ws.title = f"IVA_Q{trimestre}_{ano}"
        iva_data = calculator.calcular_iva_trimestral(ano, trimestre)
        breakdown = calculator.breakdown_iva_por_tags(ano, trimestre)

        # Write summary + breakdown table with styling
        # ...

    elif report_type == 'irc':
        # IRC Report
        ws.title = f"IRC_{ano}"
        irc_data = calculator.estimar_irc_anual(ano)
        breakdown = calculator.breakdown_irc_por_tags(ano)

        # Write summary + breakdown table with styling
        # ...

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Fiscal_{report_type.upper()}_Q{trimestre}_{ano}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response
```

**Styled Excel Output:**
- ✅ Headers com cor azul + texto branco
- ✅ Color coding: verde (100%), vermelho (0%), laranja (parcial)
- ✅ Bordas e formatação de valores (€#,##0.00)
- ✅ Auto-ajuste de colunas
- ✅ Alertas destacados (despesas sem tags)

---

## Color Scheme (Cores Terra)

| Imposto | Hex Color | RGB | Uso |
|---------|-----------|-----|-----|
| **IVA** | `#D4A574` | rgb(212, 165, 116) | Borda card, breadcrumb, ícone |
| **IRS** | `#8B9474` | rgb(139, 148, 116) | Borda card, breadcrumb, ícone |
| **IRC** | `#A89674` | rgb(168, 150, 116) | Borda card, breadcrumb, ícone |

**Cores Auxiliares:**
- Verde: `rgb(22, 163, 74)` - Entradas, valores positivos
- Vermelho: `rgb(220, 38, 38)` - Saídas, valores a pagar
- Laranja: `rgb(202, 138, 4)` - Parcialmente dedutível, avisos

**Dark Mode:**
```css
.dark .fiscal-card {
    background-color: rgb(31, 41, 55);
    border-color: rgb(75, 85, 99);
}
.dark .green-text { color: rgb(74, 222, 128); }
.dark .red-text { color: rgb(248, 113, 113); }
```

---

## Navigation Patterns

### 1. Breadcrumbs

Todas as páginas dedicadas têm breadcrumbs:

```html
<div style="margin-bottom: 1rem;">
    <a href="/admin/core/fiscal/" style="color: rgb(107, 114, 128); text-decoration: none; font-size: 0.875rem;">
        ← Estado Fiscal
    </a>
    <span style="color: rgb(107, 114, 128); margin: 0 0.5rem;">/</span>
    <span style="color: #D4A574; font-weight: 600; font-size: 0.875rem;">IVA Trimestral</span>
    <span style="color: rgb(107, 114, 128); margin: 0 0.5rem;">/</span>
    <span style="color: rgb(107, 114, 128); font-size: 0.875rem;">Q{{ trimestre_atual }}/{{ ano_atual }}</span>
</div>
```

### 2. Year Chips

Navegação por ano usando chips clicáveis:

```html
<div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
    <span style="font-size: 0.875rem; font-weight: 600;">Ano:</span>
    {% for ano in anos_disponiveis %}
        <a href="?ano={{ ano }}&trimestre={{ trimestre_atual }}"
           style="padding: 0.375rem 0.75rem; border-radius: 0.375rem;
                  {% if ano == ano_atual %}background-color: rgb(59, 130, 246); color: white;
                  {% else %}background-color: rgb(243, 244, 246); color: rgb(75, 85, 99);{% endif %}">
            {{ ano }}
        </a>
    {% endfor %}
</div>
```

### 3. Unfold-Style Tabs

Tabs horizontais com border-bottom ativo:

```html
<style>
.fiscal-tabs {
    display: flex;
    gap: 0.25rem;
    border-bottom: 2px solid rgb(229, 231, 235);
    margin-bottom: 1.5rem;
}
.fiscal-tab {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    color: rgb(107, 114, 128);
    text-decoration: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
}
.fiscal-tab:hover {
    color: #D4A574;
    border-bottom-color: #D4A574;
}
.fiscal-tab.active {
    color: #D4A574;
    border-bottom-color: #D4A574;
    font-weight: 600;
}
</style>

<div class="fiscal-tabs">
    {% for q in "1234" %}
        <a href="?ano={{ ano_atual }}&trimestre={{ q }}"
           class="fiscal-tab {% if trimestre_atual == q|add:0 %}active{% endif %}">
            Q{{ q }}
        </a>
    {% endfor %}
</div>
```

---

## Responsive Design

### Mobile (max-width: 768px)

```css
@media (max-width: 768px) {
    .fiscal-grid {
        grid-template-columns: 1fr; /* 3 colunas → 1 coluna */
    }
    .fiscal-tabs {
        flex-wrap: wrap; /* Tabs em múltiplas linhas */
    }
}
```

**Landing Page:** Cards empilham verticalmente
**Páginas Dedicadas:** Tabs quebram em múltiplas linhas se necessário

---

## User Flow

### Cenário 1: Consultar IVA Trimestral

1. User → Sidebar → "Estado Fiscal"
2. Landing page → Card "IVA Trimestral" → Clique
3. Página IVA → Mostra Q1/2025 (trimestre corrente)
4. User → Clica tab "Q4" → Ver dados Q4/2025
5. User → Clica ano "2024" → Ver dados Q4/2024
6. User → Clica "Exportar Excel" → Download relatório

### Cenário 2: Verificar Retenções IRS de Dezembro

1. User → Sidebar → "Estado Fiscal"
2. Landing page → Card "IRS Mensal" → Clique
3. Página IRS → Mostra Janeiro/2025 (mês corrente)
4. User → Clica tab "Dez" → Ver retenções de Dezembro
5. Tabela → Lista de fornecedores e valores retidos

### Cenário 3: Estimar IRC Anual

1. User → Sidebar → "Estado Fiscal"
2. Landing page → Card "IRC Anual" → Clique
3. Página IRC → Mostra estimativa 2025
4. Vê breakdown por categoria fiscal
5. Alerta → "8 despesas sem tag IRC"
6. User → Vai corrigir despesas → Volta à página IRC → Dados atualizados

---

## Testing Checklist

### Landing Page
- [ ] Cards clicáveis com hover effect (translateY + shadow)
- [ ] Cores terra corretas (#D4A574, #8B9474, #A89674)
- [ ] Valores correntes mostrados
- [ ] Material Icons `arrow_forward` aparecem
- [ ] Dark mode funciona

### Página IVA
- [ ] Breadcrumbs corretos
- [ ] Year chips funcionam
- [ ] Quarter tabs funcionam
- [ ] Resumo mostra valores corretos
- [ ] Alerta aparece se despesas sem tag
- [ ] Breakdown table com color coding
- [ ] Exportar Excel gera ficheiro

### Página IRS
- [ ] Breadcrumbs corretos
- [ ] Year chips funcionam
- [ ] Month tabs funcionam (Jan-Dez)
- [ ] Resumo mostra total retido
- [ ] Tabela lista retenções corretamente
- [ ] Dark mode funciona

### Página IRC
- [ ] Breadcrumbs corretos
- [ ] Year chips funcionam (sem tabs)
- [ ] Resumo mostra receitas/despesas/IRC
- [ ] Cálculo IRC 16%/20% correto
- [ ] Breakdown table com color coding
- [ ] Nota disclaimer aparece
- [ ] Exportar Excel gera ficheiro

### Geral
- [ ] Sidebar Unfold aparece em todas as páginas
- [ ] Header com user menu aparece
- [ ] Navegação entre páginas funciona
- [ ] Lazy loading (só calcula período pedido)
- [ ] Mobile responsive (cards + tabs)

---

## Performance Considerations

### Lazy Loading ✅

**Problema:** Calcular todos os trimestres de todos os anos = slow

**Solução:** Apenas calcular período selecionado

```python
# ❌ ERRADO - calcula tudo
for ano in anos_disponiveis:
    for trimestre in [1, 2, 3, 4]:
        calcular_iva_trimestral(ano, trimestre)  # 4 anos × 4 Q = 16 queries!

# ✅ CERTO - calcula apenas 1 período
ano = request.GET.get('ano', hoje.year)
trimestre = request.GET.get('trimestre', trimestre_atual)
calcular_iva_trimestral(ano, trimestre)  # 1 query
```

### Query Optimization

```python
# Select related para evitar N+1
despesas = Despesa.objects.filter(
    data__range=[inicio, fim]
).select_related('tag_iva', 'tag_irc', 'tag_irs', 'tag_tsu')

# Aggregation no backend quando possível
from django.db.models import Sum
total_iva = Despesa.objects.filter(
    data__range=[inicio, fim]
).aggregate(Sum('iva'))['iva__sum'] or 0
```

### Caching (Futuro)

```python
from django.core.cache import cache

def calcular_iva_trimestral(self, ano, trimestre):
    cache_key = f'iva_{ano}_q{trimestre}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Calculate...
    result = { ... }

    cache.set(cache_key, result, timeout=3600)  # 1 hour
    return result
```

---

## Future Enhancements

### Planeado (Próximas Versões)

- [ ] **Gráficos:** Evolução temporal de IVA/IRC (Chart.js)
- [ ] **Comparação Períodos:** Q1/2025 vs Q1/2024
- [ ] **Alertas Proativos:** Notificar prazos próximos
- [ ] **Estimativas Futuras:** Projeção de IRC baseado em tendências
- [ ] **Keyboard Shortcuts:** ← → para navegar entre períodos
- [ ] **Filtros Avançados:** Por projeto, fornecedor, tag
- [ ] **Export PDF:** Relatórios formatados para apresentação
- [ ] **API REST:** Endpoints para integração externa

### Não Planeado

- ❌ Substituir contabilista (app é pré-categorização)
- ❌ Gerar declarações fiscais oficiais (Modelo 3, Modelo 22)
- ❌ Integração direta com AT (Autoridade Tributária)

---

## Troubleshooting

### Páginas dedicadas não aparecem no admin

**Sintoma:** Clicar nos cards retorna 404

**Solução:**
```bash
# 1. Verificar que admin.py tem get_urls()
grep -A 10 "def get_urls" agora_web/core/admin.py

# 2. Rebuild container
docker compose up -d --build web

# 3. Verificar logs
docker compose logs -f web
```

### CSS não funciona (sem sidebar/header)

**Sintoma:** Páginas aparecem "nuas" sem frame do Unfold

**Causa:** Templates não herdam de `admin/base_site.html`

**Solução:**
```django
{# ❌ ERRADO #}
{% extends "base.html" %}

{# ✅ CERTO #}
{% extends "admin/base_site.html" %}
```

### Dark mode não funciona

**Sintoma:** Cores ficam estranhas em dark mode

**Solução:** Adicionar classes `.dark` aos estilos CSS

```css
/* Light mode */
.fiscal-card { background-color: white; }

/* Dark mode */
.dark .fiscal-card { background-color: rgb(31, 41, 55); }
```

### Dados incorretos

**Sintoma:** Valores não batem com expectativas

**Diagnóstico:**
```bash
# Django shell
docker compose exec web python manage.py shell

from core.utils.fiscal import FiscalCalculator
from datetime import date

calc = FiscalCalculator()

# Testar IVA
iva = calc.calcular_iva_trimestral(2025, 1)
print(iva)

# Testar IRC
irc = calc.estimar_irc_anual(2025)
print(irc)
```

### Exportação Excel falha

**Sintoma:** Click em "Exportar Excel" retorna erro 500

**Logs:**
```bash
docker compose logs -f web | grep ERROR
```

**Possíveis causas:**
- Biblioteca `openpyxl` não instalada → `pip install openpyxl`
- Dados com `None` values → adicionar defaults no código
- Permissões de escrita → verificar Docker volumes

---

## Deployment Checklist

Antes de fazer push para produção:

- [ ] Rebuild local: `docker compose up -d --build web`
- [ ] Testar todas as páginas (Landing + IVA + IRS + IRC)
- [ ] Testar navegação (anos, trimestres, meses)
- [ ] Testar exportação Excel
- [ ] Verificar dark mode
- [ ] Testar mobile (Chrome DevTools)
- [ ] Verificar logs sem erros: `docker compose logs web`
- [ ] Commit: `git add . && git commit -m "feat: ..."`
- [ ] Push: `git push origin main`
- [ ] Verificar em produção: https://app.agoramediaproduction.pt/admin/core/fiscal/

---

## Related Documentation

- **Sistema Fiscal Geral:** `docs/FISCAL_SYSTEM_GUIDE.md`
- **Categorização Fiscal:** `docs/FISCAL_CATEGORIZATION.md`
- **Respostas do Contabilista:** `docs/RESPOSTAS_CONTABILISTA.md`
- **Saldos Dashboard:** `docs/SALDOS_DASHBOARD.md`
- **Claude Context:** `.claude/claude.md`

---

## Changelog

### v0.3.1 (18 Janeiro 2026)

**✅ Implementado:**
- Dashboard fiscal com landing page + 3 páginas dedicadas
- Integração total no admin Unfold (sidebar + header funcionam)
- Navegação por períodos (tabs estilo Unfold)
- Breadcrumbs em todas as páginas
- Cores terra para identificação visual
- Breakdown por tags fiscais
- Exportação Excel (IVA e IRC)
- Alertas para despesas sem tags
- Dark mode support
- Lazy loading (performance)
- Responsive design (mobile)

**🔧 Mudanças:**
- Views movidas de `core/views.py` para `core/admin.py` (método `get_urls()`)
- URLs alteradas de `/fiscal/*` para `/admin/core/fiscal/*`
- Templates herdam de `admin/base_site.html` (não base custom)

**Ficheiros:**
- `agora_web/core/admin.py` (linhas 1294-1543)
- `agora_web/core/templates/admin/core/fiscal/changelist.html`
- `agora_web/core/templates/admin/core/fiscal/iva.html`
- `agora_web/core/templates/admin/core/fiscal/irs.html`
- `agora_web/core/templates/admin/core/fiscal/irc.html`
- `agora_web/core/views.py` (export_fiscal_excel, linhas 161-388)
- `agora_web/core/utils/fiscal.py` (FiscalCalculator)

---

**Documentação criada por:** Claude Code
**Última atualização:** 18 Janeiro 2026
**Versão do sistema:** 0.3.1
**Status:** ✅ Production Ready
